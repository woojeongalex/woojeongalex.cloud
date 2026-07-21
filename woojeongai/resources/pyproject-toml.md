# 🛰️ Harness Context: Hybrid Cloud Multi-Agent Hub Setup

## 1. System Architecture Overview & Constraints

You are tasking as a senior backend engineer to validate, output, and implement the project configuration for a hybrid cloud multi-agent system. The infrastructure relies on the following structural constraints:

- **Topology**: Star Topology Ontology (Core hub coordinates peripheral spokes).
- **Architecture**: Clean Architecture (Strict layer separation between Domain, Use Case, and Infrastructure).
- **Hardware Boundary**: On-Premise Ubuntu Server (`friend2`) running **RTX 3050 (8GB VRAM)**.
- **Local Models**: EXAONE 3.0 2.4B & Qwen 2.5 3B served via Ollama (4-bit quantized).
- **Databases**: Neo4j Graph DB & Redis running locally inside Docker containers.
- **Harness Pattern**: Strict payload validation using Pydantic to ensure input safety before LLM routing.

> **PC 사양 검증**: `nvidia-smi` 확인 결과 실제 GPU는 RTX 3050 **8192 MiB (8GB)** — 위 하드웨어 경계 스펙과 일치. 별도 수정 없이 그대로 적용.

---

## 2. Target File: `pyproject.toml` Specification

Generate a robust, standardized `pyproject.toml` configuration utilizing **Poetry** as the dependency manager and build backend. The specification must explicitly lock the runtime libraries required to operate the multi-agent orchestration, graph communication, and validation harness.

### Strict Requirements:

1. **Python Compatibility**: Constrain to Python `^3.11`.
2. **Production Dependencies**:
   - `fastapi` & `uvicorn` for the entry point REST API.
   - `requests` for local Ollama orchestration.
   - `neo4j` for the shared memory Graph database connection.
   - `pydantic` for the harness validation schema.
3. **Development Dependencies**:
   - `ruff` to enforce Clean Architecture coding standards and linting rules.

---

## 3. Implementation Code Block (pyproject.toml)

```toml
[tool.poetry]
name = "hybrid-cloud-mcp-hub"
version = "0.1.0"
description = "AWS-OnPrem 하이브리드 클라우드 기반 MCP 및 Graph DB 에이전트 오케스트레이션 시스템"
authors = ["woojeongalex <dnwjdwkd11@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.110.0"       # AWS/Vercel 요청을 수신할 REST API 엔드포인트용
uvicorn = "^0.28.0"        # FastAPI 서버를 구동할 ASGI 웹 서버
requests = "^2.31.0"       # 로컬 Ollama (EXAONE, Qwen) HTTP 통신용
neo4j = "^5.18.0"          # MCP 컨텍스트 공유 메모리(그래프 DB) 연동용
pydantic = "^2.6.4"        # AWS 수신 데이터 유효성 검증 가드레일(Harness)

[tool.poetry.group.dev.dependencies]
ruff = "^0.3.2"            # 클린 아키텍처 코드 스타일 및 린팅 규칙 강제 도구

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

---

## 4. 참고 — 실제 구현체 (uv 기반)

위 스펙을 기반으로 확장된 A2A-over-MCP 멀티 에이전트 구현은 패키지 관리자를 **uv**로 바꿔 모노레포 루트의 `a2a-mcp/`에 구축되어 있다 (온프레미스 `exaone`/`qwen` 에이전트 + LLM 없는 `aws_router` 에이전트 + 공유 스키마 `shared/`). 상세 구조와 실행 방법은 [[a2a-mcp/README|a2a-mcp/README.md]] 참고.
