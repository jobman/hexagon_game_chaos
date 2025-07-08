# map_generator.py
import random
from perlin_noise import PerlinNoise
from tile_types import TileType
from hex_utils import hex_distance
from constants import MAP_WIDTH, MAP_HEIGHT

def generate_map() -> dict:
    """
    Генерирует прямоугольную карту с использованием шума Перлина.
    Возвращает словарь: { (q, r): {'tile': TileType} }
    """
    grid = {}
    
    # Инициализация шума Перлина для создания континентов
    noise = PerlinNoise(octaves=4, seed=random.randint(1, 100))
    
    for q in range(MAP_WIDTH):
        for r in range(MAP_HEIGHT):
            # Используем q, r напрямую для прямоугольной карты
            
            # Генерация ландшафта с помощью шума Перлина
            # Масштабируем координаты для получения более крупных и плавных форм
            noise_val = noise([q / (MAP_WIDTH * 0.5), r / (MAP_HEIGHT * 0.5)])
            
            # Применяем радиальный градиент, чтобы в центре было больше суши
            # Это создаст ощущение "мира" с океанами по краям, но карта все равно будет зациклена
            center_q, center_r = MAP_WIDTH / 2, MAP_HEIGHT / 2
            dist_q = abs(q - center_q)
            dist_r = abs(r - center_r)
            # Мы не используем hex_distance, так как нам нужен градиент для прямоугольной области
            dist_normalized = max(dist_q / center_q, dist_r / center_r)
            
            # Уменьшаем значение шума к краям карты, чтобы создать океаны
            noise_val -= dist_normalized * 0.6

            if noise_val > 0.3:
                tile = TileType.HILLS
            elif noise_val > 0.15:
                tile = TileType.FOREST
            elif noise_val > 0:
                tile = TileType.GRASS
            elif noise_val > -0.15:
                tile = TileType.SAND
            elif noise_val > -0.3:
                tile = TileType.WATER
            else:
                tile = TileType.DEEP_WATER
            
            grid[(q, r)] = {'tile': tile}
            
    return grid