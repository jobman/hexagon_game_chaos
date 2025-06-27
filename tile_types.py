# tile_types.py
from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class TileData:
    """Хранит универсальные, не-визуальные свойства типа клетки."""
    name: str

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
    TileType.GRASS: TileData(name="Трава"),
    TileType.PLAINS: TileData(name="Равнины"),
    TileType.FOREST: TileData(name="Лес"),
    TileType.HILLS: TileData(name="Холмы"),
    TileType.MOUNTAINS: TileData(name="Горы"),
    TileType.WATER: TileData(name="Вода"),
    TileType.DEEP_WATER: TileData(name="Глубокая вода"),
    TileType.SAND: TileData(name="Песок"),
    TileType.DESERT: TileData(name="Пустыня"),
    TileType.SNOW: TileData(name="Снег"),
    TileType.ICE: TileData(name="Лед"),
    TileType.SWAMP: TileData(name="Болото"),
    TileType.LAVA: TileData(name="Лава"),
}