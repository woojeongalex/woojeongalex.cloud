# 1. 라이브러리를 불러옵니다.

import torch
from ultralytics import YOLO

# 2. GPU(MPS)만 사용합니다.
#    맥북(Apple Silicon)은 CUDA가 없고 MPS(Metal) 백엔드를 사용합니다.
#    MPS를 쓸 수 없으면 CPU로 넘어가지 않고 에러로 멈춥니다.

assert torch.backends.mps.is_available(), "MPS(GPU)를 사용할 수 없습니다."
device = "mps"

# 3. YOLO 모델을 불러옵니다 (사전학습된 yolov8n, 최초 실행 시 자동 다운로드).

model = YOLO("yolov8n.pt")

# 4. 샘플 이미지로 추론하고, 박스가 그려진 결과를 화면에 띄웁니다.

results = model("https://ultralytics.com/images/bus.jpg", device=device)
results[0].show()
