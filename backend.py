# backend.py
import collections
from events import Event, EventType
from map_generator import generate_map
from hex_utils import hex_distance # Импортируем "физику"
from tile_types import TILE_PROPERTIES # Импортируем свойства клеток
from unit_types import UnitType, UNIT_PROPERTIES

class GameState:
    """Хранит все состояние игры."""
    def __init__(self):
        # grid теперь хранит словарь с данными о клетке, включая тип
        self.grid = {}  # { (q, r): {'tile': TileType, ...} }
        self.units = {} # { unit_id: unit_data }
        self.cities = {}
        self.turn_number = 0
        self.active_player = 0
        self.next_unit_id = 0
        self.next_city_id = 0

class Backend:
    """Управляет состоянием и логикой игры."""
    def __init__(self):
        self.game_state = GameState()
        self.event_queue = collections.deque()
        self.game_state.next_city_id = 0
        self._initialize_game()

    def _post_event(self, event_type, data=None):
        self.event_queue.append(Event(event_type, data))

    def _initialize_game(self):
        """Создает начальное состояние игры, используя генератор."""
        # Используем наш новый генератор карт!
        self.game_state.grid = generate_map(radius=15)
        
        # Создаем юнитов разных типов
        self.create_unit(unit_type=UnitType.SETTLER, player=0, position=(0, 0))
        self.create_unit(unit_type=UnitType.WARRIOR, player=0, position=(0, 1))
        self.create_unit(unit_type=UnitType.RIFLEMAN, player=1, position=(3, -5))

        self._post_event(EventType.GAME_STARTED)

    def found_city(self, unit_id: int, city_name: str):
        """Основывает город на месте юнита."""
        if unit_id not in self.game_state.units:
            return False # Юнит не найден

        unit = self.game_state.units[unit_id]
        unit_props = UNIT_PROPERTIES[unit['type']]

        # 1. Проверяем, может ли этот юнит основывать города
        if not unit_props.can_found_city:
            print(f"[Backend] Unit {unit_id} ({unit_props.name}) cannot found cities.")
            return False

        # 2. Проверяем, не слишком ли близко к другому городу (простое правило)
        position = unit['position']
        for city in self.game_state.cities.values():
            if hex_distance(position, city['center_hex']) < 4:
                print(f"[Backend] Cannot found city at {position}: too close to another city.")
                return False

        # 3. Все проверки пройдены, создаем город
        city_id = self.game_state.next_city_id
        new_city = {
            'id': city_id,
            'name': city_name,
            'owner_player_id': unit['player'],
            'center_hex': position,
            'districts': [], # Пока пустой список для будущих районов
            'population': 1
        }
        self.game_state.cities[city_id] = new_city
        self.game_state.next_city_id += 1
        
        # 4. Удаляем юнита-поселенца
        del self.game_state.units[unit_id]
        
        # 5. Сообщаем всем о событии
        self._post_event(EventType.CITY_FOUNDED, {'city_data': new_city, 'consumed_unit_id': unit_id})
        print(f"[Backend] Player {unit['player']} founded {city_name} at {position}")
        return True

    def create_unit(self, unit_type: UnitType, player: int, position: tuple):
        """Создает юнита указанного типа."""
        unit_id = self.game_state.next_unit_id
        
        # Получаем базовые свойства из нашего нового справочника
        base_data = UNIT_PROPERTIES[unit_type]
        
        self.game_state.units[unit_id] = {
            'id': unit_id,
            'type': unit_type, # <-- САМОЕ ВАЖНОЕ: храним тип юнита
            'player': player,
            'position': position,
            'hp': base_data.base_hp,
            'ap': base_data.base_ap,
            'attack': base_data.base_attack,
            'can_found_city': base_data.can_found_city
        }
        self.game_state.next_unit_id += 1
        self._post_event(EventType.UNIT_CREATED, {'unit_data': self.game_state.units[unit_id]})

    def move_unit(self, unit_id, new_position):
        if unit_id in self.game_state.units:
            unit = self.game_state.units[unit_id]
            old_position = unit['position']

            if new_position not in self.game_state.grid:
                return False

            # Проверка проходимости (теперь зависит от юнита)
            target_tile_type = self.game_state.grid[new_position]['tile']
            unit_props = UNIT_PROPERTIES[unit['type']]
            if not unit_props.can_traverse(target_tile_type):
                 return False

            # Проверка дистанции
            distance = hex_distance(old_position, new_position)
            
            # УБРАНА ПРОВЕРКА MOVEMENT_COST
            # В будущем здесь будет сложная логика:
            # cost = calculate_move_cost(unit, path)
            # if cost > unit['ap']: return False
            
            if distance > unit['ap']:
                return False 

            unit['position'] = new_position
            self._post_event(
                EventType.UNIT_MOVED,
                {'unit_id': unit_id, 'from': old_position, 'to': new_position}
            )
            return True
        return False

    def get_events(self):
        events = list(self.event_queue)
        self.event_queue.clear()
        return events

    def get_game_state(self):
        return self.game_state