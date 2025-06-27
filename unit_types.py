# unit_types.py
from dataclasses import dataclass, field
from enum import Enum, auto
from tile_types import TileType, TILE_PROPERTIES # Импортируем для can_traverse

class Era(Enum):
    """Эпохи развития."""
    ANCIENT = auto()
    CLASSICAL = auto()
    INDUSTRIAL = auto()
    MODERN = auto()
    FUTURE = auto()

class UnitType(Enum):
    """Перечисление всех типов юнитов."""
    # Ancient
    SETTLER = auto()
    WARRIOR = auto()
    ARCHER = auto()
    # Industrial
    RIFLEMAN = auto()
    CANNON = auto()
    # Future
    MECH = auto()
    CYBER_NINJA = auto()

@dataclass
class BaseUnitProperties:
    """Базовые свойства юнита, от которых наследуются все остальные."""
    name: str
    era: Era
    base_hp: int
    base_ap: int  # Action Points (очки действия/передвижения)
    base_attack: int
    can_found_city: bool = False

    def can_traverse(self, tile_type: TileType) -> bool:
        """
        Определяет, может ли юнит пройти по данному типу клетки.
        По умолчанию, нельзя ходить по горам и воде.
        """
        if tile_type in [TileType.MOUNTAINS, TileType.WATER, TileType.DEEP_WATER, TileType.LAVA]:
            return False
        return True

@dataclass
class UnitProperties(BaseUnitProperties):
    """Хранит универсальные, не-визуальные свойства типа юнита."""
    pass # Пока не добавляем специфичных полей, но класс нужен для наследования

# База данных всех свойств для каждого типа юнита
UNIT_PROPERTIES = {
    UnitType.SETTLER: UnitProperties(name="Поселенец", era=Era.ANCIENT, base_hp=5, base_ap=2, base_attack=0, can_found_city=True),
    UnitType.WARRIOR: UnitProperties(name="Воин", era=Era.ANCIENT, base_hp=10, base_ap=2, base_attack=5),
    UnitType.ARCHER: UnitProperties(name="Лучник", era=Era.ANCIENT, base_hp=8, base_ap=2, base_attack=7),
    UnitType.RIFLEMAN: UnitProperties(name="Стрелок", era=Era.INDUSTRIAL, base_hp=15, base_ap=2, base_attack=15),
    UnitType.CANNON: UnitProperties(name="Пушка", era=Era.INDUSTRIAL, base_hp=12, base_ap=1, base_attack=25),
    UnitType.MECH: UnitProperties(name="Боевой мех", era=Era.FUTURE, base_hp=50, base_ap=4, base_attack=40),
    UnitType.CYBER_NINJA: UnitProperties(name="Кибер-ниндзя", era=Era.FUTURE, base_hp=25, base_ap=5, base_attack=30),
}