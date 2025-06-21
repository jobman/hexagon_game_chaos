# hex_utils.py

# Направления в axial-координатах для поиска соседей
# (q, r) ->  (q+1, r), (q+1, r-1), (q, r-1), (q-1, r), (q-1, r+1), (q, r+1)
_HEX_DIRECTIONS = [
    (1, 0), (1, -1), (0, -1),
    (-1, 0), (-1, 1), (0, 1)
]

def hex_add(a, b):
    """Сложение двух гекс-координат."""
    return a[0] + b[0], a[1] + b[1]

def hex_subtract(a, b):
    """Вычитание двух гекс-координат."""
    return a[0] - b[0], a[1] - b[1]

def hex_distance(a, b):
    """Рассчитывает дистанцию в гексах между двумя точками."""
    # Конвертируем axial в cube-координаты для простоты расчета
    a_cube = (a[0], a[1], -a[0] - a[1])
    b_cube = (b[0], b[1], -b[0] - b[1])
    # Расстояние - это половина манхэттенского расстояния в cube-координатах
    return (abs(a_cube[0] - b_cube[0]) + abs(a_cube[1] - b_cube[1]) + abs(a_cube[2] - b_cube[2])) // 2

def hex_neighbors(hex_coord):
    """Возвращает список 6 соседей указанного гекса."""
    return [hex_add(hex_coord, direction) for direction in _HEX_DIRECTIONS]

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