# backend.py
import collections
from constants import MAP_WIDTH
from events import Event, EventType
from map_generator import generate_map
from hex_utils import wrapped_hex_distance, hex_neighbors
from tile_types import TileType, TILE_PROPERTIES
from unit_types import UnitType, UNIT_PROPERTIES, MOVEMENT_COSTS, ENERGY_REGENERATION

class GameState:
    def __init__(self):
        self.grid = {}
        self.units = {}
        self.cities = {}
        self.turn_number = 1
        self.active_player = 0
        self.players = [0, 1]
        self.next_unit_id = 0
        self.next_city_id = 0

class Backend:
    def __init__(self):
        self.game_state = GameState()
        self.event_queue = collections.deque()
        self._initialize_game()

    def _post_event(self, event_type, data=None):
        self.event_queue.append(Event(event_type, data))

    def _initialize_game(self):
        self.game_state.grid = generate_map()
        # Initial units in axial coordinates
        self.create_unit(unit_type=UnitType.SETTLER, player=0, position=(5, 5))
        self.create_unit(unit_type=UnitType.WARRIOR, player=0, position=(6, 5))
        self.create_unit(unit_type=UnitType.RIFLEMAN, player=1, position=(15, 15))
        self._post_event(EventType.GAME_STARTED)

    def end_turn(self):
        current_player_index = self.game_state.players.index(self.game_state.active_player)
        next_player_index = (current_player_index + 1) % len(self.game_state.players)
        self.game_state.active_player = self.game_state.players[next_player_index]

        if self.game_state.active_player == self.game_state.players[0]:
            self.game_state.turn_number += 1
            self._post_event(EventType.TURN_ENDED, {'new_turn_number': self.game_state.turn_number})

        for unit in self.game_state.units.values():
            if unit['player'] == self.game_state.active_player:
                unit_props = UNIT_PROPERTIES[unit['type']]
                tile_type = self.game_state.grid[unit['position']]['tile']
                regen_amount = ENERGY_REGENERATION.get(unit['type'], {}).get(tile_type, 1)
                unit['energy'] = min(unit_props.max_energy, unit['energy'] + regen_amount)

        self._post_event(EventType.NEXT_PLAYER_TURN, {'player_id': self.game_state.active_player})

    def found_city(self, unit_id: int, city_name: str):
        if unit_id not in self.game_state.units: return False

        unit = self.game_state.units[unit_id]
        if not UNIT_PROPERTIES[unit['type']].can_found_city: return False

        position = unit['position']
        for city in self.game_state.cities.values():
            if wrapped_hex_distance(position, city['center_hex']) < 4:
                return False

        city_id = self.game_state.next_city_id
        new_city = {
            'id': city_id, 'name': city_name, 'owner_player_id': unit['player'],
            'center_hex': position, 'population': 1
        }
        self.game_state.cities[city_id] = new_city
        self.game_state.next_city_id += 1
        del self.game_state.units[unit_id]
        
        self._post_event(EventType.CITY_FOUNDED, {'city_data': new_city, 'consumed_unit_id': unit_id})
        return True

    def create_unit(self, unit_type: UnitType, player: int, position: tuple):
        unit_id = self.game_state.next_unit_id
        base_data = UNIT_PROPERTIES[unit_type]
        self.game_state.units[unit_id] = {
            'id': unit_id, 'type': unit_type, 'player': player, 'position': position,
            'hp': base_data.base_hp, 'energy': base_data.max_energy,
            'attack': base_data.base_attack, 'can_found_city': base_data.can_found_city
        }
        self.game_state.next_unit_id += 1
        self._post_event(EventType.UNIT_CREATED, {'unit_data': self.game_state.units[unit_id]})

    def move_unit(self, unit_id, new_position):
        if unit_id not in self.game_state.units: return False

        unit = self.game_state.units[unit_id]
        old_position = unit['position']

        if wrapped_hex_distance(old_position, new_position) != 1: return False
        if new_position not in self.game_state.grid: return False

        target_tile_type = self.game_state.grid[new_position]['tile']
        if not UNIT_PROPERTIES[unit['type']].can_traverse(target_tile_type): return False

        move_cost = MOVEMENT_COSTS.get(unit['type'], {}).get(target_tile_type, 999)
        if unit['energy'] < move_cost: return False 

        # Wrap the unit's position
        unit['position'] = (new_position[0] % MAP_WIDTH, new_position[1])
        unit['energy'] -= move_cost
        
        self._post_event(EventType.UNIT_MOVED, {'unit_id': unit_id, 'to': unit['position']})
        return True

    def get_valid_moves(self, unit_id):
        if unit_id not in self.game_state.units: return []

        unit = self.game_state.units[unit_id]
        unit_props = UNIT_PROPERTIES[unit['type']]
        valid_moves = []
        
        for neighbor in hex_neighbors(unit['position']):
            # Wrap neighbor position for grid lookup
            wrapped_neighbor = (neighbor[0] % MAP_WIDTH, neighbor[1])

            if wrapped_neighbor not in self.game_state.grid: continue
            
            target_tile_type = self.game_state.grid[wrapped_neighbor]['tile']
            if not unit_props.can_traverse(target_tile_type): continue
                
            move_cost = MOVEMENT_COSTS.get(unit['type'], {}).get(target_tile_type, 999)
            if unit['energy'] < move_cost: continue
                
            valid_moves.append(wrapped_neighbor)
            
        return valid_moves

    def get_events(self):
        events = list(self.event_queue)
        self.event_queue.clear()
        return events

    def get_game_state(self):
        return self.game_state