import pygame
from dataclasses import dataclass, field
from tile_types import TileType
from unit_types import UnitType
from constants import (
    COLOR_GRASS, COLOR_WATER, COLOR_MOUNTAIN, COLOR_FOREST, COLOR_SAND,
    COLOR_UNIT_ALLY, COLOR_UNIT_ENEMY, COLOR_HIGHLIGHT, COLOR_FOG
)

# Словарь, который сопоставляет абстрактный тип тайла с конкретным цветом для отрисовки
TILE_COLORS = {
    TileType.GRASS: COLOR_GRASS,
    TileType.PLAINS: (180, 170, 120),
    TileType.FOREST: COLOR_FOREST,
    TileType.HILLS: (120, 130, 100),
    TileType.MOUNTAINS: COLOR_MOUNTAIN,
    TileType.WATER: COLOR_WATER,
    TileType.DEEP_WATER: (40, 80, 150),
    TileType.SAND: COLOR_SAND,
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
    UnitType.WARRIOR: UnitVisualData(shape='circle', color=COLOR_UNIT_ENEMY, symbol='W'),
    UnitType.ARCHER: UnitVisualData(shape='triangle', color=COLOR_UNIT_ENEMY, symbol='A'),
    UnitType.RIFLEMAN: UnitVisualData(shape='circle', color=COLOR_UNIT_ALLY, symbol='R'),
    UnitType.CANNON: UnitVisualData(shape='square', color=(80, 80, 80), symbol='C'),
    UnitType.MECH: UnitVisualData(shape='square', color=(150, 50, 200), symbol='M'),
    UnitType.CYBER_NINJA: UnitVisualData(shape='triangle', color=(100, 180, 250), symbol='N'),
}

DEFAULT_UNIT_VISUAL = UnitVisualData(shape='circle', color=(255, 0, 255), symbol='?')