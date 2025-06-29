# events.py
from dataclasses import dataclass
from enum import Enum, auto


class EventType(Enum):
    """Типы событий в игре."""

    GAME_STARTED = auto()
    TURN_ENDED = auto()
    UNIT_MOVED = auto()
    UNIT_CREATED = auto()
    CITY_FOUNDED = auto()
    NEXT_PLAYER_TURN = auto()


@dataclass
class Event:
    """Структура одного игрового события."""

    type: EventType
    data: dict = None
