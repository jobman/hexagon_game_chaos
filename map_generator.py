# map_generator.py
import random
import math
from perlin_noise import PerlinNoise
from tile_types import TileType
from constants import MAP_WIDTH, MAP_HEIGHT

def offset_to_axial(col: int, row: int) -> tuple[int, int]:
    """Converts odd-q offset coordinates to axial coordinates."""
    q = col
    r = row - (col - (col & 1)) // 2
    return (q, r)

def generate_map() -> dict:
    """
    Generates a rectangular map using offset coordinates for layout,
    but stores them as axial coordinates in the grid.
    This creates a seamless, wrapping world.
    """
    grid = {}
    noise = PerlinNoise(octaves=4, seed=random.randint(1, 100))

    for col in range(MAP_WIDTH):
        for row in range(MAP_HEIGHT):
            # Use a seamless noise function for wrapping maps
            angle = 2 * math.pi * col / MAP_WIDTH
            x1 = math.cos(angle)
            y1 = math.sin(angle)
            x2 = row / MAP_HEIGHT

            noise_val = noise([x1, y1, x2])

            if noise_val > 0.25:
                tile = TileType.HILLS
            elif noise_val > 0.1:
                tile = TileType.FOREST
            elif noise_val > -0.05:
                tile = TileType.GRASS
            elif noise_val > -0.15:
                tile = TileType.SAND
            elif noise_val > -0.3:
                tile = TileType.WATER
            else:
                tile = TileType.DEEP_WATER
            
            axial_coord = offset_to_axial(col, row)
            grid[axial_coord] = {'tile': tile}
            
    return grid