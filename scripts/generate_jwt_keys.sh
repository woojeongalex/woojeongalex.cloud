#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "RSA-2048 키 쌍 생성 중..."
openssl genrsa -out "$ROOT_DIR/jwt_private.pem" 2048
openssl rsa -in "$ROOT_DIR/jwt_private.pem" -pubout -out "$ROOT_DIR/jwt_public.pem"

PRIVATE_B64=$(base64 -w0 "$ROOT_DIR/jwt_private.pem")
PUBLIC_B64=$(base64 -w0 "$ROOT_DIR/jwt_public.pem")

echo ""
echo "=== .env 에 아래 값을 추가하세요 ==="
echo ""
echo "JWT_PRIVATE_KEY=$PRIVATE_B64"
echo "JWT_PUBLIC_KEY=$PUBLIC_B64"
echo ""
echo "PEM 파일은 .gitignore에 등록되어 있습니다."
