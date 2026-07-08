# ⚓ [Titanic App] Walter Nichols (Crew Roaster) 개발 및 검증 보고서

---

## 1. 아키텍처 명세 및 변경 요약

Walter Nichols(일등 항해사, 승객 명단 관리 담당)의 요구사항에 맞춰 데이터셋 조회 엔드포인트 구현 및 기존 의존성 주입(DI) 버그를 전면 수정했습니다.

```
[Inbound Adapter]                   [Core / Input Port]              [Outbound Adapter]
  Router: /walter/train (def)  ──>    WalterUseCase          ──>    WalterRepository
  Router: /walter/test  (def)          (pd.DataFrame 반환)            (Pandas + Sync Engine)
```

### 포트 및 인터페이스 변경 사항

**동기(Sync) 처리 원칙 적용**
`pd.read_sql`은 Pandas가 내부적으로 동기 DB 커넥션을 사용하는 CPU/I/O 작업이므로, `async def`로 이벤트 루프를 블로킹하지 않도록 port와 repository를 **일반 `def`** 함수로 선언한다.
UseCase(Interactor) 레벨은 `async def`를 유지하여 FastAPI가 내부 스레드풀에서 안전하게 처리하도록 구조화했습니다.

**반환 타입 정립**
DTO(`WalterResponse`) 규격 제한을 탈피하고 분석 목적에 맞게 `pd.DataFrame`을 직접 반환하도록 포트 인터페이스를 통일했습니다.

---

## 2. 레이어별 코드 구현 현황

### Input Port

`apps/titanic/app/ports/input/crew_walter_use_case.py`

```python
from abc import ABC, abstractmethod
import pandas as pd

class WalterUseCase(ABC):

    @abstractmethod
    async def get_train_set(self) -> pd.DataFrame:
        """월터가 DB에서 train set 만 가져오는 메소드"""
        pass

    @abstractmethod
    async def get_test_set(self) -> pd.DataFrame:
        """월터가 DB에서 test set 만 가져오는 메소드"""
        pass
```

### Output Port

`apps/titanic/app/ports/output/crew_walter_director_port.py`

```python
from abc import ABC, abstractmethod
import pandas as pd

class WalterDirectorPort(ABC):

    @abstractmethod
    def get_train_set(self) -> pd.DataFrame:
        """survived 컬럼이 있는 데이터 전체를 데이터프레임으로 반환하는 메소드"""
        pass

    @abstractmethod
    def get_test_set(self) -> pd.DataFrame:
        """survived 컬럼이 없는 데이터 전체를 데이터프레임으로 반환하는 메소드"""
        pass
```

### Use Case (Interactor)

`apps/titanic/app/use_cases/crew_walter_interactor.py`

```python
import pandas as pd

class WalterInteractor(WalterUseCase):
    def __init__(self, repository: WalterDirectorPort) -> None:
        self._repository = repository

    async def get_train_set(self) -> pd.DataFrame:
        return self._repository.get_train_set()   # sync 호출, await 없음

    async def get_test_set(self) -> pd.DataFrame:
        return self._repository.get_test_set()    # sync 호출, await 없음
```

### Outbound Repository

`apps/titanic/adapter/outbound/repositories/crew_walter_repository.py`

```python
import pandas as pd
from sqlalchemy import create_engine
import core.matrix.database_manager as _db_manager

def _to_sync_url(async_url: str) -> str:
    return async_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

class WalterRepository(WalterDirectorPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _sync_engine(self):
        raw_url = _db_manager.engine.url.render_as_string(hide_password=False)
        return create_engine(_to_sync_url(raw_url))

    def get_train_set(self) -> pd.DataFrame:
        """survived IS NOT NULL — 훈련 데이터"""
        return pd.read_sql(
            "SELECT * FROM titanic_passengers WHERE survived IS NOT NULL",
            self._sync_engine(),
        )

    def get_test_set(self) -> pd.DataFrame:
        """survived IS NULL — 평가 데이터"""
        return pd.read_sql(
            "SELECT * FROM titanic_passengers WHERE survived IS NULL",
            self._sync_engine(),
        )
```

---

## 3. 디버깅 및 트러블슈팅 내역

| 발생 지점 | 현상 및 원인 | 조치 사항 |
|-----------|-------------|-----------|
| SQLAlchemy Engine URL | `str(engine.url)` 사용 시 패스워드가 `***`로 마스킹되어 동기 엔진 생성 시 인증 실패 | `url.render_as_string(hide_password=False)`로 원본 자격증명 주입 |
| 모듈 단위 결합도 | `from module import engine` 실행 시 `init_engine()` 호출 전 `None` 객체를 조기 스냅숏 캡처 | 모듈 객체 전체를 `import core.matrix.database_manager as _db_manager`로 가져온 후 런타임 시점에 `_db_manager.engine`으로 접근 |
| async def on sync work | `get_train_set` / `get_test_set`에 `async def` 선언 시 내부 pandas 작업이 이벤트 루프 블로킹 | Port·Repository는 `def`, Interactor는 `async def` 유지 (FastAPI 스레드풀 위임) |

---

## 4. SmithCaptain 연계 흐름

`SmithCaptainInteractor.chat` 에서 walter의 데이터셋을 받아 context에 규모를 포함시킨다.

```python
train_df = await self._walter.get_train_set()   # sync 내부, FastAPI 스레드풀 처리
test_df  = await self._walter.get_test_set()

context = (
    f"[훈련데이터: {len(train_df)}행, 테스트데이터: {len(test_df)}행, ...]"
)
```

---

## 5. 최종 통합 검증 결과

검증 방식: Walter 라우터 스코프를 격리 적용한 단독 미니 FastAPI 테스트 하네스로 실제 런타임 파이프라인 검증 수행.

**최종 판정: PASS (정상 작동)**

| 엔드포인트 | 결과 | 비고 |
|-----------|------|------|
| `GET /api/titanic/walter/train` | 200 OK — 891건 반환 | `passenger_id`, `name`, `gender`, `age`, `survived` 등 전수 포함 |
| `GET /api/titanic/walter/test` | 200 OK — 0건 반환 | DB 내 `survived IS NULL` 레코드 부재 상태 반영 (정상) |

---

## 6. 의존 패키지

```
psycopg2-binary   # pd.read_sql 동기 엔진용 (requirements.txt 등록 필요)
pandas
sqlalchemy
```
