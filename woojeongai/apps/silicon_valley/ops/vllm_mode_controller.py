#!/usr/bin/env python3
"""vLLM chat/embed 모드 전환 컨트롤러 — 로컬 개발용 수동 보조 도구.

**요청 처리 경로(core/matrix/local_llm_client.py, silicon_valley 인터랙터)와는
무관하다.** 정석적인 배포에서는 생성용·임베딩용 vLLM 인스턴스가 각자 독립된
엔드포인트로 항상 함께 떠 있어야 하고, 그러면 이 스크립트는 필요 없다.

8GB급 GPU 한 장뿐인 이 개발 데스크탑에서는 두 인스턴스를 동시에 못 띄우므로,
개발자가 수동으로 `curl -X POST localhost:8003/switch/embed`(또는 `/chat`)를
호출해 모드를 바꿔가며 개별적으로 테스트할 때만 쓴다. 자동으로 요청마다
전환하는 구조는 Cloudflare Tunnel의 ~100초 요청 제한에 걸려 실사용이
불가능하다는 것이 확인됨 (2026-07-15) — 그래서 요청 경로에서 제거했다.

실행: python3 vllm_mode_controller.py  (포트 8003)
"""

import http.server
import json
import os
import signal
import socketserver
import subprocess
import time
import urllib.error
import urllib.request

HOME = os.path.expanduser("~")
VLLM_BIN = f"{HOME}/.venvs/exaone/bin/vllm"
MODEL_PATH = f"{HOME}/models/EXAONE-3.5-7.8B-Instruct-AWQ"
MODEL_NAME = "EXAONE-3.5-7.8B-Instruct-AWQ"
MODEL_PORT = 8001
CONTROLLER_PORT = 8003
LOG_PATH = f"{HOME}/vllm_serve.log"

_BASE_CMD = [
    VLLM_BIN,
    "serve",
    MODEL_PATH,
    "--port",
    str(MODEL_PORT),
    "--gpu-memory-utilization",
    "0.85",
    "--max-model-len",
    "2048",
    "--served-model-name",
    MODEL_NAME,
    "--trust-remote-code",
]
CHAT_CMD = _BASE_CMD
EMBED_CMD = _BASE_CMD + ["--runner", "pooling", "--convert", "embed"]

_STATE: dict[str, str] = {"mode": "unknown"}


def _find_vllm_pids() -> list[int]:
    out = subprocess.run(
        ["pgrep", "-f", "vllm serve"], capture_output=True, text=True
    ).stdout
    return [int(p) for p in out.split() if p]


def _kill_vllm() -> None:
    for pid in _find_vllm_pids():
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    for _ in range(30):
        if not _find_vllm_pids():
            return
        time.sleep(1)


def _wait_healthy(timeout: int = 180) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(
                f"http://localhost:{MODEL_PORT}/health", timeout=3
            ) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionError, TimeoutError, OSError):
            pass
        time.sleep(2)
    return False


def switch_to(mode: str) -> bool:
    if _STATE.get("mode") == mode and _find_vllm_pids() and _wait_healthy(timeout=5):
        return True

    _kill_vllm()
    env = os.environ.copy()
    cmd = CHAT_CMD
    if mode == "chat":
        env["VLLM_USE_FLASHINFER_SAMPLER"] = "0"
    else:
        cmd = EMBED_CMD

    with open(LOG_PATH, "ab") as logf:
        subprocess.Popen(cmd, stdout=logf, stderr=logf, env=env, start_new_session=True)

    ok = _wait_healthy()
    if ok:
        _STATE["mode"] = mode
    else:
        _STATE["mode"] = "unknown"
    return ok


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/status":
            self._send(200, {"mode": _STATE.get("mode", "unknown")})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path == "/switch/chat":
            ok = switch_to("chat")
            self._send(200 if ok else 503, {"ok": ok, "mode": "chat"})
        elif self.path == "/switch/embed":
            ok = switch_to("embed")
            self._send(200 if ok else 503, {"ok": ok, "mode": "embed"})
        else:
            self._send(404, {"error": "not found"})

    def log_message(self, format: str, *args) -> None:  # noqa: A002
        pass


if __name__ == "__main__":
    if _find_vllm_pids() and _wait_healthy(timeout=5):
        _STATE["mode"] = "chat"
    with socketserver.ThreadingTCPServer(
        ("0.0.0.0", CONTROLLER_PORT), Handler
    ) as httpd:
        print(f"vLLM mode controller listening on :{CONTROLLER_PORT}")
        httpd.serve_forever()
