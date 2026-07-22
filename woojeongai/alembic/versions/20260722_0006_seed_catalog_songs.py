"""seed catalog_songs with initial Korean/English vocal tracks

Revision ID: 20260722_0006
Revises: 20260714_0005
Create Date: 2026-07-22
"""
from __future__ import annotations

from alembic import op

revision = "20260722_0006"
down_revision = "20260714_0005"
branch_labels = None
depends_on = None

SONGS = [
    ("spring-day",       "봄날",              "방탄소년단",   108, "Db Major",  "중음역 · 감성 발라드",       "봄날 MR (Studio)",              "피아노·스트링 중심 MR. 호흡과 감정선 연습용"),
    ("through-the-night","밤편지",            "아이유",        72,  "G Major",   "저중음역 · 어쿠스틱 발라드", "밤편지 MR (Acoustic)",          "기타·피아노 어쿠스틱 MR. 섬세한 다이내믹 연습"),
    ("defying-gravity",  "Defying Gravity",   "Wicked",       138, "Db Major",  "고음역 · 뮤지컬 넘버",       "Defying Gravity MR (Orchestra)","오케스트라 MR. 고음·벨팅 표현 연습"),
    ("dynamite",         "Dynamite",          "방탄소년단",   114, "C Major",   "중고음역 · 팝 댄스",         "Dynamite MR (Disco Pop)",       "디스코 팝 MR. 리듬·박자 정확도 연습"),
    ("celebrity",        "Celebrity",         "아이유",       120, "G Major",   "중음역 · 팝",                "Celebrity MR (Pop)",            "업템포 팝 MR. 발음 정확도·호흡 연습"),
    ("lilac",            "LILAC",             "아이유",       106, "Ab Major",  "중음역 · 팝 댄스",           "LILAC MR (Dance Pop)",          "댄스 팝 MR. 리듬감·밝은 톤 연습"),
    ("love-poem",        "Love poem",         "아이유",        74, "Bb Major",  "저중음역 · 발라드",          "Love poem MR (Ballad)",         "피아노 발라드 MR. 섬세한 감정 표현 연습"),
    ("palette",          "Palette",           "아이유",        86, "G Major",   "중음역 · 인디 팝",           "Palette MR (Indie Pop)",        "기타 중심 MR. 편안한 중음역 연습"),
    ("on",               "ON",                "방탄소년단",   95,  "Bb minor",  "중고음역 · 파워 팝",         "ON MR (Epic Pop)",              "웅장한 타악기·브라스 MR. 파워 보컬 연습"),
    ("butter",           "Butter",            "방탄소년단",   110, "G Major",   "중음역 · 팝",                "Butter MR (Pop)",               "팝 MR. 가볍고 경쾌한 톤 연습"),
    ("permission-to-dance","Permission to Dance","방탄소년단",128, "D Major",   "중고음역 · 팝 댄스",         "Permission to Dance MR",        "브라스·팝 MR. 리듬·발음 연습"),
    ("subset",           "Subset",            "아이유",        80, "F Major",   "저중음역 · 어쿠스틱",        "Subset MR (Acoustic)",          "미니멀 어쿠스틱 MR. 음정 안정성 연습"),
    ("above-the-time",   "시간의 바깥",       "아이유",        68, "E Major",   "저중음역 · 발라드",          "시간의 바깥 MR (Ballad)",       "현악 중심 MR. 긴 호흡·레가토 연습"),
    ("bts-fake-love",    "FAKE LOVE",         "방탄소년단",   130, "F# minor",  "중고음역 · 힙합 팝",         "FAKE LOVE MR (Hip-hop Pop)",    "어두운 팝 MR. 강약 대비·감정 연습"),
    ("eight",            "에잇 (eight)",      "아이유",       108, "D Major",   "중음역 · 팝",                "에잇 MR (Pop)",                 "밝은 팝 MR. 경쾌한 리듬 연습"),
    ("ending-scene",     "이런 엔딩",         "아이유",        72, "G Major",   "중음역 · 발라드",            "이런 엔딩 MR (Ballad)",         "피아노 발라드 MR. 감정 표현 연습"),
    ("drama",            "Drama",             "aespa",        148, "F minor",   "중고음역 · 팝 댄스",         "Drama MR (Dance Pop)",          "업템포 팝 MR. 빠른 발음·리듬 연습"),
    ("supernova",        "Supernova",         "aespa",        132, "Ab minor",  "중고음역 · 팝 댄스",         "Supernova MR (Dance Pop)",      "강렬한 팝 MR. 파워 보컬·호흡 연습"),
    ("antifragile",      "Antifragile",       "LE SSERAFIM",  126, "G minor",   "중음역 · 팝 댄스",           "Antifragile MR (Dance Pop)",    "댄스 팝 MR. 리듬·발음 정확도 연습"),
    ("fearless",         "FEARLESS",          "LE SSERAFIM",  140, "Bb minor",  "중음역 · 팝 댄스",           "FEARLESS MR (Dance Pop)",       "강렬한 팝 MR. 고음 안정성 연습"),
    ("whiplash",         "Whiplash",          "aespa",        140, "F minor",   "중고음역 · 팝 댄스",         "Whiplash MR (Dance Pop)",       "강렬한 팝 MR. 파워 보컬 연습"),
    ("next-level",       "Next Level",        "aespa",        138, "G minor",   "중고음역 · 팝 댄스",         "Next Level MR (Dance Pop)",     "업템포 팝 MR. 발음·리듬 연습"),
    ("queencard",        "Queencard",         "(G)I-DLE",     120, "G Major",   "중음역 · 팝 댄스",           "Queencard MR (Pop)",            "밝은 팝 MR. 경쾌한 보컬 연습"),
    ("tomboy",           "TOMBOY",            "(G)I-DLE",     140, "F# minor",  "중음역 · 록 팝",             "TOMBOY MR (Rock Pop)",          "록 팝 MR. 강렬한 보컬 연습"),
    ("nxde",             "NXDE",              "(G)I-DLE",     115, "D minor",   "중음역 · 팝",                "NXDE MR (Pop)",                 "팝 MR. 다이내믹 표현 연습"),
    ("zoom",             "ZOOM",              "Jessi",        140, "G minor",   "중음역 · 힙합 팝",           "ZOOM MR (Hip-hop Pop)",         "힙합 팝 MR. 리듬·발음 연습"),
    ("left-right",       "Left & Right",      "세븐틴",       122, "C Major",   "중음역 · 팝 댄스",           "Left & Right MR (Pop Dance)",   "팝 댄스 MR. 리듬·발음 연습"),
    ("any-song",         "아무노래",          "지코",         95,  "F Major",   "중음역 · 팝 힙합",           "아무노래 MR (Pop Hip-hop)",     "팝 힙합 MR. 리듬감 연습"),
    ("celebrity-iu-eng", "Celebrity (Eng)",   "아이유",       120, "G Major",   "중음역 · 팝",                "Celebrity MR (English Ver.)",   "영어 버전 팝 MR. 발음·리듬 연습"),
    ("hype-boy",         "Hype Boy",          "NewJeans",     105, "Bb Major",  "중음역 · 팝",                "Hype Boy MR (Pop)",             "Y2K 팝 MR. 자연스러운 보컬 연습"),
    ("attention",        "Attention",         "NewJeans",     100, "C Major",   "중음역 · 팝",                "Attention MR (Pop)",            "미니멀 팝 MR. 음정 안정성 연습"),
    ("ditto",            "Ditto",             "NewJeans",      92, "F Major",   "저중음역 · 팝",              "Ditto MR (Pop)",                "감성 팝 MR. 섬세한 표현 연습"),
    ("omg",              "OMG",               "NewJeans",     110, "G Major",   "중음역 · 팝",                "OMG MR (Pop)",                  "팝 MR. 리듬·발음 연습"),
    ("supernatural",     "Supernatural",      "NewJeans",     104, "Ab Major",  "중음역 · 팝",                "Supernatural MR (Pop)",         "팝 MR. 자연스러운 보컬 연습"),
    ("seven",            "Seven",             "정국",         120, "F Major",   "중고음역 · 팝",              "Seven MR (Pop)",                "팝 MR. 고음 안정성·리듬 연습"),
    ("standing-next",    "Standing Next to You","정국",       116, "Ab Major",  "중고음역 · 팝 R&B",          "Standing Next to You MR (R&B)", "R&B 팝 MR. 파워 보컬·그루브 연습"),
    ("love-wins-all",    "Love wins all",     "아이유",        76, "F# minor",  "중음역 · 발라드",            "Love wins all MR (Ballad)",     "감성 발라드 MR. 감정 표현 연습"),
    ("holocene",         "Holocene",          "Bon Iver",      76, "D Major",   "저중음역 · 인디 포크",       "Holocene MR (Indie Folk)",      "어쿠스틱 MR. 두성·팔세토 연습"),
    ("someone-like-you", "Someone Like You",  "Adele",         68, "A Major",   "저중음역 · 팝 발라드",       "Someone Like You MR (Piano)",   "피아노 발라드 MR. 강약 조절 연습"),
    ("rolling-in-deep",  "Rolling in the Deep","Adele",       105, "C minor",   "중고음역 · 팝 소울",         "Rolling in the Deep MR (Soul)", "소울 팝 MR. 파워 보컬 연습"),
]


def upgrade() -> None:
    for row in SONGS:
        catalog_song_id, title, artist, bpm, song_key, range_label, mr_track_name, mr_description = row
        op.execute(
            f"""
            INSERT INTO catalog_songs
                (catalog_song_id, title, artist, bpm, song_key, range_label, mr_track_name, mr_description)
            VALUES
                ('{catalog_song_id}', '{title}', '{artist}', {bpm}, '{song_key}',
                 '{range_label}', '{mr_track_name}', '{mr_description}')
            ON CONFLICT (catalog_song_id) DO NOTHING
            """
        )


def downgrade() -> None:
    ids = ", ".join(f"'{row[0]}'" for row in SONGS)
    op.execute(f"DELETE FROM catalog_songs WHERE catalog_song_id IN ({ids})")
