# 저장소 레이아웃 & 기술 스택

## 저장소 레이아웃

```
woojeongai/
  main.py                      # FastAPI 앱 · include_router · init_db · lifespan
  requirements.txt             # Python 의존성
  logging_setup.py             # 도메인별 로거 등록
  alembic.ini                  # DB 마이그레이션 설정
  apps/
    friday13th/                # 인증 (signup/login)
    music/                     # 보컬·MR·악기·스피치·비디오
    titanic/                   # James(업로드) / Walter(조회) 레퍼런스
  core/
    matrix/
      keymaker_api.py          # API 키 관리
  alembic/versions/            # 마이그레이션 스크립트
```

- 작업 루트: `woojeongai/apps/<앱명>/`
- `PYTHONPATH`에 `woojeongai/apps` 포함 (`uvicorn main:app`, `python main.py`)
- 로컬: `cd woojeongai` → `python main.py` (포트 8000, reload)

## 기술 스택

| 항목 | 버전 |
|------|------|
| FastAPI | 0.136.1 |
| SQLAlchemy | 2.0 (async) |
| SQLModel | 0.0.38 |
| asyncpg | 0.30.0 |
| Alembic | 1.18.4 |
| pandas | 3.0.3 |
| scikit-learn | 1.8.0 |
| librosa | 0.11.0 |
| moviepy | 2.2.1 |
| google-generativeai | 0.8.6 (Gemini) |
| ollama | 0.6.2 (로컬 LLM 폴백) |
| bcrypt | 4.2.1 |
| pytest + pytest-asyncio | 8.3.5 + 0.24.0 |
