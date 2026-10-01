#!/usr/bin/env bash
# 개발 기록 사이트를 EC2 nginx 에 올린다 — demo.woojeongalex.cloud
#
#   jekyll/scripts/deploy.sh            # 빌드 + 업로드 + nginx 설정
#
# 필요한 것: Docker(빌드용), EC2 SSH 키. 키·호스트는 환경변수로 바꿀 수 있다.
# HTTPS 인증서는 처음 한 번만 EC2 에서 발급한다(아래 마지막 안내 참고).
set -euo pipefail

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${DEPLOY_HOST:-ec2-user@<EC2_IP>}"
KEY="${DEPLOY_KEY:-$HOME/.ssh/<키파일>}"
DOMAIN="${DEPLOY_DOMAIN:-demo.woojeongalex.cloud}"
REMOTE_DIR="/home/ec2-user/demo-site"
SSH=(ssh -o BatchMode=yes -i "$KEY" "$HOST")

echo "[deploy] 1/4 개발 로그 갱신 · 빌드"
python3 "$SITE_DIR/scripts/build_devlog.py"
# 이전 빌드 파일은 컨테이너(root)가 만들어 호스트 사용자가 못 지울 수 있다 — 컨테이너 안에서 지운다.
docker run --rm -v "$SITE_DIR:/site" -v iuem-jekyll-gems:/usr/local/bundle -w /site \
  -e JEKYLL_ENV=production ruby:3.3 \
  bash -c "rm -rf /site/_site_prod && bundle install --quiet && bundle exec jekyll build --destination /site/_site_prod"

echo "[deploy] 2/4 업로드 → $HOST:$REMOTE_DIR"
# 새 폴더에 받은 뒤 한 번에 바꿔서, 업로드 중에 반쯤 바뀐 사이트가 보이지 않게 한다.
tar -C "$SITE_DIR/_site_prod" -czf - . | "${SSH[@]}" "
  set -e
  rm -rf $REMOTE_DIR.new && mkdir -p $REMOTE_DIR.new
  tar -xzf - -C $REMOTE_DIR.new
  # nginx 가 읽을 수 있어야 한다 — 권한이 없으면 403 이 난다.
  chmod -R a+rX $REMOTE_DIR.new
  rm -rf $REMOTE_DIR.old
  [ -d $REMOTE_DIR ] && mv $REMOTE_DIR $REMOTE_DIR.old
  mv $REMOTE_DIR.new $REMOTE_DIR
"

echo "[deploy] 3/4 nginx 설정"
# 이미 certbot 이 HTTPS 를 붙였으면 설정을 덮어쓰지 않는다.
if "${SSH[@]}" "sudo grep -q 'managed by Certbot' /etc/nginx/conf.d/demo-site.conf 2>/dev/null"; then
  echo "  HTTPS 설정이 이미 있어 그대로 둡니다"
else
  "${SSH[@]}" "sudo tee /etc/nginx/conf.d/demo-site.conf >/dev/null" <<NGINX
server {
    listen 80;
    server_name $DOMAIN;

    root $REMOTE_DIR;
    index index.html;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;
    gzip_min_length 256;

    # 페이지 파일 이름이 배포마다 같으므로 장기 캐시를 걸면 새 글이 보이지 않는다.
    location / {
        try_files \$uri \$uri/ =404;
        add_header Cache-Control "no-cache, must-revalidate";
    }
}
NGINX
fi
"${SSH[@]}" "sudo nginx -t && sudo systemctl reload nginx"

echo "[deploy] 4/4 확인"
"${SSH[@]}" "curl -s -o /dev/null -w '  EC2 안에서 %{http_code}\n' -H 'Host: $DOMAIN' http://127.0.0.1/problems/"
echo
echo "완료. HTTPS 가 아직 없으면 DNS 를 EC2 로 연결한 뒤 EC2 에서 한 번:"
echo "  sudo certbot --nginx -d $DOMAIN"
