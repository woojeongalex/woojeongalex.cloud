# 1. 가볍고 안정적인 파이썬 3.13 환경을 가져옵니다
FROM python:3.13-slim

# 2. 컨테이너 내부에서 작업할 폴더 지정
WORKDIR /app

# 3. OCR 엔진 설치 (pytesseract는 이 바이너리를 호출한다)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr tesseract-ocr-kor tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# 4. 의존성 패키지 설치 (캐시 최적화를 위해 먼저 복사)
COPY requirements.txt .
# 전에는 여기서 opencv 를 헤드리스 판으로 바꿔 끼웠다. ultralytics 가 GUI 판을
# 끌고 오는데 이 슬림 이미지엔 X11 이 없어서였다. ultralytics 를 걷어내면서
# opencv 자체가 안 들어오므로 그 줄도 같이 지웠다 —
# 남겨 두면 `pip uninstall` 이 없는 패키지를 지우려다 빌드가 죽는다.
RUN pip install --no-cache-dir -r requirements.txt

# 5. ffmpeg — 올라온 음원을 재생용 MP3 로 줄인다. 무압축 WAV 를 그대로
#    내려보내면 4분짜리 곡이 40MB 라 LTE 에서 곡 시작까지 십몇 초가 걸린다.
#
#    위 apt 줄에 끼워 넣지 않고 굳이 따로 두는 이유: 그 줄을 건드리면 뒤따르는
#    pip 레이어(6.5GB, torch 등)까지 전부 다시 받는다. RAM 912MB·디스크 30GB
#    인 운영 서버에서 그러다 디스크가 100% 차서 빌드가 죽었다. 이 자리에 두면
#    기존 레이어를 그대로 쓰고 100MB 남짓만 더 얹는다.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 4. 백엔드 폴더 안의 모든 파일(apps, core, main.py 등)을 복사
COPY . .

# 5. FastAPI 서버 실행 (main.py 호출)
CMD ["python", "main.py"]
