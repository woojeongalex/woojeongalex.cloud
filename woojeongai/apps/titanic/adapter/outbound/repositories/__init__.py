"""Repository — v1 라우터·output Port와 1:1 (*_repository)."""

from titanic.adapter.outbound.repositories.crew_andrews_architect_repository import (
    AndrewsArchitectRepository,
)
from titanic.adapter.outbound.repositories.passenger_cal_tester_repository import CalTestRepository
from titanic.adapter.outbound.repositories.crew_hartley_violin_repository import HartleyViolinRepository
from titanic.adapter.outbound.repositories.passenger_isidor_couple_repository import IsidorCoupleRepository
from titanic.adapter.outbound.repositories.passenger_jack_trainer_repository import JackTrainerRepository
from titanic.adapter.outbound.repositories.crew_james_repository import JamesRepository
from titanic.adapter.outbound.repositories.crew_lowe_boat_repository import LoweBoatRepository
from titanic.adapter.outbound.repositories.passenger_molly_scaler_repository import MollyScalerRepository
from titanic.adapter.outbound.repositories.passenger_rose_model_repository import RoseModelRepository
from titanic.adapter.outbound.repositories.passenger_ruth_survivor_repository import RuthSurvivorRepository
from titanic.adapter.outbound.repositories.crew_smith_captain_repository import SmithCaptainRepository
from titanic.adapter.outbound.repositories.crew_walter_repository import WalterRepository

__all__ = [
    "JamesRepository",
    "WalterRepository",
    "RoseModelRepository",
    "AndrewsArchitectRepository",
    "JackTrainerRepository",
    "RuthSurvivorRepository",
    "IsidorCoupleRepository",
    "SmithCaptainRepository",
    "HartleyViolinRepository",
    "CalTestRepository",
    "LoweBoatRepository",
    "MollyScalerRepository",
]
