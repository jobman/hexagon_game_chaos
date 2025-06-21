# map_generator.py
import random
from tile_types import TileType
from hex_utils import hex_distance

def generate_map(radius: int) -> dict:
    """
    Генерирует карту в виде острова.
    Возвращает словарь: { (q, r): {'tile': TileType} }
    """
    grid = {}
    center = (0, 0)
    
    for q in range(-radius, radius + 1):
        for r in range(-radius, radius + 1):
            if abs(q + r) <= radius:
                dist = hex_distance(center, (q, r))
                
                # Логика генерации острова
                if dist > radius * 0.9:
                    tile = TileType.DEEP_WATER
                elif dist > radius * 0.8:
                    tile = TileType.WATER
                elif dist > radius * 0.7:
                    tile = TileType.SAND
                else:
                    # Основной ландшафт с вкраплениями
                    noise = random.random() # Случайное число от 0.0 до 1.0
                    if noise < 0.15:
                        tile = TileType.FOREST
                    elif noise < 0.25:
                        tile = TileType.HILLS
                    else:
                        tile = TileType.GRASS
                
                grid[(q, r)] = {'tile': tile}
                
    return grid