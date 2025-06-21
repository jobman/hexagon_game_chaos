# frontend_visuals.py
import pygame
from dataclasses import dataclass, field
from tile_types import TileType
from unit_types import UnitType

# Словарь, который сопоставляет абстрактный тип тайла с конкретным цветом для отрисовки
TILE_COLORS = {
    TileType.GRASS: (100, 150, 100),
    TileType.PLAINS: (180, 170, 120),
    TileType.FOREST: (50, 100, 50),
    TileType.HILLS: (120, 130, 100),
    TileType.MOUNTAINS: (100, 100, 100),
    TileType.WATER: (70, 120, 180),
    TileType.DEEP_WATER: (40, 80, 150),
    TileType.SAND: (210, 200, 150),
    TileType.DESERT: (200, 180, 100),
    TileType.SNOW: (220, 220, 220),
    TileType.ICE: (180, 200, 250),
    TileType.SWAMP: (80, 90, 85),
    TileType.LAVA: (200, 80, 20),
}

# Цвет по умолчанию для тайлов, у которых по какой-то причине нет цвета в словаре
# Помогает легко найти ошибку, если мы добавим новый тайл, но забудем задать ему цвет
DEFAULT_TILE_COLOR = (255, 0, 255) # Ярко-розовый

@dataclass
class UnitVisualData:
    """Хранит визуальные свойства юнита для Pygame."""
    shape: str # 'circle', 'square', 'triangle'
    color: tuple[int, int, int]
    symbol: str # Буква или символ для отображения на юните

# Словарь, который сопоставляет абстрактный тип юнита с его внешним видом
UNIT_VISUALS = {
    UnitType.SETTLER: UnitVisualData(shape='square', color=(220, 220, 220), symbol='S'),
    UnitType.WARRIOR: UnitVisualData(shape='circle', color=(200, 50, 50), symbol='W'),
    UnitType.ARCHER: UnitVisualData(shape='triangle', color=(200, 50, 50), symbol='A'),
    UnitType.RIFLEMAN: UnitVisualData(shape='circle', color=(50, 70, 50), symbol='R'),
    UnitType.CANNON: UnitVisualData(shape='square', color=(80, 80, 80), symbol='C'),
    UnitType.MECH: UnitVisualData(shape='square', color=(150, 50, 200), symbol='M'),
    UnitType.CYBER_NINJA: UnitVisualData(shape='triangle', color=(100, 180, 250), symbol='N'),
}

DEFAULT_UNIT_VISUAL = UnitVisualData(shape='circle', color=(255, 0, 255), symbol='?')

CITY_CENTER_COLOR = (255, 255, 150) # Светло-желтый
CITY_NAME_COLOR = (240, 240, 240)