# 리듬 게임 (오투잼식 떨어지는 노트)

원곡(보컬+반주가 섞인 완성곡) 하나로 채보 6개(4키·7키 × 쉬움·보통·어려움)를 자동으로 만든다.
스템·가사는 필요 없다. 노래방 모드(`challenge_charts`)와는 테이블·API 가 따로다.

## 흐름

```
[관리자] 스튜디오 "채보 만들기" → POST /challenges/{id}/rhythm/build (202)
[백엔드] 원곡 S3 다운로드 → librosa 분석(10~20초) → 채보 6개 → rhythm_charts
[브라우저] 헤더 "리듬 게임" → /rhythm (GET /rhythm/songs: 채보 있는 곡 목록) → /rhythm/{id}
           GET /challenges/{id}/rhythm/{keys}/{difficulty} → 노트 [time, lane, end|null]
           키보드(4키 방향키 ← ↓ ↑ → / 7키 A S D Space J K L)·터치 → 입력 기록 [lane, down, up]
[백엔드] POST /rhythm/{keys}/{difficulty}/plays → 같은 규칙으로 다시 채점 → rhythm_plays
```

## 코드 위치 (apps/music_challenge)

| 층 | 파일 | 역할 |
|:--|:--|:--|
| domain | `value_objects/rhythm_vo.py` | 노트·소리 시작 순간(Onset)·분석 결과·채보 |
| domain | `services/rhythm_pattern.py` | 분석 결과 → 채보. 박자 격자 맞춤, 밀도, 레인, 롱노트, 동시치기. 난수 없음 |
| domain | `services/rhythm_scoring.py` | 판정·점수. `alexview/lib/rhythm-scoring.ts` 와 **같은 규칙** |
| adapter | `outbound/librosa_rhythm_analyzer_adapter.py` | 박자(beat_track), onset, HPSS 크로마(음이름), 소리 길이 |
| app | `use_cases/rhythm_chart_interactors.py` | 조회·생성 요청·백그라운드 생성(job_id 로 늦게 끝난 옛 작업 버림) |
| app | `use_cases/rhythm_play_interactors.py` | 제출(입력 검증 + 재채점)·랭킹 |
| adapter | `outbound/pg/rhythm_pg_repository.py` | 저장소 + 채보별 랭킹 SQL(`DISTINCT ON` + `RANK()`) |
| migration | `alembic/versions/20260922_0014_rhythm_game.py` | `rhythm_charts`, `rhythm_plays` |

## 판정 규칙 (서버·브라우저 공통)

- 판정 창: ±75ms COOL, ±130ms GOOD, ±185ms BAD, 밖이면 MISS. 빈 누름은 벌점 없음
  (2026-09-22 에 45/90/135 → 60/110/160, 2026-09-28 에 다시 75/130/185 로 넓혔다)
- 롱노트: 머리·꼬리 따로. 끝까지 누르면 꼬리 COOL, 일찍 떼면 그만큼 낮음. 머리를 놓치면 꼬리도 MISS
- 콤보는 BAD·MISS 에서 끊김
- 점수(최대 1,000,000) = 900,000 × 정확도 + 100,000 × 최대 콤보 / 판정 수,
  정확도 = (COOL + 0.6·GOOD + 0.2·BAD) / 판정 수
- 반올림은 JS `Math.round` 와 같게 `floor(x + 0.5)`
- 한쪽을 고치면 반드시 둘 다 고친다. 2026-09-22 무작위 입력 20판으로 두 구현의 결과가 모두 같음을 확인했다

## 채보 생성 규칙 요약

| 키·난이도 | 격자 | 최소 간격 | 초당 노트 | 롱노트 | 동시치기 |
|:--|:--|:--|:--|:--|:--|
| 4키 쉬움 / 7키 쉬움 | 정박(4분) | 1박 | 0.8 / 1.0 | 다음 노트 전에 끝남 | 없음 |
| 4키 보통 / 7키 보통 | 8분 | 0.5박 | 1.5 / 2.0 | 누르는 동안 다른 레인 노트 있음(동시 1개) | 없음 |
| 4키 어려움 / 7키 어려움 | 16분 | 0.5박 | 2.6 / 3.2 | 동시 1개 | 정박의 센 순간 (2% / 3%) |

- 세기는 주변 ±4초 안에서 상대값이라 조용한 구간에도 노트가 남는다
- 레인은 음이름을 곡 안 순위로 바꿔 배치(같은 음은 같은 쪽). 같은 레인을 0.4초 안에 다시 치게 되면 옆 레인으로 옮긴다
- 어려움은 격자가 16분이라 엇박에 노트가 놓일 수 있지만, 최소 간격이 0.5박이라 16분 연타는 나오지 않는다
- 2026-09-22 "너무 어려워" 피드백으로 밀도·동시치기를 낮추고 판정 창을 넓혔다
- 2026-09-28 한 번 더 낮췄다. 밀도 약 −25%, 어려움 최소 간격 0.25박 → 0.5박,
  보통의 동시치기 제거, 어려움 동시치기 비율 축소(7키 세 개 동시는 세기 0.99 이상만)
- 곡 #6·#7·#8 기준(9/22 프로필로 만든 채보): 쉬움 Lv.4~6, 보통 Lv.8~12, 어려움 Lv.10~15.
  9/28 프로필은 합성 분석(180초·100BPM)에서 Lv 가 2~4 낮게 나왔다 — 실제 곡은 다시 만들어 봐야 안다
- **프로필을 바꿔도 이미 저장된 채보는 그대로다.** 곡마다
  `POST /api/v1/challenges/{id}/rhythm/build`(admin) 로 다시 만들어야 새 규칙이 적용된다.
  다시 만드는 동안에도 이전 채보로 플레이는 계속된다. 판정 창은 저장물이 아니라 실행 규칙이라
  다시 만들지 않아도 바로 적용된다

## 알려진 한계

- 입력 기록은 브라우저가 만든다. 채보(GET)로 "완벽한 입력"을 합성해 보내면 막을 수 없다(노래방 모드와 같은 한계)
- 싱크 보정은 사용자가 설정(±300ms). 기기별 자동 보정은 없다
- 로그인 토큰이 만료된 채 제출하면 `authFetch` 가 먼저 갱신을 시도한다. 갱신도 실패하면 익명 기록으로 저장된다
