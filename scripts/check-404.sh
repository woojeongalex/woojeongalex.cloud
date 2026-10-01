#!/usr/bin/env bash
# 사이트에 404 가 있는지 훑는다. 배포 뒤에 한 번 돌린다.
#
#   bash scripts/check-404.sh                      # 운영
#   bash scripts/check-404.sh http://localhost:3100 # 로컬
#
# 왜 필요한가: 404 는 대개 화면에 안 보인다. 아이콘 하나, robots.txt 하나가 빠져도
# 페이지는 멀쩡히 그려지고 콘솔에만 남는다. 2026-10-01 에 favicon.ico·robots.txt·
# sitemap.xml·og:image 가 통째로 빠져 있던 것을 이 방식으로 찾았다.

set -uo pipefail
BASE="${1:-https://woojeongalex.cloud}"
BASE="${BASE%/}"
fail=0
pass=0

code() { curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$@"; }

check() {  # check <경로> <기대코드>
  local path="$1" want="${2:-200}" got
  got=$(code "$BASE$path")
  if [ "$got" = "$want" ]; then
    pass=$((pass + 1))
  else
    printf '  ❌ %-44s %s (기대 %s)\n' "$path" "$got" "$want"
    fail=$((fail + 1))
  fi
}

echo "대상: $BASE"
echo
echo "[사람이 여는 화면]"
for p in / /music-challenge /rhythm /analyze /instrument /speech /auth /music-challenge/me; do
  check "$p"
done

echo "[브라우저·크롤러가 말없이 찾는 것]"
# 선언하지 않아도 요청이 오는 경로들. 없으면 조용히 404 가 쌓인다.
for p in /favicon.ico /robots.txt /sitemap.xml; do
  check "$p"
done

echo "[링크 미리보기]"
# og:image 가 없으면 메신저에 주소만 뜬다. 404 는 아니지만 같은 종류의 '빠진 것'이다.
og=$(curl -s --max-time 20 "$BASE/" | grep -oE '<meta[^>]*property="og:image"[^>]*content="[^"]*"' | grep -oE 'content="[^"]*"' | sed 's/content="//;s/"//' | head -1)
if [ -z "$og" ]; then
  echo "  ❌ og:image 메타가 없다 — 링크를 붙여도 미리보기가 안 뜬다"
  fail=$((fail + 1))
else
  got=$(code "$og")
  if [ "$got" = "200" ]; then
    pass=$((pass + 1))
  else
    printf '  ❌ og:image %s → %s\n' "$og" "$got"
    fail=$((fail + 1))
  fi
fi

echo "[각 화면이 선언한 파일]"
# HTML 안의 link/script/img 를 긁어 전부 눌러 본다. 아이콘·폰트·청크가 여기서 걸린다.
for p in / /music-challenge /rhythm; do
  while read -r asset; do
    [ -z "$asset" ] && continue
    case "$asset" in
      http*) url="$asset" ;;
      /*)    url="$BASE$asset" ;;
      *)     continue ;;
    esac
    got=$(code "$url")
    if [ "$got" = "200" ]; then
      pass=$((pass + 1))
    else
      printf '  ❌ %s 에서 %s → %s\n' "$p" "$asset" "$got"
      fail=$((fail + 1))
    fi
  done < <(curl -s --max-time 20 "$BASE$p" \
      | grep -oE '(href|src)="[^"]+\.(css|js|png|svg|ico|webmanifest|woff2?)"' \
      | sed -E 's/^(href|src)="//; s/"$//' | sort -u)
done

echo
echo "결과: ✅ $pass  ❌ $fail"
[ "$fail" = 0 ]
