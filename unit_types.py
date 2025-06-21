# unit_types.py
from dataclasses import dataclass, field
from enum import Enum, auto

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
class UnitData:
    """Хранит универсальные, не-визуальные свойства типа юнита."""
    name: str
    era: Era
    base_hp: int
    base_ap: int  # Action Points (очки действия/передвижения)
    base_attack: int
    # Особые способности
    can_found_city: bool = False

# База данных всех свойств для каждого типа юнита
UNIT_PROPERTIES = {
    UnitType.SETTLER: UnitData(name="Поселенец", era=Era.ANCIENT, base_hp=5, base_ap=2, base_attack=0, can_found_city=True),
    UnitType.WARRIOR: UnitData(name="Воин", era=Era.ANCIENT, base_hp=10, base_ap=2, base_attack=5),
    UnitType.ARCHER: UnitData(name="Лучник", era=Era.ANCIENT, base_hp=8, base_ap=2, base_attack=7),
    UnitType.RIFLEMAN: UnitData(name="Стрелок", era=Era.INDUSTRIAL, base_hp=15, base_ap=2, base_attack=15),
    UnitType.CANNON: UnitData(name="Пушка", era=Era.INDUSTRIAL, base_hp=12, base_ap=1, base_attack=25),
    UnitType.MECH: UnitData(name="Боевой мех", era=Era.FUTURE, base_hp=50, base_ap=4, base_attack=40),
    UnitType.CYBER_NINJA: UnitData(name="Кибер-ниндзя", era=Era.FUTURE, base_hp=25, base_ap=5, base_attack=30),
}