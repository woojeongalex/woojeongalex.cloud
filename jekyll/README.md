# IUEM 개발 기록 사이트 (Jekyll)

Just the Docs 테마. 로컬 미리보기는 Docker 로 한다(Ruby 설치 불필요).

```bash
# jekyll/ 에서
docker run --rm -p 4000:4000 -v "$PWD:/site" -w /site ruby:3.3 \
  bash -c "bundle install && bundle exec jekyll serve --host 0.0.0.0"
```

개발 로그(`devlog.md`)는 git 이력에서 만든다: `python3 scripts/build_devlog.py`
