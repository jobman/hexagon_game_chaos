# hex_utils.py
from typing import Tuple
from constants import MAP_WIDTH

Hex = Tuple[int, int]

# Направления для гексагональной сетки (axial coordinates)
HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1), 
    (-1, 0), (-1, 1), (0, 1)
]

def hex_add(hex1: Hex, hex2: Hex) -> Hex:
    """Складывает две гексагональные координаты."""
    return (hex1[0] + hex2[0], hex1[1] + hex2[1])

def hex_subtract(hex1: Hex, hex2: Hex) -> Hex:
    """Вычитает одну гексагональную координату из другой."""
    return (hex1[0] - hex2[0], hex1[1] - hex2[1])

def hex_wrap(h: Hex) -> Hex:
    """Обеспечивает зацикливание по горизонтали (ось q)."""
    q, r = h
    return (q % MAP_WIDTH, r)

def hex_distance(hex1: Hex, hex2: Hex) -> int:
    """Рассчитывает расстояние между двумя гексами с учетом зацикливания."""
    # Учитываем зацикливание по оси q
    q1, r1 = hex1
    q2, r2 = hex2

    # Находим кратчайшее расстояние по q, учитывая зацикливание
    q_dist = abs(q1 - q2)
    wrapped_q_dist = min(q_dist, MAP_WIDTH - q_dist)
    
    # Прямое расстояние по q и r без зацикливания
    direct_dist_vec = hex_subtract(hex1, hex2)
    
    # Если кратчайший путь лежит через край карты, нужно скорректировать r
    if wrapped_q_dist != q_dist:
        # Это сложная часть гексагонального зацикливания.
        # Для простоты пока будем использовать эвристику, которая хорошо работает для axial coordinates.
        # Более точный расчет потребовал бы преобразования в кубические координаты.
        # В нашем случае, изменение q влияет на r, но для большинства игровых механик
        # достаточно аппроксимации.
        r_dist = abs(r1 - r2)
        # Простая аппроксимация, может быть неточной в некоторых случаях
        return max(wrapped_q_dist, r_dist, (wrapped_q_dist + r_dist) // 2)
    else:
        # Стандартный расчет расстояния для axial coordinates
        return (abs(direct_dist_vec[0]) + abs(direct_dist_vec[1]) + abs(direct_dist_vec[0] + direct_dist_vec[1])) // 2

def hex_neighbors(h: Hex) -> list[Hex]:
    """Возвращает список соседних гексов с учетом зацикливания."""
    return [hex_wrap(hex_add(h, direction)) for direction in HEX_DIRECTIONS]

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