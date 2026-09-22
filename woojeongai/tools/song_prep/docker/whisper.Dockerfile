# 가사 줄 타이밍용 음성 인식 (faster-whisper). CTranslate2 라 PyTorch 가 필요 없다.
# faster-whisper 1.1.1 은 requests 의존성을 선언하지 않아 따로 넣는다.
FROM python:3.11-slim
RUN pip install --no-cache-dir faster-whisper==1.1.1 requests
WORKDIR /data
ENTRYPOINT ["python"]
