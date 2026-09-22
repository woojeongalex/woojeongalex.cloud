"""리듬 게임 한 판 제출(서버 재채점)과 채보별 랭킹."""

import math
from datetime import datetime

from fastapi import HTTPException

from music_challenge.app.dtos.rhythm_dto import (
    RhythmPlayResult,
    RhythmRankingEntry,
    RhythmStanding,
    SubmitRhythmPlayCommand,
)
from music_challenge.app.ports.input.rhythm_use_case import (
    GetRhythmRankingUseCase,
    SubmitRhythmPlayUseCase,
)
from music_challenge.app.ports.output.challenge_repository_port import (
    ChallengeRepositoryPort,
)
from music_challenge.app.ports.output.rhythm_repository_port import (
    RhythmChartRepositoryPort,
    RhythmPlayRepositoryPort,
    RhythmRankingQueryPort,
)
from music_challenge.app.ports.output.user_lookup_port import UserLookupPort
from music_challenge.domain.entities.chart_entity import ChartStatus
from music_challenge.domain.entities.rhythm_entity import RhythmPlay
from music_challenge.domain.services.rhythm_scoring import Press, score_play
from music_challenge.domain.value_objects.rhythm_vo import RHYTHM_KEYS, RhythmDifficulty

# 노트 수보다 훨씬 많은 입력은 아무 키나 계속 누른 것이다. 이 이상이면 받지 않는다.
_MAX_PRESSES_PER_NOTE = 4
_MIN_PRESS_ALLOWANCE = 200


def _clean_presses(
    presses: list[Press], keys: int, duration: float, note_count: int
) -> list[Press]:
    limit = max(_MIN_PRESS_ALLOWANCE, note_count * _MAX_PRESSES_PER_NOTE)
    if len(presses) > limit:
        raise HTTPException(status_code=422, detail="입력 기록이 너무 많습니다.")
    cleaned: list[Press] = []
    for p in presses:
        if not (0 <= p.lane < keys):
            raise HTTPException(status_code=422, detail="없는 레인의 입력이 있습니다.")
        if not (math.isfinite(p.down) and math.isfinite(p.up)):
            raise HTTPException(status_code=422, detail="입력 시각이 잘못되었습니다.")
        if p.down < -1.0 or p.down > duration + 5.0:
            continue  # 곡 밖의 누름은 판정에 영향이 없으니 버린다
        cleaned.append(Press(lane=p.lane, down=p.down, up=max(p.down, p.up)))
    return cleaned


class SubmitRhythmPlayInteractor(SubmitRhythmPlayUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        rhythm_repo: RhythmChartRepositoryPort,
        play_repo: RhythmPlayRepositoryPort,
        ranking: RhythmRankingQueryPort,
        user_lookup: UserLookupPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._rhythm_repo = rhythm_repo
        self._play_repo = play_repo
        self._ranking = ranking
        self._user_lookup = user_lookup

    async def submit(self, command: SubmitRhythmPlayCommand) -> RhythmPlayResult:
        if command.keys not in RHYTHM_KEYS:
            raise HTTPException(status_code=422, detail="4키 또는 7키만 있습니다.")
        if not await self._challenge_repo.find_by_id(command.challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        chart = await self._rhythm_repo.find(command.challenge_id)
        sheet = chart.sheet(command.keys, command.difficulty) if chart else None
        if chart is None or chart.status != ChartStatus.READY or sheet is None:
            raise HTTPException(status_code=404, detail="채보가 없습니다.")

        presses = _clean_presses(
            command.presses, command.keys, chart.duration or 0.0, len(sheet.notes)
        )
        # 화면 점수는 믿지 않는다. 입력 기록을 같은 규칙으로 다시 계산한다.
        result = score_play(sheet.notes, presses)

        # 클라이언트가 보낸 id 를 믿지 않는다. 검증된 토큰의 username 으로만 찾는다.
        user_id = (
            await self._user_lookup.find_id_by_username(command.username)
            if command.username
            else None
        )
        await self._play_repo.save(
            RhythmPlay(
                id=0,
                challenge_id=command.challenge_id,
                user_id=user_id,
                keys=command.keys,
                difficulty=command.difficulty,
                score=result.score,
                accuracy=result.accuracy,
                max_combo=result.max_combo,
                cool=result.cool,
                good=result.good,
                bad=result.bad,
                miss=result.miss,
                created_at=datetime.utcnow(),
            )
        )
        standing = (
            await self._ranking.my_standing(
                command.challenge_id, command.keys, command.difficulty, user_id
            )
            if user_id
            else None
        )
        return RhythmPlayResult(
            score=result.score,
            accuracy=result.accuracy,
            max_combo=result.max_combo,
            cool=result.cool,
            good=result.good,
            bad=result.bad,
            miss=result.miss,
            rank=standing.rank if standing else None,
            best_score=standing.best_score if standing else None,
            is_personal_best=standing is not None
            and result.score >= standing.best_score,
        )


class GetRhythmRankingInteractor(GetRhythmRankingUseCase):
    def __init__(
        self,
        challenge_repo: ChallengeRepositoryPort,
        ranking: RhythmRankingQueryPort,
        user_lookup: UserLookupPort,
    ) -> None:
        self._challenge_repo = challenge_repo
        self._ranking = ranking
        self._user_lookup = user_lookup

    async def get(
        self,
        challenge_id: int,
        keys: int,
        difficulty: RhythmDifficulty,
        limit: int,
        username: str | None,
    ) -> tuple[list[RhythmRankingEntry], RhythmStanding | None]:
        if not await self._challenge_repo.find_by_id(challenge_id):
            raise HTTPException(status_code=404, detail="챌린지를 찾을 수 없습니다.")
        entries = await self._ranking.ranking(challenge_id, keys, difficulty, limit)
        user_id = (
            await self._user_lookup.find_id_by_username(username) if username else None
        )
        me = (
            await self._ranking.my_standing(challenge_id, keys, difficulty, user_id)
            if user_id
            else None
        )
        return entries, me
