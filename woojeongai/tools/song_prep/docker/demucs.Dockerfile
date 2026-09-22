# 보컬 / 반주 분리 (Demucs htdemucs)
# CPU 전용 PyTorch — 로컬 GPU 는 EXAONE 이 쓰고 있다.
# torch 2.5.x 는 torchaudio.save 가 torchcodec 없이 동작한다(2.9 부터는 필요).
FROM python:3.11-slim
RUN pip install --no-cache-dir torch==2.5.1 torchaudio==2.5.1 --index-url https://download.pytorch.org/whl/cpu \
 && pip install --no-cache-dir demucs==4.0.1 soundfile
WORKDIR /data
ENTRYPOINT ["python", "-m", "demucs"]
