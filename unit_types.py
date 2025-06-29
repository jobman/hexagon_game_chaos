# unit_types.py
from dataclasses import dataclass, field
from enum import Enum, auto
from tile_types import TileType, TILE_PROPERTIES

class Era(Enum):
    """Эпохи развития."""
    ANCIENT = auto()
    CLASSICAL = auto()
    INDUSTRIAL = auto()
    MODERN = auto()
    FUTURE = auto()

class UnitType(Enum):
    """Перечисление всех типов юнитов."""
    SETTLER = auto()
    WARRIOR = auto()
    ARCHER = auto()
    RIFLEMAN = auto()
    CANNON = auto()
    MECH = auto()
    CYBER_NINJA = auto()

@dataclass
class BaseUnitProperties:
    """Базовые свойства юнита, от которых наследуются все остальные."""
    name: str
    era: Era
    base_hp: int
    max_energy: int  # Максимальный запас энергии
    base_attack: int
    can_found_city: bool = False

    def can_traverse(self, tile_type: TileType) -> bool:
        """Определяет, может ли юнит пройти по данному типу клетки."""
        return tile_type not in [TileType.MOUNTAINS, TileType.WATER, TileType.DEEP_WATER, TileType.LAVA]

@dataclass
class UnitProperties(BaseUnitProperties):
    """Хранит универсальные, не-визуальные свойства типа юнита."""
    pass

# База данных всех свойств для каждого типа юнита
UNIT_PROPERTIES = {
    UnitType.SETTLER: UnitProperties(name="Поселенец", era=Era.ANCIENT, base_hp=5, max_energy=10, base_attack=0, can_found_city=True),
    UnitType.WARRIOR: UnitProperties(name="Воин", era=Era.ANCIENT, base_hp=10, max_energy=10, base_attack=5),
    UnitType.ARCHER: UnitProperties(name="Лучник", era=Era.ANCIENT, base_hp=8, max_energy=12, base_attack=7),
    UnitType.RIFLEMAN: UnitProperties(name="Стрелок", era=Era.INDUSTRIAL, base_hp=15, max_energy=10, base_attack=15),
    UnitType.CANNON: UnitProperties(name="Пушка", era=Era.INDUSTRIAL, base_hp=12, max_energy=8, base_attack=25),
    UnitType.MECH: UnitProperties(name="Боевой мех", era=Era.FUTURE, base_hp=50, max_energy=20, base_attack=40),
    UnitType.CYBER_NINJA: UnitProperties(name="Кибер-ниндзя", era=Era.FUTURE, base_hp=25, max_energy=15, base_attack=30),
}

# Регенерация энергии для разных юнитов по разным типам местности
# Формат: {UnitType: {TileType: energy_gain}}
ENERGY_REGENERATION = {
    unit: {tile: 1 for tile in TileType} for unit in UnitType
}
# Примеры кастомизации:
ENERGY_REGENERATION[UnitType.WARRIOR].update({
    TileType.FOREST: 2,
    TileType.HILLS: 2,
})
ENERGY_REGENERATION[UnitType.ARCHER].update({
    TileType.FOREST: 3,
    TileType.HILLS: 2,
})
ENERGY_REGENERATION[UnitType.CYBER_NINJA].update({
    TileType.FOREST: 2,
    TileType.HILLS: 2,
    TileType.MOUNTAINS: 1, # Могут медленно восстанавливаться в горах
})
ENERGY_REGENERATION[UnitType.MECH].update({
    TileType.LAVA: 5, # Питаются от лавы
})


# Стоимость передвижения для разных юнитов по разным типам местности
# Формат: {UnitType: {TileType: cost}}
MOVEMENT_COSTS = {
    UnitType.WARRIOR: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 2,
        TileType.HILLS: 2,
        TileType.SAND: 2,
        TileType.DESERT: 2,
        TileType.SNOW: 2,
        TileType.SWAMP: 3,
    },
    UnitType.ARCHER: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 1,
        TileType.HILLS: 2,
        TileType.SAND: 2,
        TileType.DESERT: 2,
        TileType.SNOW: 2,
        TileType.SWAMP: 2,
    },
    UnitType.RIFLEMAN: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 1,
        TileType.HILLS: 1,
        TileType.SAND: 1,
        TileType.DESERT: 1,
        TileType.SNOW: 1,
        TileType.SWAMP: 1,
    },
    UnitType.CANNON: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 3,
        TileType.HILLS: 3,
        TileType.SAND: 2,
        TileType.DESERT: 2,
        TileType.SNOW: 2,
        TileType.SWAMP: 3,
    },
    UnitType.MECH: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 1,
        TileType.HILLS: 1,
        TileType.SAND: 1,
        TileType.DESERT: 1,
        TileType.SNOW: 1,
        TileType.SWAMP: 1,
        TileType.LAVA: 2, # Мехи могут ходить по лаве!
    },
    UnitType.CYBER_NINJA: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 1,
        TileType.HILLS: 1,
        TileType.SAND: 1,
        TileType.DESERT: 1,
        TileType.SNOW: 1,
        TileType.SWAMP: 1,
    },
    UnitType.SETTLER: {
        TileType.GRASS: 1,
        TileType.PLAINS: 1,
        TileType.FOREST: 2,
        TileType.HILLS: 2,
        TileType.SAND: 2,
        TileType.DESERT: 2,
        TileType.SNOW: 2,
        TileType.SWAMP: 3,
    },
}

# Переопределение can_traverse для специфичных юнитов
def mech_can_traverse(self, tile_type: TileType) -> bool:
    """Мехи могут ходить везде, кроме глубокой воды."""
    if tile_type in [TileType.DEEP_WATER]:
        return False
    return True

UNIT_PROPERTIES[UnitType.MECH].can_traverse = mech_can_traverse.__get__(UNIT_PROPERTIES[UnitType.MECH])
