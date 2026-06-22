from constants import (
    CAMPUS_DURATION,
    CAMPUS_TARGET_TASKS,
    FINALS_DURATION,
    TRANSITION_DURATION,
)


def test_production_game_configuration() -> None:
    """Evita confirmar accidentalmente valores usados para pruebas rápidas."""

    assert CAMPUS_DURATION == 120.0
    assert CAMPUS_TARGET_TASKS == 15
    assert TRANSITION_DURATION == 3.0
    assert FINALS_DURATION == 150.0
