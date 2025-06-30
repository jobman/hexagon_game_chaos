# map_generator.py
import random
from tile_types import TileType
from hex_utils import hex_distance
from constants import MAP_WIDTH, MAP_HEIGHT

def generate_map() -> dict:
    """
    Генерирует карту в виде острова.
    Возвращает словарь: { (q, r): {'tile': TileType} }
    """
    grid = {}
    center_q, center_r = MAP_WIDTH // 2, MAP_HEIGHT // 2
    
    for q in range(MAP_WIDTH):
        for r in range(MAP_HEIGHT):
            # Смещение для гексагональной сетки
            q_offset = q - center_q
            r_offset = r - center_r

            dist = hex_distance((0,0), (q_offset, r_offset))
            radius = min(MAP_WIDTH, MAP_HEIGHT) / 2
            
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
            
            grid[(q_offset, r_offset)] = {'tile': tile}
            
    return grid