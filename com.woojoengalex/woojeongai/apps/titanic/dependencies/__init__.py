"""Titanic 의존성 조립소 — director(실구현)·provider(스텁) 모음."""

from titanic.dependencies.crew_james_provider import get_james_use_case
from titanic.dependencies.crew_walter_provider import get_walter_use_case
from titanic.dependencies.crew_andrews_architect_provider import get_andrews_architect_use_case
from titanic.dependencies.crew_lowe_boat_provider import get_lowe_boat_use_case
from titanic.dependencies.crew_smith_captain_provider import get_smith_captain_use_case
from titanic.dependencies.crew_hartley_violin_provider import get_hartley_violin_use_case
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_train_use_case
from titanic.dependencies.passenger_ruth_survivor_provider import get_ruth_survivor_use_case
from titanic.dependencies.passenger_isidor_couple_provider import get_isidor_couple_use_case
from titanic.dependencies.passenger_cal_tester_provider import get_cal_test_use_case
from titanic.dependencies.passenger_molly_scaler_provider import get_molly_scaler_use_case

__all__ = [
    "get_james_use_case",
    "get_walter_use_case",
    "get_andrews_architect_use_case",
    "get_lowe_boat_use_case",
    "get_smith_captain_use_case",
    "get_hartley_violin_use_case",
    "get_rose_model_use_case",
    "get_jack_train_use_case",
    "get_ruth_survivor_use_case",
    "get_isidor_couple_use_case",
    "get_cal_test_use_case",
    "get_molly_scaler_use_case",
]
