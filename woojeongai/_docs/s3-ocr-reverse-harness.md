# S3 → OCR 리버스 플로우 하네스 (silicon_valley 앱)

대상: `woojeongai/apps/silicon_valley/` (클린 아키텍처 · 헥사고날 Ports & Adapters).
원칙: 기존 S3 업로드 흐름(`POST /silicon_valley/s3-image/upload`)은 **한 줄도 수정하지 않는다**.
리버스 방향(S3 읽기 → OCR → 웹 응답) 전용 포트·어댑터·인터랙터를 신규 추가만 한다.
이 문서는 **설계·작업 지시서**이며, 실제 구현 코드는 이 문서에 작성하지 않는다.

전체 프로그램 목표: Flutter 촬영 → S3 저장 → 프론트(alexview) 진입 시 자동으로 S3 폴더 이미지를
인식하여 서버로 불러오고 → 서버에서 OCR로 텍스트 추출 → 웹 화면에 내용 표시.

---

## 0. 컨텍스트

### 0.1 기존 구현 (정방향 — 업로드)

| 계층 | 파일 | 역할 |
|------|------|------|
| 아웃바운드 포트 | `app/ports/output/s3_image_storage_port.py` | `upload()` 단일 메서드 (ISP) |
| 아웃바운드 어댑터 | `adapter/outbound/s3/s3_image_storage_adapter.py` | `S3Manager.put_bytes` 래핑 |
| 인바운드 포트 | `app/ports/input/s3_image_upload_use_case.py` | `upload(command) → result` |
| 인터랙터 | `app/use_cases/s3_image_upload_interactor.py` | 포트 위임만 |
| DTO | `app/dtos/s3_image_upload_dto.py` | `S3ImageUploadCommand`, `S3ImageUploadResult` |
| 라우터 | `adapter/inbound/api/v1/s3_image_upload_router.py` | `POST /s3-image/upload` |
| DI | `dependencies/s3_image_upload_provider.py` | `get_port` + `get_use_case` 분리 |

데이터 흐름 (정방향):
```
웹/Flutter → Router → Interactor → S3StoragePort.upload() → S3
```

### 0.2 코어 S3Manager 상태

`core/matrix/aws_s3_manager.py`의 `S3Manager`는 다음 메서드를 이미 보유한다:
- `list_objects(prefix, bucket)` → 키 목록 반환
- `download_file(key, local_path, bucket)` → 로컬 파일로 다운로드
- `put_bytes(key, data, content_type, bucket)` → 바이트 업로드

이 중 `list_objects`와 `download_file`은 앱 레벨(포트·인터랙터·라우터)로 **노출된 적이 없다**.
이번 작업에서 리버스 방향 포트를 통해 처음 노출한다.

### 0.3 OCR 현황

코드베이스에 OCR 관련 구현은 **전무**하다. Tesseract, Textract, EasyOCR 등 어떤 라이브러리도
도입된 적 없다. 이번 작업에서 신규 도입한다.

---

## 1. 왜 기존 업로드 포트에 읽기를 추가하면 안 되는가 (ISP)

`S3ImageStoragePort`에 `list_images()`나 `get_bytes()`를 추가하면 ISP 위반이다.

| | 기존 `S3ImageStoragePort` | 신규 `S3ImageReadPort` |
|---|---|---|
| 역할 | **쓰기 전용** — 이미지를 S3에 저장 | **읽기 전용** — S3에서 이미지를 가져옴 |
| 메서드 | `upload(filename, content_type, data)` | `list_images(prefix)`, `get_bytes(key)` |
| 클라이언트 | `S3ImageUploadInteractor` (업로드만 필요) | `S3ImageOcrInteractor` (읽기만 필요) |
| 변경 이유 | 저장 방식 변경 (S3 → GCS 등) | 조회 방식 변경 (페이지네이션, 필터 등) |

업로드 인터랙터는 읽기 메서드를 알 필요가 없고, OCR 인터랙터는 쓰기 메서드를 알 필요가 없다.
각자 자기가 쓰는 메서드만 포트에 가진다 — 이것이 ISP의 핵심이다.

마찬가지로 OCR은 S3와 관계없는 **별도 외부 능력**이므로 독립 포트(`OcrPort`)로 분리한다.

---

## 2. 리버스 흐름 — 데이터 방향 상세

정방향(업로드)과 리버스(OCR 읽기)를 비교한다.

### 2.1 정방향 (기존 — 무변경)

```
웹/Flutter ──①──▷ Router ──②──▷ Interactor ──③──▷ S3StoragePort.upload() ──④──▷ S3
                  (인바운드)      (앱 계층)         (아웃바운드 포트)           (인프라)
```

데이터가 **웹에서 출발**하여 S3에 도착. Interactor는 통과만(pass-through).

### 2.2 리버스 (신규)

```
웹(alexview) ◁──⑤── Router ◁──④── Interactor ──③──▷ S3ReadPort.list/get() ──②──▷ S3
                     (인바운드)      (앱 계층)          (아웃바운드 포트)           (인프라)
                                       │
                                       ├──③'──▷ OcrPort.extract_text()
                                       │         (아웃바운드 포트, CPU-bound)
                                       │
                                       └── 결과 조합: {key, url, extracted_text}
```

HTTP 요청 자체는 여전히 웹 → 서버 방향이지만, **데이터의 원점은 S3**이다.
Interactor가 S3에서 읽어온 이미지를 OCR로 가공한 뒤 웹으로 내보낸다 —
이것이 "리버스"의 의미다.

### 2.3 단계별 흐름

| 단계 | 위치 | 동작 | 계층 |
|------|------|------|------|
| ① | alexview 페이지 진입 | `GET /silicon_valley/s3-image/ocr?prefix=silicon_valley/` 자동 호출 | 프론트 |
| ② | `s3_image_ocr_router.py` | 쿼리 파라미터를 `S3ImageOcrCommand` DTO로 변환, UseCase 위임 | 인바운드 어댑터 |
| ③ | `S3ImageOcrInteractor` | `S3ImageReadPort.list_images(prefix)` 호출 → 이미지 키 목록 취득 | 앱 (UseCase) |
| ④ | `S3ImageOcrInteractor` | 각 키에 대해 `S3ImageReadPort.get_bytes(key)` → 이미지 바이트 취득 | 앱 (UseCase) |
| ⑤ | `S3ImageOcrInteractor` | `OcrPort.extract_text(data)` → OCR 텍스트 추출 (CPU-bound, 스레드풀) | 앱 (UseCase) |
| ⑥ | `S3ImageOcrInteractor` | `S3ImageOcrResult` DTO 조합 후 반환 | 앱 (UseCase) |
| ⑦ | `s3_image_ocr_router.py` | DTO → Pydantic Response 변환, JSON 응답 | 인바운드 어댑터 |
| ⑧ | alexview 페이지 | 이미지 목록 + 추출 텍스트를 화면에 렌더링 | 프론트 |

---

## 3. ISP 포트 설계

### 3.1 S3ImageReadPort (아웃바운드 — 읽기 전용)

```
app/ports/output/s3_image_read_port.py

class S3ImageReadPort(ABC):
    async def list_images(self, prefix: str) -> list[str]:
        """prefix 하위의 이미지 키 목록을 반환한다."""

    async def get_bytes(self, key: str) -> bytes:
        """S3 키에 해당하는 이미지를 바이트로 반환한다."""
```

I/O-bound (S3 네트워크 호출) → `async def`.
어댑터(`S3ImageReadAdapter`)에서 `asyncio.to_thread`로 동기 `S3Manager` 호출을 감싼다.

> **`download_file` 대신 `get_object` 사용:**
> `S3Manager.download_file()`은 로컬 파일시스템에 쓴다.
> OCR은 바이트만 필요하므로 어댑터에서 `boto3.get_object()['Body'].read()`를 직접 호출하거나,
> `S3Manager`에 `get_bytes(key)` 메서드를 추가하는 것이 낫다.
> `S3Manager` 확장은 코어 유틸리티 변경이므로 최소한으로 `get_bytes()` 한 메서드만 추가한다.

### 3.2 OcrPort (아웃바운드 — 텍스트 추출)

```
app/ports/output/ocr_port.py

class OcrPort(ABC):
    def extract_text(self, data: bytes) -> str:
        """이미지 바이트에서 텍스트를 추출한다."""
```

CPU-bound (EasyOCR 추론) → `def` (동기).
호출 측(Interactor)에서 `await asyncio.to_thread(self._ocr.extract_text, data)`로 스레드풀 위임한다.
이는 CLAUDE.md §13의 "CPU-bound는 def, 호출 측에서 스레드풀 위임" 규칙을 따른다.

### 3.3 S3ImageOcrUseCase (인바운드 — 입력 포트)

```
app/ports/input/s3_image_ocr_use_case.py

class S3ImageOcrUseCase(ABC):
    async def scan(self, command: S3ImageOcrCommand) -> S3ImageOcrResult:
        """S3 prefix 하위 이미지를 OCR 스캔하여 텍스트를 반환한다."""
```

---

## 4. DTO 설계

```
app/dtos/s3_image_ocr_dto.py

@dataclass(frozen=True)
class S3ImageOcrCommand:
    prefix: str                        # S3 검색 prefix (예: "silicon_valley/")

@dataclass(frozen=True)
class S3ImageOcrItem:
    key: str                           # S3 오브젝트 키
    url: str                           # S3 퍼블릭 URL
    extracted_text: str                # OCR 추출 텍스트

@dataclass(frozen=True)
class S3ImageOcrResult:
    items: list[S3ImageOcrItem]        # 이미지별 OCR 결과
    total: int                         # 총 이미지 수
```

---

## 5. Interactor 설계

```
app/use_cases/s3_image_ocr_interactor.py

class S3ImageOcrInteractor(S3ImageOcrUseCase):
    def __init__(self, read_port: S3ImageReadPort, ocr_port: OcrPort):
        self._read = read_port
        self._ocr = ocr_port
```

처리 순서:

1. `keys = await self._read.list_images(command.prefix)`
2. 이미지 확장자 필터링 (`.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`)
3. 각 키에 대해:
   - `data = await self._read.get_bytes(key)`
   - `text = await asyncio.to_thread(self._ocr.extract_text, data)`
   - URL 조합: `https://{bucket}.s3.{region}.amazonaws.com/{key}`
4. `S3ImageOcrResult` 조합 후 반환

> **병렬 처리 고려:** 이미지가 다수일 경우 `asyncio.gather`로 병렬 다운로드+OCR이 가능하지만,
> 초기 구현은 순차 처리로 시작하고 성능 이슈 발생 시 병렬로 전환한다.
> EasyOCR 모델 로드가 무겁기 때문에 어댑터에서 모델을 1회 로드 후 재사용해야 한다.

---

## 6. 어댑터 설계

### 6.1 S3ImageReadAdapter (아웃바운드)

```
adapter/outbound/s3/s3_image_read_adapter.py

class S3ImageReadAdapter(S3ImageReadPort):
    def __init__(self, s3_manager: S3Manager):
        self._s3 = s3_manager
```

- `list_images(prefix)`: `asyncio.to_thread(self._s3.list_objects, prefix)` 호출,
  이미지 확장자만 필터
- `get_bytes(key)`: `asyncio.to_thread`로 `boto3.get_object()['Body'].read()` 호출
  (S3Manager에 `get_bytes` 추가 또는 어댑터에서 직접 boto3 접근)

### 6.2 EasyOcrAdapter (아웃바운드)

```
adapter/outbound/ocr/easyocr_adapter.py

class EasyOcrAdapter(OcrPort):
    def __init__(self, languages: list[str] | None = None):
        self._reader = easyocr.Reader(languages or ["ko", "en"])
```

- `extract_text(data)`: `self._reader.readtext(data, detail=0)` → 문자열 리스트 → 줄바꿈 join
- CPU-bound이므로 `def` (동기)
- `_reader`는 `__init__`에서 1회 생성 후 재사용 (모델 로드 비용 절감)
- DI 팩토리에서 싱글턴으로 관리하여 요청마다 모델을 재로드하지 않도록 한다

### 6.3 인바운드 라우터

```
adapter/inbound/api/v1/s3_image_ocr_router.py

s3_image_ocr_router = APIRouter(prefix="/s3-image", tags=["s3-image-ocr"])

@s3_image_ocr_router.get("/ocr", summary="S3 이미지 OCR 텍스트 추출")
async def scan_images(
    prefix: str = Query("silicon_valley/"),
    use_case: S3ImageOcrUseCase = Depends(get_s3_image_ocr_use_case),
) -> S3ImageOcrResponse:
    ...
```

Thin router — 비즈니스 로직 없이 UseCase에 위임만.

### 6.4 인바운드 스키마

```
adapter/inbound/api/schemas/s3_image_ocr_schema.py

class S3ImageOcrItemResponse(BaseModel):
    key: str
    url: str
    extracted_text: str

class S3ImageOcrResponse(BaseModel):
    items: list[S3ImageOcrItemResponse]
    total: int
```

---

## 7. Director (DI 조립)

```
dependencies/s3_image_ocr_provider.py

def get_s3_image_read_port() -> S3ImageReadPort:
    return S3ImageReadAdapter(s3_manager=get_s3_manager())

def get_ocr_port() -> OcrPort:
    return EasyOcrAdapter(languages=["ko", "en"])  # 싱글턴 고려

def get_s3_image_ocr_use_case(
    read_port: S3ImageReadPort = Depends(get_s3_image_read_port),
    ocr_port: OcrPort = Depends(get_ocr_port),
) -> S3ImageOcrUseCase:
    return S3ImageOcrInteractor(read_port=read_port, ocr_port=ocr_port)
```

`get_repository` + `get_use_case` 분리 규칙에 따라 아웃바운드 포트 팩토리 2개(read, ocr)와
유스케이스 팩토리 1개를 별도 함수로 분리한다.

> **EasyOCR 싱글턴:** `easyocr.Reader` 초기화 시 모델을 디스크에서 로드하므로
> 요청마다 생성하면 수 초 지연이 발생한다. `get_ocr_port()`에서 모듈 레벨 캐시 또는
> `functools.lru_cache`로 싱글턴 처리한다.

---

## 8. 신규 엔드포인트 계약

### 8.1 요청/응답

```
GET /silicon_valley/s3-image/ocr?prefix=silicon_valley/

Response 200:
{
  "items": [
    {
      "key": "silicon_valley/a1b2c3.jpg",
      "url": "https://bucket.s3.ap-northeast-2.amazonaws.com/silicon_valley/a1b2c3.jpg",
      "extracted_text": "OCR로 추출된 텍스트 내용..."
    },
    ...
  ],
  "total": 3
}

Response 500:
  - s3_access_error  — S3 접근 실패 (자격 증명·버킷·네트워크)
  - ocr_error        — OCR 처리 중 오류 (모델 로드 실패·이미지 손상)
```

### 8.2 라우터 등록

`adapter/inbound/api/__init__.py`에 추가:

```python
from silicon_valley.adapter.inbound.api.v1.s3_image_ocr_router import s3_image_ocr_router
silicon_valley_router.include_router(s3_image_ocr_router)
```

---

## 9. OCR 라이브러리 선택: EasyOCR

| 항목 | EasyOCR | AWS Textract | Tesseract |
|------|---------|-------------|-----------|
| 한국어 지원 | O (80+ 언어) | O (제한적) | O (학습 데이터 필요) |
| 비용 | 무료 (오픈소스) | 유료 ($1.50/1000페이지) | 무료 (오픈소스) |
| 설치 | `pip install easyocr` | boto3 (이미 설치됨) | 시스템 패키지 필요 |
| 정확도 | 양호 (딥러닝 기반) | 우수 | 보통 |
| GPU 활용 | O (PyTorch) | N/A (클라우드) | X |
| 서버 의존성 | PyTorch (~2GB) | 없음 | libstesseract |

선택 이유: 한국어 지원이 좋고, 추가 비용 없으며, Python 네이티브(`pip install`)로 설치 가능.
EC2 인스턴스에서 CPU 모드로 동작 가능 (GPU 없어도 됨, 다만 느림).

`requirements.txt` 추가:
```
easyocr>=1.7.0
```

> **주의:** EasyOCR은 PyTorch에 의존하므로 Docker 이미지 크기가 상당히 증가한다.
> 최초 실행 시 모델 파일 다운로드가 필요하다 (한국어+영어 약 100MB).
> Dockerfile에서 모델 사전 다운로드를 포함하거나, 볼륨 마운트로 모델 캐시를 유지한다.

---

## 10. 신규 파일 목록 (체크리스트)

silicon_valley 앱 내 추가 파일:

```
app/
  ports/
    output/
      s3_image_read_port.py          ← S3 읽기 아웃바운드 포트 (ABC)
      ocr_port.py                    ← OCR 아웃바운드 포트 (ABC)
    input/
      s3_image_ocr_use_case.py       ← OCR 인바운드 포트 (ABC)
  dtos/
    s3_image_ocr_dto.py              ← Command / Item / Result DTO
  use_cases/
    s3_image_ocr_interactor.py       ← Interactor (S3Read + OCR 조합)

adapter/
  outbound/
    s3/
      s3_image_read_adapter.py       ← S3Manager 읽기 래핑
    ocr/
      __init__.py
      easyocr_adapter.py             ← EasyOCR 구현 (CPU-bound)
  inbound/
    api/
      v1/
        s3_image_ocr_router.py       ← thin router
      schemas/
        s3_image_ocr_schema.py       ← Pydantic Response

dependencies/
  s3_image_ocr_provider.py           ← DI 조립 (read_port + ocr_port + use_case)
```

코어 변경 (최소):
```
core/matrix/aws_s3_manager.py       ← get_bytes(key, bucket) 메서드 1개 추가
```

등록:
```
adapter/inbound/api/__init__.py     ← s3_image_ocr_router include 추가
```

---

## 11. 스타 토폴로지 시각화

기존 silicon_valley 앱의 스타 토폴로지에 리버스 흐름이 추가된 형태:

```
                         ┌─────────────────┐
                         │  웹 (alexview)   │
                         │  Flutter (촬영)  │
                         └────────┬────────┘
                                  │
                    ┌─────────────┼─────────────┐
                    ▼             ▼              ▼
            ┌──────────┐  ┌──────────┐   ┌──────────┐
            │ 업로드    │  │ OCR 스캔 │   │ Gemini   │
            │ Router   │  │ Router   │   │ Router   │
            │ (POST)   │  │ (GET)    │   │ (POST)   │
            └────┬─────┘  └────┬─────┘   └──────────┘
                 │             │
                 ▼             ▼
         ┌─────────────────────────────┐
         │        App (Interactor)      │
         │                              │
         │  Upload      OcrScan         │
         │  Interactor  Interactor      │
         └──────┬──────────┬──┬─────────┘
                │          │  │
                ▼          ▼  ▼
         ┌──────────┐ ┌──────┐ ┌────────┐
         │ Storage  │ │ Read │ │  OCR   │
         │ Port     │ │ Port │ │  Port  │
         │ (쓰기)   │ │(읽기)│ │(추출)  │
         └────┬─────┘ └──┬──┘ └───┬────┘
              │          │        │
              ▼          ▼        ▼
         ┌─────────┐          ┌────────┐
         │   S3    │          │EasyOCR │
         │ (인프라) │          │(라이브러리)│
         └─────────┘          └────────┘
```

포트가 별(star)처럼 중심(App)에서 바깥(인프라)으로 뻗어나가며,
각 포트는 단일 책임을 가진다.

---

## 12. async / def 선택 (§13 규칙 적용)

| 메서드 | 성격 | 선언 | 이유 |
|--------|------|------|------|
| `S3ImageReadPort.list_images()` | I/O (S3 네트워크) | `async def` | 네트워크 대기 |
| `S3ImageReadPort.get_bytes()` | I/O (S3 네트워크) | `async def` | 네트워크 대기 |
| `OcrPort.extract_text()` | CPU-bound (딥러닝 추론) | `def` | 이벤트 루프 블로킹 방지 |
| `S3ImageOcrInteractor.scan()` | 오케스트레이션 | `async def` | 내부에서 async 포트 호출 |

Interactor에서 OCR 호출 시:
```python
text = await asyncio.to_thread(self._ocr.extract_text, data)
```

---

## 13. 보안 체크리스트

- [ ] S3 prefix 인젝션 방지 — `prefix` 파라미터에 `..`이나 절대 경로가 포함되지 않도록 검증
- [ ] 이미지 확장자 화이트리스트 — `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`만 처리
- [ ] 파일 크기 제한 — OCR 처리할 이미지의 최대 크기 설정 (예: 10MB)
- [ ] 목록 개수 제한 — `list_images` 결과가 과다할 경우 페이지네이션 또는 상한 설정
- [ ] S3 자격 증명 — 기존 `S3Manager`의 `Keymaker` 경로 그대로 사용, 신규 키 불필요
- [ ] OCR 결과에 민감 정보가 포함될 수 있음 — 로그에 추출 텍스트를 기록하지 않는다

---

## 14. 환경변수

신규 환경변수는 **없다**. 기존 S3 자격 증명(`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`,
`AWS_REGION`, `AWS_S3_BUCKET`)을 그대로 사용한다.

EasyOCR 모델 캐시 경로는 기본값(`~/.EasyOCR/`)을 사용하되,
Docker 환경에서는 볼륨 마운트로 모델을 영속화한다:
```yaml
volumes:
  - easyocr_models:/root/.EasyOCR
```

---

## 15. 검증 절차

1. S3에 테스트 이미지 업로드 — 기존 `POST /silicon_valley/s3-image/upload` 사용.
2. `curl "GET /silicon_valley/s3-image/ocr?prefix=silicon_valley/"` → 200 + 이미지 목록 + OCR 텍스트 확인.
3. 한국어 이미지 OCR 결과 확인 — 한국어 텍스트가 정상 추출되는지.
4. 이미지가 없는 prefix로 요청 → `{"items": [], "total": 0}` 확인.
5. 기존 `POST /silicon_valley/s3-image/upload` 회귀 테스트 — 무변경 확인.
6. 하네스 게이트: `ruff check . --fix` → `ruff format .` → `mypy . --ignore-missing-imports`.

---

## 16. 완료 기준 (Acceptance Criteria)

- [ ] `GET /silicon_valley/s3-image/ocr` 신규 추가, 기존 업로드 라우트 무변경
- [ ] ISP 준수: `S3ImageReadPort`(읽기), `OcrPort`(추출), `S3ImageStoragePort`(쓰기) 각각 독립
- [ ] OcrPort가 `def`(동기), Interactor에서 `asyncio.to_thread`로 호출
- [ ] Director 패턴: `get_read_port` + `get_ocr_port` + `get_use_case` 분리
- [ ] EasyOCR Reader 싱글턴 — 요청마다 모델 재로드하지 않음
- [ ] S3Manager에 `get_bytes()` 메서드 추가 (코어 최소 변경)
- [ ] `adapter/inbound/api/__init__.py`에 라우터 등록
- [ ] 한국어+영어 OCR 동작 확인
- [ ] 하네스 게이트(`ruff`, `mypy`) 통과
