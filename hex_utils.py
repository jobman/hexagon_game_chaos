# hex_utils.py
from typing import Tuple
from constants import MAP_WIDTH

Hex = Tuple[int, int]

# Axial coordinates are used for all game logic (pathfinding, distances, etc.)
HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1), 
    (-1, 0), (-1, 1), (0, 1)
]

def hex_add(hex1: Hex, hex2: Hex) -> Hex:
    return (hex1[0] + hex2[0], hex1[1] + hex2[1])

def hex_subtract(hex1: Hex, hex2: Hex) -> Hex:
    return (hex1[0] - hex2[0], hex1[1] - hex2[1])

def hex_distance(hex1: Hex, hex2: Hex) -> int:
    """Calculates the distance between two hexes in axial coordinates."""
    vec = hex_subtract(hex1, hex2)
    return (abs(vec[0]) + abs(vec[1]) + abs(vec[0] + vec[1])) // 2

def hex_neighbors(h: Hex) -> list[Hex]:
    """Gets the 6 neighbors of a hex in axial coordinates."""
    return [hex_add(h, direction) for direction in HEX_DIRECTIONS]

def wrapped_hex_distance(hex1: Hex, hex2: Hex) -> int:
    """Calculates the shortest distance between two hexes on a wrapping map."""
    # Direct distance
    dist = hex_distance(hex1, hex2)
    
    # Distance when wrapping across the map edge
    # We check wrapping in both directions (e.g., hex2 is to the left or right)
    dist_wrap_pos = hex_distance(hex1, (hex2[0] + MAP_WIDTH, hex2[1]))
    dist_wrap_neg = hex_distance(hex1, (hex2[0] - MAP_WIDTH, hex2[1]))
    
    return min(dist, dist_wrap_pos, dist_wrap_neg)


# Для интерполяции и рисования линий
def _lerp(a, b, t):
    return a + (b - a) * t

def _hex_lerp(a, b, t):
    """Линейная интерполяция для гекс-координат."""
    q = _lerp(a[0], b[0], t)
    r = _lerp(a[1], b[1], t)
    return q, r

def hex_linedraw(a, b):
    """Возвращает все гексы на линии между a и b."""
    dist = hex_distance(a, b)
    if dist == 0:
        return [a]
        
    results = []
    # +0.000001 чтобы избежать проблем с точностью на концах отрезка
    step = 1.0 / (dist + 0.000001) 
    
    for i in range(dist + 1):
        q, r = _hex_lerp(a, b, step * i)
        # Округляем до ближайшего гекса (алгоритм из frontend)
        s = -q - r
        rq, rr, rs = round(q), round(r), round(s)
        q_diff, r_diff, s_diff = abs(rq - q), abs(rr - r), abs(rs - s)

        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
            
        results.append((int(rq), int(rr)))
        
    return list(dict.fromkeys(results)) # Удаляем дубликаты