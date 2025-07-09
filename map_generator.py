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

def _get_tile_type(elevation: float, moisture: float) -> TileType:
    """Determines the tile type based on elevation and moisture values."""
    if elevation < 0.1:
        return TileType.DEEP_WATER
    if elevation < 0.25:
        return TileType.WATER
    if elevation < 0.35:
        return TileType.SAND

    if elevation > 0.8:
        if moisture < 0.5:
            return TileType.MOUNTAINS
        else:
            return TileType.SNOW

    if elevation > 0.7:
        return TileType.HILLS

    if moisture < 0.2:
        return TileType.DESERT
    if moisture < 0.4:
        return TileType.PLAINS
    if moisture > 0.75:
        return TileType.SWAMP
    if moisture > 0.6:
        return TileType.FOREST

    return TileType.GRASS

def generate_map() -> dict:
    """
    Generates a rectangular map using layered Perlin noise for elevation and moisture
    to create fractal-like biome distributions.
    The map is seamless and wraps around.
    """
    grid = {}
    seed = random.randint(1, 1000)
    elevation_noise = PerlinNoise(octaves=8, seed=seed)
    moisture_noise = PerlinNoise(octaves=6, seed=seed + 1)

    # Adjust frequency of the noise to control the size of features
    elevation_freq = 3.0
    moisture_freq = 4.0

    for col in range(MAP_WIDTH):
        for row in range(MAP_HEIGHT):
            # Use a seamless noise function for wrapping maps
            # By mapping coordinates to a circle/cylinder
            angle = 2 * math.pi * col / MAP_WIDTH
            x1 = math.cos(angle)
            y1 = math.sin(angle)
            
            # Use different coordinates for the noise functions to get varied patterns
            elevation_val = elevation_noise([x1 * elevation_freq, y1 * elevation_freq, row / MAP_HEIGHT * elevation_freq])
            moisture_val = moisture_noise([x1 * moisture_freq, y1 * moisture_freq, row / MAP_HEIGHT * moisture_freq])

            # Normalize values to be roughly between 0 and 1
            elevation_val = (elevation_val + 1) / 2
            moisture_val = (moisture_val + 1) / 2

            tile = _get_tile_type(elevation_val, moisture_val)
            
            axial_coord = offset_to_axial(col, row)
            grid[axial_coord] = {'tile': tile}
            
    return grid