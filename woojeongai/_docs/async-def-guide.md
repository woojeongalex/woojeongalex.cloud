# async / def 선택 규칙 — CPU-bound vs I/O-bound

| 성격 | 예시 | Port 선언 | 구현 |
|------|------|-----------|------|
| I/O-bound | DB 조회, LLM API, 파일 읽기 | `async def` | `async def` + `await` |
| CPU-bound | Kiwi 형태소 분석, 수치 계산 | `def` | `def` (동기) |

## 핵심 원칙

- `async def`는 비블로킹을 **보장하지 않는다**. 내부가 CPU 연산이면 이벤트 루프를 그대로 블로킹한다.
- CPU-bound 메서드에 `async`를 붙이면 비블로킹인 것처럼 **오해를 유발**하므로 금지한다.
- Kiwi처럼 처리 시간이 길어질 수 있는 CPU 작업이 실제로 이벤트 루프를 막을 경우, 메서드 시그니처를 바꾸는 게 아니라 **호출 측에서 스레드풀로 넘긴다**.

```python
# ✅ Port: CPU-bound는 def
class AndrewsArchitectUseCase(ABC):
    def analyze_intent(self, question: str) -> dict:  # async 붙이지 않음
        pass

# ✅ Interactor: 동기 구현
def analyze_intent(self, question: str) -> dict:
    tokens = self.kiwi.tokenize(question)
    ...

# ✅ 호출 측(router/interactor)에서 무거울 때만 스레드풀 위임
result = await asyncio.to_thread(self.analyze_intent, question)

# ❌ CPU-bound에 async 붙이기 — 비블로킹처럼 보이지만 실제론 블로킹
async def analyze_intent(self, question: str) -> dict:
    tokens = self.kiwi.tokenize(question)  # 이벤트 루프 블로킹
    ...
```
