#!/usr/bin/env python3
"""git 이력에서 개발 로그(devlog.md)를 만든다. 저장소 루트의 git 을 읽는다.

  python3 jekyll/scripts/build_devlog.py
"""

import subprocess
from collections import OrderedDict
from pathlib import Path

SITE = Path(__file__).resolve().parents[1]
SEP = "\x1f"

raw = subprocess.run(
    ["git", "log", "--no-merges", f"--format=%ad{SEP}%h{SEP}%s", "--date=short"],
    cwd=SITE.parent,
    check=True,
    text=True,
    capture_output=True,
    encoding="utf-8",
).stdout

days: "OrderedDict[str, list[tuple[str, str]]]" = OrderedDict()
for line in raw.splitlines():
    date, sha, subject = line.split(SEP, 2)
    days.setdefault(date, []).append((sha, subject))

total = sum(len(v) for v in days.values())
first, last = next(reversed(days)), next(iter(days))
out = [
    "---",
    "title: 개발 로그",
    "nav_order: 5",
    "---",
    "",
    "# 개발 로그",
    "{: .no_toc }",
    "",
    f"git 이력에서 자동으로 만든 기록이다 — 커밋 {total}개 · {len(days)}일 ({first} ~ {last}). 최신순.",
    "",
    "1. TOC",
    "{:toc}",
    "",
    "---",
    "",
]
month = None
for date, commits in days.items():
    if date[:7] != month:
        month = date[:7]
        out += [f"## {month[:4]}년 {int(month[5:])}월", ""]
    out += [f"### {date} · 커밋 {len(commits)}개", ""]
    for sha, subject in commits:
        # 표 문법(|)과 HTML 태그(<)로 읽히지 않게 막는다.
        subject = subject.replace("|", r"\|").replace("<", "&lt;")
        out.append(f"- `{sha}` {subject}")
    out.append("")

(SITE / "devlog.md").write_text("\n".join(out), encoding="utf-8")
print(f"devlog.md — 커밋 {total}개, {len(days)}일")
