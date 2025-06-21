# tile_types.py
from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class TileData:
    """Хранит универсальные, не-визуальные свойства типа клетки."""
    name: str
    is_passable: bool

class TileType(Enum):
    """Перечисление всех типов клеток."""
    GRASS = auto()
    PLAINS = auto()
    FOREST = auto()
    HILLS = auto()
    MOUNTAINS = auto()
    WATER = auto()
    DEEP_WATER = auto()
    SAND = auto()
    DESERT = auto()
    SNOW = auto()
    ICE = auto()
    SWAMP = auto()
    LAVA = auto()

# База данных универсальных свойств
TILE_PROPERTIES = {
    TileType.GRASS: TileData(name="Трава", is_passable=True),
    TileType.PLAINS: TileData(name="Равнины", is_passable=True),
    TileType.FOREST: TileData(name="Лес", is_passable=True),
    TileType.HILLS: TileData(name="Холмы", is_passable=True),
    TileType.MOUNTAINS: TileData(name="Горы", is_passable=False),
    TileType.WATER: TileData(name="Вода", is_passable=False),
    TileType.DEEP_WATER: TileData(name="Глубокая вода", is_passable=False),
    TileType.SAND: TileData(name="Песок", is_passable=True),
    TileType.DESERT: TileData(name="Пустыня", is_passable=True),
    TileType.SNOW: TileData(name="Снег", is_passable=True),
    TileType.ICE: TileData(name="Лед", is_passable=True),
    TileType.SWAMP: TileData(name="Болото", is_passable=True),
    TileType.LAVA: TileData(name="Лава", is_passable=False),
}