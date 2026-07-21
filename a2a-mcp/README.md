# a2a-mcp

3개 에이전트(온프레미스 EXAONE, 온프레미스 Qwen, AWS 라우터)로 구성된 A2A-over-MCP 포트폴리오 프로젝트.

## 아키텍처

- **온프레미스 우분투 서버** (`friend2`, RTX 3050 8GB VRAM): EXAONE 3.5 2.4B, Qwen2.5 3B를 Ollama로 구동. Neo4j·Redis 동거.
- **AWS** (t4g.micro 또는 Lambda): LLM 없는 오케스트레이터/라우터 에이전트. 온프레미스와 Cloudflare Tunnel/Tailscale 경유 통신.
- 각 에이전트는 MCP 서버로 노출되며, 상대 에이전트를 MCP 클라이언트로 호출한다 (A2A over MCP).
- 그래프 DB는 온프레미스 에이전트만 직접 접근한다. AWS 라우터는 MCP 경유로만 데이터에 접근한다.
- 결과물은 Vercel 프론트엔드로 전달된다 (온프레미스 FastAPI → Vercel fetch).

## 디렉터리 구조

```
a2a-mcp/
├── shared/                  # A2A 메시지 스키마 (pydantic) — 단일 소스
├── agents/
│   ├── exaone/               # 온프레미스 주 추론 에이전트 (EXAONE 3.5 2.4B)
│   ├── qwen/                 # 온프레미스 보조 에이전트 (Qwen2.5 3B)
│   └── aws_router/           # AWS 오케스트레이터 (LLM·GPU·그래프DB 의존성 없음)
└── README.md
```

## 패키지 관리

패키지 관리자는 [uv](https://docs.astral.sh/uv/)를 사용한다. **uv workspace는 사용하지 않는다** — 배포 대상이 물리적으로 분리되어 있으므로(우분표 서버 vs AWS), 각 에이전트 디렉터리가 독립적인 `uv sync` 단위다.

```bash
cd shared && uv sync && cd ..
cd agents/exaone && uv sync && cd ../..
cd agents/qwen && uv sync && cd ../..
cd agents/aws_router && uv sync && cd ../..
```

공통 스키마 import 검증:

```bash
cd agents/exaone && uv run python -c "from a2a_shared.schemas import A2AMessage; print('ok')"
```

`aws_router`에 `ollama`, `neo4j`가 설치되지 않았음을 확인:

```bash
cd agents/aws_router && uv pip list | grep -E "ollama|neo4j" && echo "FAIL: 금지 의존성 발견" || echo "ok"
```

## 제약 사항

- 파이썬 버전은 `>=3.11` 고정. 서버와 AWS 인스턴스 간 버전 일치 확인 필요.
- `a2a-shared`는 editable 로컬 경로 의존성이다. 배포 시 각 서버에 `shared/` 디렉터리가 함께 복사되어야 한다 (git clone 단위가 모노레포 전체이므로 충족됨).
- 버전 상한(`<`)은 지정하지 않는다. 잠금은 `uv.lock`이 담당한다.
- 스키마 변경은 반드시 `shared/`에서만 한다. 에이전트 개별 디렉터리에 스키마를 복제하지 않는다.
