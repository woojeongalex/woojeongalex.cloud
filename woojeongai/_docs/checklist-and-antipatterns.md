# 코딩·리뷰 체크리스트 & 안티패턴

## 체크리스트

- [ ] Use Case가 `adapter.inbound` 스키마를 import 하지 않는가?
- [ ] Router가 Repository / `get_db` / Interactor 구현을 import 하지 않는가?
- [ ] Port 메서드가 **한 역할·짧은 동사**인가? (ISP)
- [ ] Fat Interface / 미사용 abstract 메서드 없는가?
- [ ] 조립이 `dependencies/*_director.py` 또는 `deps/`에만 있는가?
- [ ] schema ↔ dto 변환이 mapper에서 1회인가?
- [ ] `Depends()`가 라우터 파라미터에만 있는가?
- [ ] diff가 사용자 요청 범위만 포함하는가?

## 안티패턴 (하지 말 것)

```python
# ❌ 라우터에서 Repository 직접 조립
def _use_case(db):
    return EvaluationService(EvaluationRepository(db))

# ❌ Use Case에서 ORM Entity를 HTTP body로 직접 수신
async def save_evaluation(self, body: VocalEvaluationCreateRequest): ...

# ❌ Port에 쓰기+읽기 한꺼번에 (ISP 위반)
class TitanicRepository(ABC):
    async def upload(...): ...
    async def read_passengers(...): ...
    async def train_model(...): ...

# ❌ 클래스 속성에 Depends
class Router:
    use_case: UseCase = Depends(get_use_case)  # 절대 금지

# ❌ dependencies/에서 get_repository + get_use_case 미분리
def get_use_case(db: AsyncSession = Depends(get_db)) -> UseCase:
    return Interactor(PgRepository(session=db))  # 분리해야 함
```
