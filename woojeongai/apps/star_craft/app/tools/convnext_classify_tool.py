from __future__ import annotations

import threading
from io import BytesIO

import timm
import torch
from PIL import Image
from timm.data import ImageNetInfo
from torchvision import transforms

from star_craft.domain.value_objects.classification_vo import ClassificationVO

_MODEL_NAME = "convnext_nano"
_TOP_K = 5

_transform = transforms.Compose(
    [
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)

_model_lock = threading.Lock()
_model: torch.nn.Module | None = None
_labels: list[str] | None = None


def _get_model() -> tuple[torch.nn.Module, list[str]]:
    global _model, _labels
    if _model is None:
        with _model_lock:
            if _model is None:
                model = timm.create_model(
                    _MODEL_NAME, pretrained=True, num_classes=1000
                )
                model.eval()
                info = ImageNetInfo()
                _labels = [info.index_to_description(i) for i in range(1000)]
                _model = model
    assert _model is not None
    assert _labels is not None
    return _model, _labels


def classify_image(image_bytes: bytes) -> ClassificationVO:
    model, labels = _get_model()
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    tensor = _transform(image).unsqueeze(0)

    with torch.no_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0]

    top5_probs, top5_indices = torch.topk(probs, k=_TOP_K)
    top5 = [
        (labels[idx], float(prob))
        for prob, idx in zip(top5_probs.tolist(), top5_indices.tolist())
    ]

    return ClassificationVO(label=top5[0][0], confidence=top5[0][1], top5=top5)
