from sqlalchemy.ext.asyncio import AsyncSession

from music_challenge.adapter.outbound.librosa_rhythm_analyzer_adapter import (
    LibrosaRhythmAnalyzerAdapter,
)
from music_challenge.adapter.outbound.pg.rhythm_pg_repository import (
    RhythmChartPgRepository,
    RhythmPlayPgRepository,
    RhythmRankingPgQuery,
)
from music_challenge.app.ports.input.rhythm_use_case import (
    BuildRhythmChartUseCase,
    GetRhythmChartUseCase,
    GetRhythmRankingUseCase,
    RequestRhythmBuildUseCase,
    SubmitRhythmPlayUseCase,
)
from music_challenge.app.use_cases.rhythm_chart_interactors import (
    BuildRhythmChartInteractor,
    GetRhythmChartInteractor,
    RequestRhythmBuildInteractor,
)
from music_challenge.app.use_cases.rhythm_play_interactors import (
    GetRhythmRankingInteractor,
    SubmitRhythmPlayInteractor,
)

from music_challenge.adapter.outbound.gemini_evaluator_adapter import (
    GeminiEvaluatorAdapter,
)
from music_challenge.adapter.outbound.librosa_audio_analysis_adapter import (
    LibrosaAudioAnalysisAdapter,
)
from music_challenge.adapter.outbound.librosa_melody_extractor_adapter import (
    LibrosaMelodyExtractorAdapter,
    LibrosaPitchTrackerAdapter,
)
from music_challenge.adapter.outbound.pg.challenge_pg_repository import (
    ChallengePgRepository,
)
from music_challenge.adapter.outbound.pg.chart_pg_repository import ChartPgRepository
from music_challenge.adapter.outbound.pg.evaluation_pg_repository import (
    EvaluationPgRepository,
)
from music_challenge.adapter.outbound.pg.ranking_pg_query import RankingPgQuery
from music_challenge.adapter.outbound.pg.submission_pg_repository import (
    SubmissionPgRepository,
)
from music_challenge.adapter.outbound.pg.user_lookup_pg_repository import (
    UserLookupPgRepository,
)
from music_challenge.adapter.outbound.s3_media_storage_adapter import (
    S3MediaStorageAdapter,
)
from music_challenge.app.ports.input.challenge_use_case import (
    CreateChallengeUseCase,
    GetChallengeUseCase,
    ListChallengesUseCase,
)
from music_challenge.app.ports.input.chart_use_case import (
    BuildChartUseCase,
    GetChartUseCase,
    UpdateLyricsUseCase,
    UploadStemsUseCase,
)
from music_challenge.app.ports.input.history_use_case import GetMyHistoryUseCase
from music_challenge.app.ports.input.ranking_use_case import (
    GetChallengeRankingUseCase,
    GetWeeklyRankingUseCase,
)
from music_challenge.app.ports.input.submission_use_case import SubmitChallengeUseCase
from music_challenge.app.use_cases.build_chart_interactor import BuildChartInteractor
from music_challenge.app.use_cases.create_challenge_interactor import (
    CreateChallengeInteractor,
)
from music_challenge.app.use_cases.get_challenge_interactor import (
    GetChallengeInteractor,
)
from music_challenge.app.use_cases.get_challenge_ranking_interactor import (
    GetChallengeRankingInteractor,
)
from music_challenge.app.use_cases.get_chart_interactor import GetChartInteractor
from music_challenge.app.use_cases.get_my_history_interactor import (
    GetMyHistoryInteractor,
)
from music_challenge.app.use_cases.get_weekly_ranking_interactor import (
    GetWeeklyRankingInteractor,
)
from music_challenge.app.use_cases.list_challenges_interactor import (
    ListChallengesInteractor,
)
from music_challenge.app.use_cases.submit_challenge_interactor import (
    SubmitChallengeInteractor,
)
from music_challenge.app.use_cases.update_lyrics_interactor import (
    UpdateLyricsInteractor,
)
from music_challenge.app.use_cases.upload_stems_interactor import (
    UploadStemsInteractor,
)


def get_create_challenge_use_case(session: AsyncSession) -> CreateChallengeUseCase:
    return CreateChallengeInteractor(
        challenge_repo=ChallengePgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_list_challenges_use_case(session: AsyncSession) -> ListChallengesUseCase:
    return ListChallengesInteractor(
        challenge_repo=ChallengePgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_challenge_use_case(session: AsyncSession) -> GetChallengeUseCase:
    return GetChallengeInteractor(
        challenge_repo=ChallengePgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_submit_challenge_use_case(session: AsyncSession) -> SubmitChallengeUseCase:
    return SubmitChallengeInteractor(
        challenge_repo=ChallengePgRepository(session),
        submission_repo=SubmissionPgRepository(session),
        evaluation_repo=EvaluationPgRepository(session),
        storage=S3MediaStorageAdapter(),
        evaluator=GeminiEvaluatorAdapter(),
        user_lookup=UserLookupPgRepository(session),
        audio_analysis=LibrosaAudioAnalysisAdapter(),
        chart_repo=ChartPgRepository(session),
        pitch_tracker=LibrosaPitchTrackerAdapter(),
        ranking=RankingPgQuery(session),
    )


def get_my_history_use_case(session: AsyncSession) -> GetMyHistoryUseCase:
    return GetMyHistoryInteractor(
        submission_repo=SubmissionPgRepository(session),
        user_lookup=UserLookupPgRepository(session),
    )


def get_chart_use_case(session: AsyncSession) -> GetChartUseCase:
    return GetChartInteractor(
        challenge_repo=ChallengePgRepository(session),
        chart_repo=ChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_upload_stems_use_case(session: AsyncSession) -> UploadStemsUseCase:
    return UploadStemsInteractor(
        challenge_repo=ChallengePgRepository(session),
        chart_repo=ChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_build_chart_use_case(session: AsyncSession) -> BuildChartUseCase:
    return BuildChartInteractor(
        chart_repo=ChartPgRepository(session),
        extractor=LibrosaMelodyExtractorAdapter(),
    )


def get_update_lyrics_use_case(session: AsyncSession) -> UpdateLyricsUseCase:
    return UpdateLyricsInteractor(
        challenge_repo=ChallengePgRepository(session),
        chart_repo=ChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_challenge_ranking_use_case(session: AsyncSession) -> GetChallengeRankingUseCase:
    return GetChallengeRankingInteractor(
        challenge_repo=ChallengePgRepository(session),
        ranking=RankingPgQuery(session),
        user_lookup=UserLookupPgRepository(session),
    )


def get_weekly_ranking_use_case(session: AsyncSession) -> GetWeeklyRankingUseCase:
    return GetWeeklyRankingInteractor(ranking=RankingPgQuery(session))


def get_rhythm_chart_use_case(session: AsyncSession) -> GetRhythmChartUseCase:
    return GetRhythmChartInteractor(
        challenge_repo=ChallengePgRepository(session),
        rhythm_repo=RhythmChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_request_rhythm_build_use_case(
    session: AsyncSession,
) -> RequestRhythmBuildUseCase:
    return RequestRhythmBuildInteractor(
        challenge_repo=ChallengePgRepository(session),
        rhythm_repo=RhythmChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
    )


def get_build_rhythm_chart_use_case(session: AsyncSession) -> BuildRhythmChartUseCase:
    return BuildRhythmChartInteractor(
        rhythm_repo=RhythmChartPgRepository(session),
        storage=S3MediaStorageAdapter(),
        analyzer=LibrosaRhythmAnalyzerAdapter(),
    )


def get_submit_rhythm_play_use_case(session: AsyncSession) -> SubmitRhythmPlayUseCase:
    return SubmitRhythmPlayInteractor(
        challenge_repo=ChallengePgRepository(session),
        rhythm_repo=RhythmChartPgRepository(session),
        play_repo=RhythmPlayPgRepository(session),
        ranking=RhythmRankingPgQuery(session),
        user_lookup=UserLookupPgRepository(session),
    )


def get_rhythm_ranking_use_case(session: AsyncSession) -> GetRhythmRankingUseCase:
    return GetRhythmRankingInteractor(
        challenge_repo=ChallengePgRepository(session),
        ranking=RhythmRankingPgQuery(session),
        user_lookup=UserLookupPgRepository(session),
    )
