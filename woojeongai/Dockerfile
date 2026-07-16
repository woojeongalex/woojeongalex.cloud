# 1. 가볍고 안정적인 파이썬 3.13 환경을 가져옵니다
FROM python:3.13-slim

# 2. 컨테이너 내부에서 작업할 폴더 지정
WORKDIR /app

# 3. 의존성 패키지 설치 (캐시 최적화를 위해 먼저 복사)
COPY requirements.txt .
# ultralytics가 opencv-python(GUI용, X11 라이브러리 필요)을 끌고 오는데
# 이 슬림 이미지엔 X11이 없다. 서버에는 GUI가 필요 없으니 헤드리스로 교체한다.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y opencv-python \
    && pip install --no-cache-dir opencv-python-headless==4.10.0.84

# 4. 백엔드 폴더 안의 모든 파일(apps, core, main.py 등)을 복사
COPY . .

# 5. FastAPI 서버 실행 (main.py 호출)
CMD ["python", "main.py"]
