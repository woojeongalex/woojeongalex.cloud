#!/usr/bin/env python3
"""Suno 곡 한 곡을 노래방 챌린지로 준비한다 — 명령 한 번.

  완성곡(WAV/MP3) + 가사 텍스트
    → Demucs 로 보컬/반주 분리
    → 챌린지 등록(또는 기존 챌린지 재사용) · 가사 저장
    → 스템 업로드 → 서버가 정답 멜로디 추출
    → Whisper 두 번(medium · small)으로 가사 줄 타이밍 인식
    → 곡 전체 흐름으로 두 결과를 합쳐 저장
    → 점검 보고(음표 품질 · 확인이 필요한 가사 줄)

WSL/리눅스에서 실행한다(파이썬 표준 라이브러리 + Docker 만 필요).
자세한 사용법과 판단 근거는 woojeongai/_docs/song-prep-pipeline.md.

예)
  export SONG_PREP_PASSWORD=...   # 관리자 비밀번호 — 코드·기록에 남기지 않는다
  python3 prepare_song.py song.wav lyrics.txt --title "Still Here In The Dark"
  python3 prepare_song.py song.wav lyrics.txt --title "가로등 아래" --language ko
  python3 prepare_song.py song.wav lyrics.txt --challenge-id 6        # 이미 등록한 곡
  python3 prepare_song.py song.wav lyrics.txt --title X --vocals v.wav --backing b.wav  # Suno 스템이 있으면 분리 생략
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEMUCS_IMAGE = "song-prep-demucs"
WHISPER_IMAGE = "song-prep-whisper"

# WSL 기본 메모리는 PC 램의 절반(16GB PC 면 8GB)이고 백엔드·DB 도 같은 가상머신에서 돈다.
# 한도 없이 돌렸다가 WSL 전체가 멈춘 적이 있다. 모델마다 상한을 건다.
LIMITS = {
    "demucs": ("5g", "6"),
    "whisper-medium": ("4g", "6"),
    "whisper-small": ("3g", "6"),
}
MODELS = {"en": ("medium.en", "small.en"), "ko": ("medium", "small")}

# Suno 가사의 구간 표시 줄 — alexview/lib/lyrics.ts 의 parseLyricsText 와 같은 규칙
SECTION_TAG = re.compile(r"^\[[^\]]*\]$")


# ── 준비 ────────────────────────────────────────────────────────────


def log(msg: str) -> None:
    print(f"[song-prep] {msg}", flush=True)


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def ensure_image(name: str, dockerfile: str) -> None:
    if run(["docker", "image", "inspect", name], check=False).returncode == 0:
        return
    log(f"도커 이미지 {name} 을 처음 만듭니다 (몇 분 걸립니다)")
    subprocess.run(
        ["docker", "build", "-t", name, "-f", str(HERE / "docker" / dockerfile), str(HERE)],
        check=True,
    )


def parse_lyrics(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not SECTION_TAG.match(line.strip())
    ]


def slug(title: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower()
    return s or uuid.uuid4().hex[:8]


# ── API ─────────────────────────────────────────────────────────────


class Api:
    def __init__(self, base: str, username: str, password: str) -> None:
        self.base = base.rstrip("/")
        body = json.dumps({"username": username, "password": password}).encode()
        data = self._request("POST", "/api/auth/login", body, {"Content-Type": "application/json"}, auth=False)
        self.token = data["access_token"]

    def _request(self, method: str, path: str, body: bytes | None, headers: dict, auth: bool = True) -> dict:
        req = urllib.request.Request(self.base + path, data=body, method=method, headers=headers)
        if auth:
            req.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(req, timeout=300) as res:
                return json.loads(res.read() or b"{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:300]
            sys.exit(f"API {method} {path} 실패 ({e.code}): {detail}")

    def _multipart(self, method: str, path: str, fields: dict[str, str], files: dict[str, Path]) -> dict:
        # 한글 제목·설명이 깨지지 않게 UTF-8 로 직접 만든다(명령줄 인자로 보내면 깨졌다).
        boundary = uuid.uuid4().hex
        parts: list[bytes] = []
        for k, v in fields.items():
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        for k, p in files.items():
            parts.append(
                f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"; filename="{p.name}"\r\n'
                f"Content-Type: audio/wav\r\n\r\n".encode()
                + p.read_bytes()
                + b"\r\n"
            )
        parts.append(f"--{boundary}--\r\n".encode())
        return self._request(method, path, b"".join(parts), {"Content-Type": f"multipart/form-data; boundary={boundary}"})

    def create_challenge(self, title: str, description: str, music: Path) -> int:
        data = self._multipart(
            "POST", "/music_challenge/challenges",
            {"title": title, "description": description, "challenge_type": "vocal"},
            {"music_file": music},
        )
        return int(data["id"])

    def put_lyrics(self, cid: int, lines: list[dict]) -> None:
        body = json.dumps({"lines": lines}, ensure_ascii=False).encode()
        self._request("PUT", f"/music_challenge/challenges/{cid}/lyrics", body, {"Content-Type": "application/json"})

    def upload_stems(self, cid: int, vocals: Path, backing: Path) -> None:
        self._multipart(
            "POST", f"/music_challenge/challenges/{cid}/stems",
            {"melody_source": "vocal"},
            {"melody_file": vocals, "backing_file": backing},
        )

    def chart(self, cid: int) -> dict:
        return self._request("GET", f"/music_challenge/challenges/{cid}/chart", None, {})

    def wait_chart(self, cid: int, timeout: float = 600) -> dict:
        start = time.time()
        while time.time() - start < timeout:
            c = self.chart(cid)
            if c.get("status") in ("ready", "failed"):
                return c
            time.sleep(3)
        sys.exit("정답 멜로디 추출이 10분 안에 끝나지 않았습니다. 백엔드 로그를 확인해 주세요.")


# ── 단계 ────────────────────────────────────────────────────────────


def docker_run(kind: str, work: Path, image: str, args: list[str], env: dict[str, str] | None = None) -> int:
    mem, cpus = LIMITS[kind]
    # 모델 캐시(약 2GB)는 곡마다가 아니라 한곳에 둔다. 곡마다 두면 매번 다시 받는다.
    cache = work.parent / ".cache"
    cache.mkdir(parents=True, exist_ok=True)
    cmd = ["docker", "run", "--rm", f"--memory={mem}", f"--cpus={cpus}", "-v", f"{work}:/data", "-v", f"{cache}:/cache"]
    for k, v in (env or {}).items():
        cmd += ["-e", f"{k}={v}"]
    cmd += [image, *args]
    return subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True).returncode


def separate(work: Path, song: Path) -> tuple[Path, Path]:
    out = work / "out" / "htdemucs" / "song"
    if (out / "vocals.wav").exists():
        log("보컬 분리 결과가 이미 있어 건너뜁니다")
    else:
        log("보컬 / 반주 분리 중 (CPU, 4분 곡 약 3분)")
        t = time.time()
        rc = docker_run("demucs", work, DEMUCS_IMAGE,
                        ["--two-stems", "vocals", "-n", "htdemucs", "-o", "/data/out", f"/data/{song.name}"],
                        {"TORCH_HOME": "/cache/torch"})
        if rc != 0:
            sys.exit(f"Demucs 실패 (exit {rc})")
        log(f"  분리 완료 {time.time() - t:.0f}초")
    return out / "vocals.wav", out / "no_vocals.wav"


def align(work: Path, language: str) -> Path:
    """스크립트는 이미지에 굽지 않고 작업 폴더 사본(/data)을 쓴다 — 고쳐도 이미지를 다시 만들 필요가 없다."""
    medium, small = MODELS[language]
    runs = [("medium", medium, "whisper-medium", "song_timed_medium"), ("small", small, "whisper-small", "song_timed")]
    done = []
    for label, model, kind, name in runs:
        log(f"가사 타이밍 인식 — {model}")
        t = time.time()
        rc = docker_run(kind, work, WHISPER_IMAGE,
                        ["/data/align_lyrics.py", "/data/vocals.wav", "/data/lyrics.json", f"/data/{name}.json",
                         model, "novad", language],
                        {"HF_HOME": "/cache/hf", "OMP_NUM_THREADS": LIMITS[kind][1]})
        if rc == 137:
            log(f"  {model} 이 메모리 한도에 걸려 종료됐습니다 — 나머지 결과로 계속합니다")
        elif rc != 0:
            log(f"  {model} 실패 (exit {rc}) — 나머지 결과로 계속합니다")
        else:
            log(f"  완료 {time.time() - t:.0f}초")
            done.append(label)
    if not done:
        sys.exit("두 인식 모두 실패했습니다.")
    if done == ["medium", "small"]:
        rc = subprocess.run(
            ["docker", "run", "--rm", "-v", f"{work}:/data", WHISPER_IMAGE, "/data/combine_alignments.py", "song"],
            text=True,
        ).returncode
        if rc != 0:
            sys.exit("두 결과를 합치지 못했습니다.")
        return work / "song_timed_final.json"
    log("  인식 결과가 하나뿐이라 교차 확인 없이 씁니다")
    return work / ("song_timed_medium.json" if done == ["medium"] else "song_timed.json")


def report(chart: dict, final_status: Path | None) -> None:
    notes = chart["notes"]
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    nm = lambda m: f"{names[m % 12]}{m // 12 - 1}"  # noqa: E731
    durs = [n["end"] - n["start"] for n in notes]
    midis = sorted(n["midi"] for n in notes)
    p5, p95 = midis[len(midis) // 20], midis[len(midis) * 19 // 20]
    short = sum(d < 0.15 for d in durs)
    jumps = sum(1 for a, b in zip(notes, notes[1:]) if abs(a["midi"] - b["midi"]) >= 12 and b["start"] - a["end"] < 0.3)
    log("── 점검 보고 ──")
    log(f"정답 음표 {len(notes)}개 · 곡 {chart['duration']:.0f}초 · 첫 음 {notes[0]['start']:.1f}s · 끝 음 {notes[-1]['end']:.1f}s")
    log(f"주 음역 {nm(p5)} ~ {nm(p95)} · 0.15초 미만 조각 {100 * short / len(notes):.0f}% · 옥타브 튐 {jumps}곳")
    if notes[-1]["end"] < chart["duration"] - 20:
        log("  끝부분 20초 넘게 음표가 없습니다 — 연주로 끝나는 곡인지 들어 보세요")
    if final_status and final_status.exists():
        status = json.loads(final_status.read_text(encoding="utf-8"))
        lines = chart["lyric_lines"]
        check = [(i, s) for i, s in enumerate(status) if s.startswith("골라냄") or s == "추정"]
        log(f"가사 {len(lines)}줄 · 두 인식이 일치 {status.count('확정')}줄 · 확인 권장 {len(check)}줄")
        for i, s in check:
            log(f"  {i + 1:3d}번 {lines[i]['start']:7.2f}s [{s}] {lines[i]['text']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("song", type=Path, help="완성곡 WAV/MP3")
    ap.add_argument("lyrics", type=Path, help="가사 텍스트 (Suno 에서 복사한 그대로)")
    ap.add_argument("--title", help="새 챌린지 제목 (--challenge-id 가 없으면 필수)")
    ap.add_argument("--description", default="Suno로 만든 곡입니다.")
    ap.add_argument("--challenge-id", type=int, help="이미 등록한 챌린지에 붙일 때")
    ap.add_argument("--language", choices=["en", "ko"], default="en")
    ap.add_argument("--vocals", type=Path, help="Suno 보컬 스템 (주면 분리를 건너뜀)")
    ap.add_argument("--backing", type=Path, help="Suno 반주 스템 (--vocals 와 함께)")
    ap.add_argument("--api", default=os.environ.get("SONG_PREP_API", "http://localhost:8000"))
    ap.add_argument("--username", default=os.environ.get("SONG_PREP_USERNAME", "testuser1"))
    ap.add_argument("--workdir", type=Path, default=Path.home() / ".cache" / "song_prep")
    a = ap.parse_args()

    if not a.challenge_id and not a.title:
        ap.error("--title 또는 --challenge-id 중 하나가 필요합니다")
    if bool(a.vocals) != bool(a.backing):
        ap.error("--vocals 와 --backing 은 함께 주세요")
    lines = parse_lyrics(a.lyrics.read_text(encoding="utf-8"))
    if not lines:
        ap.error("가사에서 부를 줄을 찾지 못했습니다")

    password = os.environ.get("SONG_PREP_PASSWORD") or getpass.getpass(f"{a.username} 비밀번호: ")
    api = Api(a.api, a.username, password)

    work = a.workdir / slug(a.title or f"challenge-{a.challenge_id}")
    work.mkdir(parents=True, exist_ok=True)
    # 확장자는 그대로 둔다(MP3 를 .wav 이름으로 두면 헷갈린다). 분리 결과 폴더 이름이 "song" 이 된다.
    song = work / f"song{a.song.suffix.lower()}"
    shutil.copy(a.song, song)
    # 컨테이너 안에서 스크립트를 쓰도록 작업 폴더에 둔다.
    for f in ("align_lyrics.py", "combine_alignments.py"):
        shutil.copy(HERE / f, work / f)
    (work / "lyrics.json").write_text(
        json.dumps({"lines": [{"text": t, "start": None} for t in lines]}, ensure_ascii=False), encoding="utf-8"
    )
    log(f"작업 폴더 {work} · 가사 {len(lines)}줄")

    ensure_image(WHISPER_IMAGE, "whisper.Dockerfile")
    if a.vocals:
        vocals, backing = a.vocals, a.backing
    else:
        ensure_image(DEMUCS_IMAGE, "demucs.Dockerfile")
        vocals, backing = separate(work, song)
    shutil.copy(vocals, work / "vocals.wav")

    cid = a.challenge_id or api.create_challenge(a.title, a.description, song)
    log(f"챌린지 #{cid}")
    api.put_lyrics(cid, [{"text": t, "start": None} for t in lines])
    log("스템 업로드 → 정답 멜로디 추출 중")
    api.upload_stems(cid, vocals, backing)
    chart = api.wait_chart(cid)
    if chart["status"] == "failed":
        sys.exit(f"정답 멜로디 추출 실패: {chart.get('error')}")

    timed = align(work, a.language)
    api.put_lyrics(cid, json.loads(timed.read_text(encoding="utf-8"))["lines"])
    report(api.chart(cid), work / "song_timed_final_status.json" if timed.name == "song_timed_final.json" else None)
    log(f"완료 — 스튜디오: /music-challenge/{cid}/studio · 도전: /music-challenge/{cid}/play")


if __name__ == "__main__":
    main()
