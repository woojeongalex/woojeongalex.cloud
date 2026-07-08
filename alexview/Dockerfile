# 1. Next.js를 실행할 노드(Node.js) 환경을 가져옵니다
FROM node:24-alpine

# 2. pnpm 활성화
RUN corepack enable && corepack prepare pnpm@latest --activate

# 3. 컨테이너 내부 작업 폴더 지정
WORKDIR /app

# 4. 라이브러리 설치 파일 먼저 복사 후 설치
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# 5. Next.js 소스 코드 전체 복사
COPY . .

# 6. 프로덕션용 빌드 및 Next.js 서버 가동 (3000포트)
RUN pnpm run build
CMD ["pnpm", "run", "start"]
