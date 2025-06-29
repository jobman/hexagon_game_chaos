# backend.py
import collections
from events import Event, EventType
from map_generator import generate_map
from hex_utils import hex_distance
from tile_types import TileType, TILE_PROPERTIES
from unit_types import UnitType, UNIT_PROPERTIES, MOVEMENT_COSTS, ENERGY_REGENERATION

class GameState:
    """Хранит все состояние игры."""
    def __init__(self):
        self.grid = {}  
        self.units = {} 
        self.cities = {}
        self.turn_number = 1
        self.active_player = 0
        self.players = [0, 1] # Пример
        self.next_unit_id = 0
        self.next_city_id = 0

class Backend:
    """Управляет состоянием и логикой игры."""
    def __init__(self):
        self.game_state = GameState()
        self.event_queue = collections.deque()
        self._initialize_game()

    def _post_event(self, event_type, data=None):
        self.event_queue.append(Event(event_type, data))

    def _initialize_game(self):
        """Создает начальное состояние игры."""
        self.game_state.grid = generate_map(radius=15)
        self.create_unit(unit_type=UnitType.SETTLER, player=0, position=(0, 0))
        self.create_unit(unit_type=UnitType.WARRIOR, player=0, position=(0, 1))
        self.create_unit(unit_type=UnitType.RIFLEMAN, player=1, position=(3, -5))
        self._post_event(EventType.GAME_STARTED)

    def end_turn(self):
        """Завершает ход текущего игрока и начинает ход следующего."""
        # 1. Переключаем активного игрока
        current_player_index = self.game_state.players.index(self.game_state.active_player)
        next_player_index = (current_player_index + 1) % len(self.game_state.players)
        self.game_state.active_player = self.game_state.players[next_player_index]

        # Если круг завершился, увеличиваем номер хода
        if self.game_state.active_player == self.game_state.players[0]:
            self.game_state.turn_number += 1
            self._post_event(EventType.TURN_ENDED, {'new_turn_number': self.game_state.turn_number})

        # 2. Восстанавливаем энергию всем юнитам нового активного игрока
        for unit in self.game_state.units.values():
            if unit['player'] == self.game_state.active_player:
                unit_props = UNIT_PROPERTIES[unit['type']]
                tile_type = self.game_state.grid[unit['position']]['tile']
                
                # Получаем регенерацию для типа юнита и типа клетки
                regen_amount = ENERGY_REGENERATION.get(unit['type'], {}).get(tile_type, 1)
                
                # Восстанавливаем энергию, не превышая максимум
                unit['energy'] = min(unit_props.max_energy, unit['energy'] + regen_amount)

        self._post_event(EventType.NEXT_PLAYER_TURN, {'player_id': self.game_state.active_player})
        print(f"[Backend] Turn {self.game_state.turn_number}, Player {self.game_state.active_player}'s turn.")


    def found_city(self, unit_id: int, city_name: str):
        """Основывает город на месте юнита."""
        if unit_id not in self.game_state.units:
            return False

        unit = self.game_state.units[unit_id]
        unit_props = UNIT_PROPERTIES[unit['type']]

        if not unit_props.can_found_city:
            return False

        position = unit['position']
        for city in self.game_state.cities.values():
            if hex_distance(position, city['center_hex']) < 4:
                return False

        city_id = self.game_state.next_city_id
        new_city = {
            'id': city_id,
            'name': city_name,
            'owner_player_id': unit['player'],
            'center_hex': position,
            'districts': [],
            'population': 1
        }
        self.game_state.cities[city_id] = new_city
        self.game_state.next_city_id += 1
        
        del self.game_state.units[unit_id]
        
        self._post_event(EventType.CITY_FOUNDED, {'city_data': new_city, 'consumed_unit_id': unit_id})
        return True

    def create_unit(self, unit_type: UnitType, player: int, position: tuple):
        """Создает юнита указанного типа."""
        unit_id = self.game_state.next_unit_id
        base_data = UNIT_PROPERTIES[unit_type]
        
        self.game_state.units[unit_id] = {
            'id': unit_id,
            'type': unit_type,
            'player': player,
            'position': position,
            'hp': base_data.base_hp,
            'energy': base_data.max_energy, # <-- Используем энергию
            'attack': base_data.base_attack,
            'can_found_city': base_data.can_found_city
        }
        self.game_state.next_unit_id += 1
        self._post_event(EventType.UNIT_CREATED, {'unit_data': self.game_state.units[unit_id]})

    def move_unit(self, unit_id, new_position):
        if unit_id not in self.game_state.units:
            return False

        unit = self.game_state.units[unit_id]
        old_position = unit['position']

        if new_position not in self.game_state.grid:
            return False

        target_tile_type = self.game_state.grid[new_position]['tile']
        unit_props = UNIT_PROPERTIES[unit['type']]
        if not unit_props.can_traverse(target_tile_type):
            return False

        # Используем MOVEMENT_COSTS для определения стоимости
        move_cost = MOVEMENT_COSTS.get(unit['type'], {}).get(target_tile_type, 999)

        if unit['energy'] < move_cost:
            return False 

        unit['position'] = new_position
        unit['energy'] -= move_cost # Тратим энергию
        
        self._post_event(
            EventType.UNIT_MOVED,
            {'unit_id': unit_id, 'from': old_position, 'to': new_position, 'new_energy': unit['energy']}
        )
        return True

    def get_events(self):
        events = list(self.event_queue)
        self.event_queue.clear()
        return events

    def get_game_state(self):
        return self.game_state