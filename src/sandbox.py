"""
sandbox.py
Sandbox conquest state, roster transfer, and battle setup helpers.
"""

import copy
import random

import shop
from terrain import generate_faction_battlefield
import world_map

STARTING_TREASURY = shop.STARTING_GOLD
CAPTURE_REWARD = 500
MIN_GARRISON_UNITS = 0
MIN_ENEMY_STARTING_UNITS = 1
MAX_GARRISON_UNITS = 6
PLAYER_STARTING_FIELD_UNITS = 3
FIELD_TEAM_CAPACITY = 6

GRID_ROWS = world_map.GRID_ROWS
GRID_COLS = world_map.GRID_COLS

FACTIONS = world_map.FACTIONS
PLAYABLE_FACTIONS = world_map.PLAYABLE_FACTIONS
FACTION_LOOKUP = world_map.FACTION_LOOKUP
TILE_CITY = world_map.TILE_CITY
TILE_EMPTY = world_map.TILE_EMPTY
TILE_BLOCKED = world_map.TILE_BLOCKED
TERRITORY_TEMPLATES = world_map.TILE_TEMPLATES
TERRITORY_LOOKUP = {territory["id"]: territory for territory in TERRITORY_TEMPLATES}
TERRITORY_IDS = list(world_map.TILE_ID_ORDER)
ADJACENCY_GRAPH = world_map.ADJACENCY_GRAPH
FACTION_OWNERSHIP = world_map.FACTION_OWNERSHIP
CENTRAL_EXPANSION_SCORE = world_map.CENTRAL_EXPANSION_SCORE

PLAYER_TEMPLATE = [
    {
        "unit_id": "hero",
        "name": "Hero",
        "strength": 5,
        "defense": 5,
        "speed": 8,
        "move": 3,
        "max_hp": 18,
        "weapon": ("Iron Sword", 5, 1),
        "inventory": [
            ("weapon", "Iron Sword", 5, 1),
            ("weapon", "Javelin", 4, 2),
            ("potion", "Potion", 8),
        ],
        "sprite_key": "F1",
        "position": (2, 2),
    },
    {
        "unit_id": "knight",
        "name": "Knight",
        "strength": 6,
        "defense": 7,
        "speed": 4,
        "move": 2,
        "max_hp": 20,
        "weapon": ("Lance", 4, 1),
        "inventory": [
            ("weapon", "Lance", 4, 1),
            ("weapon", "Javelin", 3, 2),
        ],
        "sprite_key": "M1",
        "position": (3, 2),
    },
]

ENEMY_TEMPLATE = [
    {
        "name": "Bandit",
        "strength": 5,
        "defense": 3,
        "speed": 5,
        "move": 3,
        "max_hp": 16,
        "weapon": ("Axe", 5, 1),
        "inventory": [("weapon", "Axe", 5, 1)],
        "sprite_key": "E1",
        "position": (6, 7),
    },
    {
        "name": "Soldier",
        "strength": 4,
        "defense": 5,
        "speed": 4,
        "move": 3,
        "max_hp": 17,
        "weapon": ("Spear", 4, 1),
        "inventory": [("weapon", "Spear", 4, 1)],
        "sprite_key": "E2",
        "position": (7, 7),
    },
]

PLAYER_SPRITE_KEYS = ["F1", "M1"]
ENEMY_SPRITE_KEYS = ["E1", "E2"]
PLAYER_DEPLOYMENT_POSITIONS = [(1, 1), (1, 3), (1, 5), (2, 2), (2, 4), (2, 6)]
ENEMY_DEPLOYMENT_POSITIONS = [(8, 3), (8, 5), (8, 7), (7, 2), (7, 4), (7, 6)]

_DEBUG_CORE_NAMES = [
    "Lyn",
    "Eli",
    "Ike",
    "Roy",
    "Mia",
    "Sain",
    "Kent",
    "Nino",
    "Flor",
    "Tana",
    "Erk",
    "Seth",
]
_NAME_ONSETS = ["B", "C", "D", "F", "G", "J", "K", "L", "M", "N", "R", "S", "T", "V", "W", "Z"]
_NAME_VOWELS = ["a", "e", "i", "o", "u"]
_NAME_CODAS = ["n", "l", "r", "s", "m", "k", "th"]
DEBUG_NAME_POOL = list(
    dict.fromkeys(
        _DEBUG_CORE_NAMES
        + [
            f"{onset}{vowel}{coda}".title()
            for onset in _NAME_ONSETS
            for vowel in _NAME_VOWELS
            for coda in _NAME_CODAS
        ]
    )
)


def create_sandbox_state():
    state = {
        "player_faction": None,
        "territories": {},
        "treasuries": {faction["id"]: STARTING_TREASURY for faction in FACTIONS},
        "faction_sizes": {
            faction_id: len(city_ids)
            for faction_id, city_ids in FACTION_OWNERSHIP.items()
        },
        "field_team": [],
        "field_units": PLAYER_STARTING_FIELD_UNITS,
        "next_unit_id": 1,
        "convoy": [],
        "shop_stock": shop.create_shop_stock(),
    }

    for template in world_map.TILE_TEMPLATES:
        territory = dict(template)
        initial_units = random.randint(MIN_ENEMY_STARTING_UNITS, 5) if territory["type"] == TILE_CITY else 0
        territory["units"] = create_named_units(state, initial_units)
        territory["stationed_units"] = len(territory["units"])
        state["territories"][territory["id"]] = territory

    state["field_team"] = create_named_units(state, PLAYER_STARTING_FIELD_UNITS)
    sync_unit_counts(state)
    return state


def get_territory(state, territory_id):
    return state["territories"].get(territory_id)


def get_faction(faction_id):
    return FACTION_LOOKUP[faction_id]


def get_faction_name(faction_id):
    return get_faction(faction_id)["name"]


def get_faction_color(faction_id):
    return get_faction(faction_id)["color"]


def get_player_faction(state):
    return state["player_faction"]


def set_player_faction(state, faction_id):
    state["player_faction"] = faction_id


def get_expansion_priority(territory_id):
    return CENTRAL_EXPANSION_SCORE.get(territory_id, 99)


def get_preferred_expansion_targets(state, faction_id):
    attackable = [
        territory["id"]
        for territory in iter_territories(state)
        if territory["owner_faction"] != faction_id
        and any(
            get_territory(state, neighbor_id)["owner_faction"] == faction_id
            for neighbor_id in territory["neighbors"]
        )
    ]
    return sorted(
        attackable,
        key=lambda territory_id: (
            get_expansion_priority(territory_id),
            get_stationed_units(state, territory_id),
            territory_id,
        ),
    )


def create_named_unit(state, reserved_names=None):
    unit_id = f"sandbox-unit-{state.get('next_unit_id', 1)}"
    state["next_unit_id"] = state.get("next_unit_id", 1) + 1
    used_names = {
        unit["name"]
        for territory in state.get("territories", {}).values()
        for unit in territory.get("units", [])
    }
    used_names.update(unit["name"] for unit in state.get("field_team", []))
    if reserved_names:
        used_names.update(reserved_names)
    name = next((candidate for candidate in DEBUG_NAME_POOL if candidate not in used_names), None)
    if name is None:
        name = f"U{state['next_unit_id']}"
    return {"id": unit_id, "name": name}


def create_named_units(state, count):
    created_units = []
    reserved_names = set()
    for _ in range(max(0, count)):
        unit = create_named_unit(state, reserved_names)
        created_units.append(unit)
        reserved_names.add(unit["name"])
    return created_units


def clone_named_unit(unit_data):
    return {
        "id": str(unit_data.get("id", "")),
        "name": str(unit_data.get("name", "Unit")),
    }


def clamp_stationed_units(unit_count):
    return max(MIN_GARRISON_UNITS, min(MAX_GARRISON_UNITS, unit_count))


def clamp_field_units(unit_count):
    return max(0, min(FIELD_TEAM_CAPACITY, unit_count))


def _extract_unit_index(unit_id):
    if not isinstance(unit_id, str):
        return 0
    try:
        return int(unit_id.rsplit("-", 1)[-1])
    except (TypeError, ValueError):
        return 0


def get_next_unit_id(state):
    max_index = max(
        [_extract_unit_index(unit["id"]) for territory in state["territories"].values() for unit in territory.get("units", [])]
        + [_extract_unit_index(unit["id"]) for unit in state.get("field_team", [])]
        + [0]
    )
    return max(state.get("next_unit_id", 1), max_index + 1)


def sync_unit_counts(state):
    for territory in state["territories"].values():
        if territory.get("type") == TILE_CITY:
            territory["units"] = [clone_named_unit(unit) for unit in territory.get("units", [])[:MAX_GARRISON_UNITS]]
            territory["stationed_units"] = clamp_stationed_units(len(territory["units"]))
        else:
            territory["units"] = []
            territory["stationed_units"] = 0
    state["field_team"] = [clone_named_unit(unit) for unit in state.get("field_team", [])[:FIELD_TEAM_CAPACITY]]
    state["field_units"] = clamp_field_units(len(state["field_team"]))
    state["next_unit_id"] = get_next_unit_id(state)
    state["faction_sizes"] = {
        faction["id"]: sum(
            1
            for territory in state["territories"].values()
            if territory.get("type") == TILE_CITY and territory.get("owner_faction") == faction["id"]
        )
        for faction in FACTIONS
    }


def iter_territories(state):
    for territory_id in TERRITORY_IDS:
        if territory_id in state["territories"]:
            yield state["territories"][territory_id]


def get_territory_units(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None:
        return []
    if territory.get("type") != TILE_CITY:
        territory["units"] = []
        territory["stationed_units"] = 0
        return []
    territory.setdefault("units", [])
    territory["units"] = territory["units"][:MAX_GARRISON_UNITS]
    territory["stationed_units"] = len(territory["units"])
    return territory["units"]


def get_field_team(state):
    state.setdefault("field_team", [])
    state["field_team"] = state["field_team"][:FIELD_TEAM_CAPACITY]
    state["field_units"] = len(state["field_team"])
    return state["field_team"]


def get_stationed_units(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None:
        return 0
    return len(get_territory_units(state, territory_id))


def get_dispatchable_units(state, territory_id):
    if not is_player_owned(state, territory_id):
        return 0
    return get_stationed_units(state, territory_id)


def is_player_owned(state, territory_id):
    territory = get_territory(state, territory_id)
    player_faction = get_player_faction(state)
    if territory is None or player_faction is None:
        return False
    return territory["type"] == TILE_CITY and territory["owner_faction"] == player_faction


def is_empty_reward_tile(state, territory_id):
    territory = get_territory(state, territory_id)
    return territory is not None and territory["type"] == TILE_EMPTY


def is_city_tile(state, territory_id):
    territory = get_territory(state, territory_id)
    return territory is not None and territory["type"] == TILE_CITY


def can_assign_field_unit(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None or territory.get("type") != TILE_CITY or not is_player_owned(state, territory_id):
        return False
    if not get_field_team(state):
        return False
    return get_stationed_units(state, territory_id) < MAX_GARRISON_UNITS


def assign_field_unit(state, territory_id, unit_index=0):
    if not can_assign_field_unit(state, territory_id):
        return False

    territory = get_territory(state, territory_id)
    field_team = get_field_team(state)
    if not (0 <= unit_index < len(field_team)):
        return False
    territory_units = get_territory_units(state, territory_id)
    territory_units.append(field_team.pop(unit_index))
    sync_unit_counts(state)
    return True


def can_recall_field_unit(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None or territory.get("type") != TILE_CITY or not is_player_owned(state, territory_id):
        return False
    if len(get_field_team(state)) >= FIELD_TEAM_CAPACITY:
        return False
    return get_dispatchable_units(state, territory_id) > 0


def recall_field_unit(state, territory_id, unit_index=0):
    if not can_recall_field_unit(state, territory_id):
        return False

    territory_units = get_territory_units(state, territory_id)
    if not (0 <= unit_index < len(territory_units)):
        return False
    get_field_team(state).append(territory_units.pop(unit_index))
    sync_unit_counts(state)
    return True


def is_attackable(state, territory_id):
    player_faction = get_player_faction(state)
    territory = get_territory(state, territory_id)
    if not player_faction or territory is None:
        return False
    if territory["type"] == TILE_BLOCKED:
        return False
    if territory["type"] == TILE_CITY and territory["owner_faction"] == player_faction:
        return False
    return any(
        is_player_owned(state, neighbor_id)
        for neighbor_id in territory["neighbors"]
    )


def get_valid_targets_from_source(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None or not is_player_owned(state, territory_id):
        return []

    return [
        neighbor_id
        for neighbor_id in territory["neighbors"]
        if is_attackable(state, neighbor_id)
    ]


def _build_deployment_positions(preferred_positions, count):
    if count <= len(preferred_positions):
        return list(preferred_positions[:count])

    positions = list(preferred_positions)
    for row in range(10):
        for col in range(10):
            candidate = (row, col)
            if candidate not in positions:
                positions.append(candidate)
            if len(positions) >= count:
                return positions[:count]
    return positions[:count]


def _build_side_specs(unit_entries, templates, sprite_keys, positions, enemy_levels=False):
    deployment_positions = _build_deployment_positions(positions, len(unit_entries))
    specs = []

    for index, unit_data in enumerate(unit_entries):
        template = copy.deepcopy(templates[index % len(templates)])
        template["name"] = unit_data["name"]
        template["unit_id"] = unit_data.get("id")
        template["position"] = deployment_positions[index]
        template["sprite_key"] = sprite_keys[index % len(sprite_keys)]
        template["level"] = unit_data.get("level", random.randint(1, 10) if enemy_levels else 1)
        specs.append(template)

    return specs


def build_battle_setup(state, territory_id):
    territory = get_territory(state, territory_id)
    if territory is None or territory.get("type") != TILE_CITY:
        return None

    attackers = [clone_named_unit(unit) for unit in get_field_team(state)]
    defenders = [clone_named_unit(unit) for unit in get_territory_units(state, territory_id)]
    if not attackers or not defenders:
        return None

    players = _build_side_specs(
        attackers,
        PLAYER_TEMPLATE,
        PLAYER_SPRITE_KEYS,
        PLAYER_DEPLOYMENT_POSITIONS,
        enemy_levels=False,
    )
    enemies = _build_side_specs(
        defenders,
        ENEMY_TEMPLATE,
        ENEMY_SPRITE_KEYS,
        ENEMY_DEPLOYMENT_POSITIONS,
        enemy_levels=True,
    )

    return {
        "name": f"Battle for {territory['name']}",
        "players": players,
        "enemies": enemies,
        "terrain": generate_faction_battlefield(territory["owner_faction"], territory["id"]),
    }


def apply_battle_result(state, territory_id, player_won):
    territory = get_territory(state, territory_id)
    player_faction = get_player_faction(state)
    if territory is None or player_faction is None or territory.get("type") != TILE_CITY:
        return

    if player_won:
        territory["owner_faction"] = player_faction
        retained_units = max(1, min(MAX_GARRISON_UNITS, get_stationed_units(state, territory_id)))
        territory["units"] = create_named_units(state, retained_units)
        sync_unit_counts(state)
        state["treasuries"][player_faction] += territory["reward"]
        return

    state["treasuries"][player_faction] = max(
        0,
        state["treasuries"][player_faction] - territory["reward"],
    )


def _next_city_name(state, faction_id):
    existing = {
        territory["name"]
        for territory in iter_territories(state)
        if territory.get("owner_faction") == faction_id and territory.get("type") == TILE_CITY
    }
    faction_name = get_faction_name(faction_id)
    index = 1
    while f"{faction_name}{index}" in existing:
        index += 1
    return f"{faction_name}{index}"


def capture_empty_tile(state, territory_id):
    territory = get_territory(state, territory_id)
    player_faction = get_player_faction(state)
    if territory is None or player_faction is None or territory.get("type") != TILE_EMPTY:
        return False
    if not is_attackable(state, territory_id):
        return False

    territory["type"] = TILE_CITY
    territory["owner_faction"] = player_faction
    territory["name"] = _next_city_name(state, player_faction)
    territory["units"] = []
    territory["stationed_units"] = 0
    state["treasuries"][player_faction] += territory["reward"]
    sync_unit_counts(state)
    return True
