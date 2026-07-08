# Friday13th 헥사고날 단계별 가이드 (STEP BY STEP)

## 1) 작업 시작 전 필수 체크리스트

- [ ] 터미널에 `uvicorn main:app --reload`가 정상 작동 중인지 확인합니다.
- [ ] 라우터 파일(`router.py`) 상단에 `get_db`, `AsyncSession`, `Repository` 같은 DB 관련 직접 import가 있다면 정리할 준비를 합니다.

라우터는 오직 HTTP 요청을 받아서 UseCase로 전달하는 역할만 담당합니다.

---

## 2) [1단계] 데이터 모델 & DTO 정의 (`schemas/`, `domain/`)

가장 먼저 데이터 형태를 명확히 정리합니다.

### 2-1. Pydantic 스키마 정의 (`app/schemas/friday13th.py`)

```python
from pydantic import BaseModel
from typing import Optional

class Friday13thSchema(BaseModel):
    id: Optional[int] = None
    name: str
    status: str
    # 테이블 컬럼에 맞게 필드를 추가하세요.

    class Config:
        from_attributes = True
```

### 2-2. 유스케이스 Command DTO 정의 (`app/domain/commands.py`)

```python
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class CreateFriday13thCommand:
    id: int
    name: str
    status: str
```

---

## 3) [2단계] 책임 연쇄(CoR) 핸들러 구현 (`domain/handlers/`)

데이터를 유스케이스로 넘기기 전 검증/변환을 체인으로 분리합니다.

### 3-1. 베이스 핸들러 (`app/domain/handlers/base.py`)

```python
from typing import Any, Optional

class BaseHandler:
    def __init__(self):
        self._next_handler: Optional['BaseHandler'] = None

    def set_next(self, handler: 'BaseHandler') -> 'BaseHandler':
        self._next_handler = handler
        return handler

    def handle(self, request: Any) -> Any:
        if self._next_handler:
            return self._next_handler.handle(request)
        return request
```

### 3-2. 검증 핸들러 (`app/domain/handlers/validation_handler.py`)

```python
from typing import List, Dict, Any
from app.domain.handlers.base import BaseHandler

class DataValidationHandler(BaseHandler):
    def handle(self, request: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        print(f"[체인-검증] 데이터 정형화 및 필수값 체크 시작 (총 {len(request)}건)")
        validated_data = [row for row in request if row.get("name")]
        print(f"[체인-검증] 완료 (정상: {len(validated_data)}건, 필터링: {len(request) - len(validated_data)}건)")
        return super().handle(validated_data)
```

### 3-3. DTO 매핑 핸들러 (`app/domain/handlers/mapper_handler.py`)

```python
from typing import List, Dict, Any
from app.domain.handlers.base import BaseHandler
from app.domain.commands import CreateFriday13thCommand

class DomainMapperHandler(BaseHandler):
    def handle(self, request: List[Dict[str, Any]]) -> List[CreateFriday13thCommand]:
        print("[체인-변환] Dictionary 데이터를 Command DTO 객체로 변환 시작")
        commands = []
        for row in request:
            cmd = CreateFriday13thCommand(
                id=int(row.get("id")) if row.get("id") else None,
                name=row.get("name"),
                status=row.get("status"),
            )
            commands.append(cmd)
        print(f"[체인-변환] 완료 (Command DTO {len(commands)}개 생성됨)")
        return super().handle(commands)
```

---

## 4) [3단계] 유스케이스와 포트 구성 (`port/inbound/`, `use_case/`)

### 4-1. Input Port (`app/port/inbound/friday13th_use_case.py`)

```python
from abc import ABC, abstractmethod
from typing import List
from app.domain.commands import CreateFriday13thCommand

class Friday13thUseCase(ABC):
    @abstractmethod
    async def execute(self, commands: List[CreateFriday13thCommand], file_name: str) -> bool:
        pass
```

### 4-2. Interactor (`app/use_case/friday13th_interactor.py`)

```python
from typing import List
from app.port.inbound.friday13th_use_case import Friday13thUseCase
from app.port.outbound.friday13th_repository_port import Friday13thRepositoryPort
from app.domain.commands import CreateFriday13thCommand

class Friday13thInteractor(Friday13thUseCase):
    def __init__(self, repository_port: Friday13thRepositoryPort):
        self.repository = repository_port

    async def execute(self, commands: List[CreateFriday13thCommand], file_name: str) -> bool:
        print("[유스케이스] 라우터 및 체인을 통해 유스케이스로 전달된 상위 5개 레코드:")
        for cmd in commands[:5]:
            print(f"   - {cmd}")
        return await self.repository.save_all(commands, file_name)
```

---

## 5) [4단계] 레포지터리 패턴 적용 (`port/outbound/`, `adapter/outbound/`)

### 5-1. Output Port (`app/port/outbound/friday13th_repository_port.py`)

```python
from abc import ABC, abstractmethod
from typing import List
from app.domain.commands import CreateFriday13thCommand

class Friday13thRepositoryPort(ABC):
    @abstractmethod
    async def save_all(self, commands: List[CreateFriday13thCommand], file_name: str) -> bool:
        pass
```

### 5-2. PG Repository (`app/adapter/outbound/pg/friday13th_repository.py`)

```python
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.port.outbound.friday13th_repository_port import Friday13thRepositoryPort
from app.domain.commands import CreateFriday13thCommand

class Friday13thPgRepository(Friday13thRepositoryPort):
    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def save_all(self, commands: List[CreateFriday13thCommand], file_name: str) -> bool:
        print(f"[레포지터리] 저장 시작 file={file_name} rows={len(commands)}")
        try:
            # 기존 SQLAlchemy bulk insert 혹은 반복문 insert 로직을 여기에 작성
            await self.session.commit()
            print(f"[레포지터리] 저장 완료 file={file_name} rows={len(commands)}")
            return True
        except Exception as e:
            await self.session.rollback()
            print(f"[레포지터리] 에러 발생으로 롤백됨: {e}")
            raise e
```

---

## 6) [5단계] 라우터 얇게 만들기 & 체인 조립 (`adapter/inbound/`)

### 라우터 구현 예시 (`app/adapter/inbound/router.py`)

```python
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db_session
from app.domain.handlers.validation_handler import DataValidationHandler
from app.domain.handlers.mapper_handler import DomainMapperHandler
from app.adapter.outbound.pg.friday13th_repository import Friday13thPgRepository
from app.use_case.friday13th_interactor import Friday13thInteractor

router = APIRouter()

@router.post("/upload-friday13th")
async def upload_friday13th_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session)
):
    raw_data = [{"id": 1, "name": "Jason", "status": "active"}]  # 예시 데이터
    print(f"[라우터] 업로드된 파일({file.filename})에서 읽어온 상위 5개 레코드:")
    for row in raw_data[:5]:
        print(f"   - {row}")

    validation_handler = DataValidationHandler()
    mapper_handler = DomainMapperHandler()
    validation_handler.set_next(mapper_handler)
    commands = validation_handler.handle(raw_data)

    repository_adapter = Friday13thPgRepository(db_session=db)
    use_case = Friday13thInteractor(repository_port=repository_adapter)
    success = await use_case.execute(commands, file_name=file.filename)
    return {"success": success, "count": len(commands)}
```

---

## 7) Cursor 프롬프트 예시

아래 프롬프트를 그대로 사용해도 됩니다.

> 내가 전달한 가이드라인 문서의 [5단계] 라우터 구조와 [4단계] 레포지터리 어댑터 구조를 바탕으로, 현재 코드를 레포지터리 클래스로 안전하게 옮겨줘.  
> 특히 BaseHandler를 확장한 검증 및 매퍼 핸들러 체인이 라우터 안에서 완벽히 조립되어 터미널 로그 가이드라인대로 print문이 찍히도록 코드를 완성해줘.

