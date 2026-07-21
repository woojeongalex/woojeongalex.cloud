# SSD 물체 감지 에이전트 구현 지시서

> 대상: `woojeongai/apps/star_craft/`
> 패턴 정본: `woojeongai/CLAUDE.md` §3–5, `star_craft/dependencies/yolo_provider.py`, `star_craft/adapter/outbound/resource_adapters/yolo/`
> 하드웨어: RTX 3050 8GB VRAM / RAM 16GB / i7-8700
> 완료 기준: 하네스 게이트(`ruff check`, `ruff format`, `mypy`) 전부 통과

---

## 0. 구현 전 필독

1. `woojeongai/CLAUDE.md` 전문을 읽고 4계층·ISP·DIP·Director 패턴을 숙지한다.
2. **패턴 정본** — 아래 파일을 반드시 먼저 읽어 기존 스타일을 맞춘다.
   - `star_craft/dependencies/yolo_provider.py`
   - `star_craft/adapter/outbound/resource_adapters/yolo/yolo_model_adapter.py`
   - `star_craft/app/use_cases/yolo_interactor.py`
3. 기존 파일을 **절대 수정하지 않는다**. 신규 파일만 추가한다.
4. 모든 파일 상단에 `from __future__ import annotations` 를 붙인다.
5. 물체 감지 추론은 CPU-bound → `def` (동기), 호출 측에서 `asyncio.to_thread` 위임.

---

## 1. 모델 선택 — SSD 대신 SSDLite320 + MobileNetV3

원서의 SSD는 VGG-16 백본으로 RTX 3050 8GB에서 파인튜닝 시 VRAM 부족.
아래 모델 중 하나를 선택한다 (기본값: SSDLite320).

| 모델 | VRAM 추론 | VRAM 파인튜닝(QLoRA) | COCO mAP | torchvision |
|------|-----------|---------------------|----------|------------|
| **SSDLite320_MobileNetV3** | ~1.5GB | ~3GB (배치 8) | 21.3 | ✅ 기본값 |
| SSD300_VGG16 | ~4GB | ⚠️ 배치 2만 가능 | 25.1 | ✅ |
| RT-DETR-L (추천 대안) | ~5GB | ~6GB (QLoRA, 배치 2) | 53.0 | HuggingFace |
| YOLOv8n (이미 구현됨) | ~1GB | — | 37.3 | ultralytics |

> **QLoRA 파인튜닝 목적이라면 RT-DETR-L 추천** — HuggingFace 기반으로
> `prepare_model_for_kbit_training` 바로 적용 가능.

---

## 2. 구현할 기능

SSDLite320(또는 RT-DETR-L)로 이미지에서 물체를 감지하고,

- 감지 결과(바운딩박스 + 레이블 + 신뢰도)를 **Neo4j Graph DB** 에 노드로 저장한다.
- 감지 결과 이미지(bbox 시각화)를 **S3** 에 업로드한다.
- FastAPI `POST /api/star-craft/detection/detect` 엔드포인트로 이미지를 수신한다.
- (선택) `POST /api/star-craft/detection/train` 엔드포인트로 커스텀 데이터셋 파인튜닝.

---

## 3. 생성할 파일 목록 (순서 엄수)

### Step 1 — Domain Value Object

**`domain/value_objects/detection_vo.py`**
```
- frozen dataclass
- DetectionBox: label: str, confidence: float, x1: float, y1: float, x2: float, y2: float
- DetectionVO: boxes: list[DetectionBox], image_width: int, image_height: int
- __post_init__ 검증: confidence 0.0~1.0, 좌표 범위 0.0~1.0(정규화)
```

### Step 2 — DTOs

**`app/dtos/detection_dto.py`**
```
- DetectCommand(frozen dataclass):
    filename: str
    content_type: str
    image_bytes: bytes
    confidence_threshold: float = 0.5
    
- DetectResponse(frozen dataclass):
    node_id: str
    filename: str
    detected_count: int
    boxes: list[dict]   # {label: str, confidence: float, bbox: [x1,y1,x2,y2]}
    result_image_url: str

- TrainCommand(frozen dataclass):
    dataset_path: str
    epochs: int
    batch_size: int
    device: str = cuda

- TrainResponse(frozen dataclass):
    weights_path: str
    epochs: int
    classes: list[str]
```

### Step 3 — Outbound Ports (ISP: 포트 최소화)

**`app/ports/output/detection_model_port.py`**
```python
class DetectionModelPort(ABC):
    def save(self, trained_weights_path: str) -> str: ...   # 정본 경로 반환
    def load_path(self) -> str: ...                         # 없으면 FileNotFoundError
```

**`app/ports/output/detection_graph_port.py`**
```python
class DetectionGraphPort(ABC):
    async def save_detection(
        self,
        filename: str,
        boxes: list[dict],
        result_image_url: str,
    ) -> str: ...  # 반환: node_id
```

**`app/ports/output/detection_storage_port.py`**
```python
class DetectionStoragePort(ABC):
    async def save_result_image(
        self, filename: str, image_bytes: bytes
    ) -> str: ...  # 반환: S3 URL
```

### Step 4 — Inbound Port

**`app/ports/input/detection_use_case.py`**
```python
class DetectionUseCase(ABC):
    async def detect(self, cmd: DetectCommand) -> DetectResponse: ...
    def train(self, cmd: TrainCommand) -> TrainResponse: ...
    # train은 CPU/GPU-bound → def (동기)
```

### Step 5 — Tool 함수 (CPU/GPU-bound)

**`app/tools/ssd_detect_tool.py`**
```
- 함수: detect_objects(image_bytes: bytes, threshold: float) -> DetectionVO
- 모델 로드: torchvision.models.detection.ssdlite320_mobilenet_v3_large(pretrained=True)
- 모델 싱글턴: _model = None / _model_lock = threading.Lock() — 요청마다 새로 로드 금지
- 전처리:
    img = Image.open(io.BytesIO(image_bytes)).convert(RGB)
    tensor = F.to_tensor(img).unsqueeze(0)
    device = cuda if torch.cuda.is_available() else cpu
- 추론: model.eval() + torch.no_grad()
- 후처리:
    결과에서 scores > threshold 인 박스만 필터
    bbox를 이미지 크기로 나눠 0~1 정규화
    COCO 91클래스 레이블 매핑 (별도 COCO_LABELS 딕셔너리)
- 반환: DetectionVO
- CPU/GPU-bound → def detect_objects(...) — async 절대 금지
```

**`app/tools/detection_visualizer.py`**
```
- 함수: draw_boxes(image_bytes: bytes, boxes: list[DetectionBox]) -> bytes
- PIL.ImageDraw 로 bbox + 레이블 텍스트 렌더링
- 반환: PNG bytes
- def (동기)
```

### Step 6 — Interactor

**`app/use_cases/detection_interactor.py`**
```
- DetectionInteractor(DetectionUseCase) 구현
- __init__: model: DetectionModelPort, graph: DetectionGraphPort, storage: DetectionStoragePort

- async def detect(self, cmd: DetectCommand) -> DetectResponse:
    1. result_vo = await asyncio.to_thread(detect_objects, cmd.image_bytes, cmd.confidence_threshold)
    2. vis_bytes = await asyncio.to_thread(draw_boxes, cmd.image_bytes, result_vo.boxes)
    3. url = await self.storage.save_result_image(cmd.filename, vis_bytes)
    4. boxes_dict = [{label: b.label, confidence: b.confidence, bbox: [b.x1, b.y1, b.x2, b.y2]} for b in result_vo.boxes]
    5. node_id = await self.graph.save_detection(cmd.filename, boxes_dict, url)
    6. return DetectResponse(...)

- def train(self, cmd: TrainCommand) -> TrainResponse:
    # SSDLite 파인튜닝 — CPU/GPU-bound이므로 def (동기)
    # 커스텀 데이터셋 로드 → torchvision DataLoader
    # optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9)
    # 학습 루프 → self.model.save(best_weights_path)
    # 반환: TrainResponse

- adapter/inbound 스키마 import 금지
```

### Step 7 — Outbound Adapters

**`adapter/outbound/resource_adapters/ssd/ssd_model_adapter.py`**
```
- DetectionModelPort 구현
- yolo_model_adapter.py 와 동일한 구조
- __init__: model_path: str
- save: shutil.copyfile(trained_weights_path, self._model_path)
- load_path: FileNotFoundError 없으면
```

**`adapter/outbound/neo4j/neo4j_detection_repository.py`**
```
- DetectionGraphPort 구현
- __init__: driver (neo4j.AsyncDriver)
- save_detection:
    MERGE (n:ObjectDetection {filename: $filename})
    SET n.detected_count = $count,
        n.boxes = $boxes_json,
        n.result_image_url = $url,
        n.updated_at = timestamp()
    RETURN elementId(n) AS node_id
  boxes는 json.dumps(boxes) 로 직렬화
- 반환: node_id (str)
- 로깅: INFO 1줄
```

**`adapter/outbound/s3/s3_detection_storage.py`**
```
- DetectionStoragePort 구현
- __init__: bucket: str, region: str
- save_result_image: boto3 put_object → 공개 URL 반환
- star_craft/adapter/outbound/s3/s3_image_storage_gateway.py 참고하여 동일 패턴 적용
```

### Step 8 — Inbound Adapter

**`adapter/inbound/api/schemas/detection_schema.py`**
```python
class DetectResponse(BaseModel):
    node_id: str
    filename: str
    detected_count: int
    boxes: list[dict]
    result_image_url: str

class TrainRequest(BaseModel):
    dataset_path: str
    epochs: int = 10
    batch_size: int = 8
    device: str = cuda

class TrainResponse(BaseModel):
    weights_path: str
    epochs: int
    classes: list[str]
```

**`adapter/inbound/api/mappers/detection_mapper.py`**
```
- upload_to_detect_command(file: UploadFile, data: bytes, threshold: float) -> DetectCommand
- train_request_to_command(req: TrainRequest) -> TrainCommand
- detect_dto_to_response(dto: DetectResponse) -> DetectResponseSchema
- train_dto_to_response(dto: TrainResponse) -> TrainResponseSchema
```

**`adapter/inbound/api/v1/detection_router.py`**
```
- prefix=/detection, tags=[Detection]

- POST /detect:
    file: UploadFile = File(...)
    threshold: float = Query(0.5, ge=0.1, le=1.0)
    use_case: DetectionUseCase = Depends(get_detection_use_case)
    →  data = await file.read()
       cmd = upload_to_detect_command(file, data, threshold)
       result = await use_case.detect(cmd)
       return detect_dto_to_response(result)

- POST /train:
    req: TrainRequest
    use_case: DetectionUseCase = Depends(get_detection_use_case)
    → cmd = train_request_to_command(req)
       result = await asyncio.to_thread(use_case.train, cmd)
       return train_dto_to_response(result)
    # train()은 동기 메서드 → 라우터에서 asyncio.to_thread 위임
```

**`adapter/inbound/api/deps/detection_deps.py`**
```python
from star_craft.dependencies.detection_provider import get_detection_use_case
```

### Step 9 — Director

**`dependencies/detection_provider.py`**
```
환경변수:
  DETECTION_MODEL_PATH  (기본: resources/models/ssd_detector.pt)
  DETECTION_S3_BUCKET
  AWS_REGION            (기본: ap-northeast-2)
  NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

- get_detection_model_port() -> DetectionModelPort:
    return SsdModelAdapter(model_path=os.getenv(DETECTION_MODEL_PATH, _DEFAULT_MODEL_PATH))

- get_detection_graph_port() -> DetectionGraphPort:
    driver = neo4j.AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return Neo4jDetectionRepository(driver=driver)

- get_detection_storage_port() -> DetectionStoragePort:
    return S3DetectionStorage(bucket=..., region=...)

- get_detection_use_case(
      model: DetectionModelPort = Depends(get_detection_model_port),
      graph: DetectionGraphPort = Depends(get_detection_graph_port),
      storage: DetectionStoragePort = Depends(get_detection_storage_port),
  ) -> DetectionUseCase:
    return DetectionInteractor(model=model, graph=graph, storage=storage)

# 3개 포트 팩토리 반드시 분리 (CLAUDE.md §4 DIP 규칙)
```

### Step 10 — main.py 등록

`woojeongai/main.py` 에 추가:
```python
from star_craft.adapter.inbound.api.v1.detection_router import router as detection_router
app.include_router(detection_router, prefix=/api/star-craft)
```

---

## 4. QLoRA 파인튜닝 가이드 (RTX 3050 8GB)

### 선택 A — SSDLite320 직접 파인튜닝 (QLoRA 불필요, 모델 소형)

```python
# app/use_cases/detection_interactor.py → def train() 내부
import torchvision
from torchvision.models.detection import ssdlite320_mobilenet_v3_large, SSDLite320_MobileNet_V3_Large_Weights

model = ssdlite320_mobilenet_v3_large(weights=SSDLite320_MobileNet_V3_Large_Weights.DEFAULT)
# 헤드만 교체 (커스텀 클래스 수)
in_channels = [672, 480]
num_anchors = model.anchor_generator.num_anchors_per_location()
model.head = SSDLiteHead(in_channels, num_anchors, num_classes=<your_class_count>+1)
model.to(cuda)

optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9, weight_decay=5e-4)
# 배치 8, 에폭 20 → RTX 3050 8GB VRAM 내 처리 가능
```

### 선택 B — RT-DETR-L + QLoRA (더 높은 정확도, HuggingFace 기반)

```python
from transformers import RTDetrForObjectDetection, BitsAndBytesConfig
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type=nf4,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,  # RAM 16GB 안전
)

model = RTDetrForObjectDetection.from_pretrained(
    PekingU/rtdetr_r50vd_coco_o365,
    quantization_config=bnb_config,
    num_labels=<your_class_count>,
    ignore_mismatched_sizes=True,
)
model = prepare_model_for_kbit_training(model)

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=[q_proj, v_proj],
    lora_dropout=0.05,
    bias=none,
)
model = get_peft_model(model, lora_config)
# trainable params: ~2M / 32M (6.3%) — 8GB VRAM 내 배치 2 가능

# 학습 완료 후 병합
model = model.merge_and_unload()
# → SsdModelAdapter.save()로 정본 경로에 저장
```

### 학습 설정 (RTX 3050 8GB 기준)

```python
from transformers import TrainingArguments

TrainingArguments(
    per_device_train_batch_size=2,      # 8GB VRAM
    gradient_accumulation_steps=4,      # 유효 배치 8
    num_train_epochs=20,
    learning_rate=1e-4,
    fp16=True,
    optim=paged_adamw_8bit,           # RAM 16GB 고려
    dataloader_num_workers=4,           # i7-8700 6코어
    warmup_ratio=0.05,
    lr_scheduler_type=cosine,
)
```

---

## 5. COCO 클래스 레이블 (ssd_detect_tool.py 에 포함)

```python
COCO_LABELS = {
    1: person, 2: bicycle, 3: car, 4: motorcycle, 5: airplane,
    6: bus, 7: train, 8: truck, 9: boat, 10: traffic light,
    11: fire hydrant, 13: stop sign, 14: parking meter, 15: bench,
    16: bird, 17: cat, 18: dog, 19: horse, 20: sheep,
    21: cow, 22: elephant, 23: bear, 24: zebra, 25: giraffe,
    27: backpack, 28: umbrella, 31: handbag, 32: tie, 33: suitcase,
    34: frisbee, 35: skis, 36: snowboard, 37: sports ball, 38: kite,
    39: baseball bat, 40: baseball glove, 41: skateboard, 42: surfboard,
    43: tennis racket, 44: bottle, 46: wine glass, 47: cup,
    48: fork, 49: knife, 50: spoon, 51: bowl, 52: banana,
    53: apple, 54: sandwich, 55: orange, 56: broccoli, 57: carrot,
    58: hot dog, 59: pizza, 60: donut, 61: cake, 62: chair,
    63: couch, 64: potted plant, 65: bed, 67: dining table,
    70: toilet, 72: tv, 73: laptop, 74: mouse, 75: remote,
    76: keyboard, 77: cell phone, 78: microwave, 79: oven,
    80: toaster, 81: sink, 82: refrigerator, 84: book,
    85: clock, 86: vase, 87: scissors, 88: teddy bear,
    89: hair drier, 90: toothbrush,
}
```

---

## 6. 안티패턴 — 하지 말 것

```python
# ❌ 추론 함수에 async 붙이기 (CPU/GPU-bound)
async def detect_objects(image_bytes: bytes): ...

# ❌ 라우터에서 asyncio.to_thread 없이 동기 train 직접 호출
result = use_case.train(cmd)   # 이벤트 루프 수십 초 블로킹

# ❌ 3개 포트를 하나로 합치기 (ISP 위반)
class DetectionPort(ABC):
    def save(...): ...
    async def save_detection(...): ...
    async def save_result_image(...): ...

# ❌ 모델을 요청마다 새로 로드
async def detect(self, cmd):
    model = ssdlite320_mobilenet_v3_large(pretrained=True)  # 매 요청마다 로드 금지

# ❌ Director에서 포트 팩토리 미분리
def get_detection_use_case(db=...):
    return DetectionInteractor(
        model=SsdModelAdapter(...),
        graph=Neo4jDetectionRepository(...),
        storage=S3DetectionStorage(...),
    )
```

---

## 7. 하네스 게이트 (완료 조건)

```bash
cd woojeongai && ruff check . --fix
```

```bash
ruff format .
```

```bash
mypy . --ignore-missing-imports
```

```bash
python main.py
```

```bash
curl -X POST http://localhost:8000/api/star-craft/detection/detect \
  -F file=@test_image.jpg \
  -F threshold=0.5
```

---

## 8. 의존성 추가 (requirements.txt)

```
torchvision>=0.15.0
torch>=2.0.0
Pillow>=10.0.0
neo4j>=5.0.0
boto3>=1.26.0
# QLoRA 선택 시 추가
transformers>=4.40.0
peft>=0.10.0
bitsandbytes>=0.43.0
```

---

## 9. 완료 체크리스트

- [ ] `detect_objects`와 `draw_boxes`가 `def` (동기) 인가?
- [ ] Interactor에서 `asyncio.to_thread`로 툴 함수를 호출하는가?
- [ ] 라우터에서 `train()`을 `asyncio.to_thread`로 위임하는가?
- [ ] `DetectionModelPort`, `DetectionGraphPort`, `DetectionStoragePort` 가 별도 파일로 분리되어 있는가?
- [ ] 모델이 모듈 레벨 싱글턴으로 1회만 로드되는가? (`threading.Lock`)
- [ ] `detection_provider.py` 에 3개 포트 팩토리가 분리되어 있는가?
- [ ] `DetectionInteractor`가 `adapter/inbound` 스키마를 import하지 않는가?
- [ ] 하네스 게이트 3개(`ruff check`, `ruff format`, `mypy`) 전부 통과하는가?

