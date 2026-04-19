import os
import sys

pygame = None

from ai import enemy_action
from combat import attack_preview, combat, get_attack_tiles, get_attack_tiles_from_position, in_range
from inventory import Potion, item_label
from map import Map
from menu import VerticalMenu
from movement import can_move, get_reachable_tiles
from terrain import (
    TERRAIN_FORT,
    TERRAIN_GRASS,
    apply_end_turn_terrain_effect,
    build_terrain_overlays,
    draw_terrain_tile,
)
from unit import Unit
from weapon import Weapon

WIDTH, HEIGHT = 760, 800
CELL = 50
GRID_SIZE = 10
BOARD_TOP = 100
BOARD_SIZE = GRID_SIZE * CELL
PANEL_X = BOARD_SIZE + 20
PANEL_WIDTH = WIDTH - PANEL_X - 20
PANEL_PADDING = 12
PANEL_LINE_HEIGHT = 24
PANEL_BUTTON_Y = 18
PANEL_BUTTON_HEIGHT = 42
PANEL_HEADER_Y = 78
PANEL_HEADER_HEIGHT = 82
PANEL_UNIT_Y = 176
PANEL_UNIT_HEIGHT = 134
PANEL_ACTION_Y = 326
PANEL_ACTION_HEIGHT = 170
PANEL_PREVIEW_Y = 512
PANEL_PREVIEW_HEIGHT = 112
PANEL_LOG_Y = 640
PANEL_LOG_HEIGHT = 142

SCENE_MENU = "MENU"
SCENE_CHAPTER_SELECT = "CHAPTER_SELECT"
SCENE_GAME = "GAME"

WHITE = (245, 243, 238)
BLACK = (32, 32, 32)
BLUE = (100, 150, 255)
RED = (220, 100, 100)
GREEN = (120, 205, 130)
GOLD = (240, 210, 90)
PANEL_BG = (224, 219, 209)
PANEL_BORDER = (145, 135, 120)
LIGHT_BLUE = (180, 213, 255)
LIGHT_RED = (248, 193, 193)
LIGHT_GOLD = (252, 234, 167)
GREY = (150, 150, 150)
GRID = (150, 150, 150)
BUTTON = (236, 232, 221)
BUTTON_DISABLED = (194, 190, 182)
TEXT_DISABLED = (115, 115, 115)
HP_GREEN = (100, 205, 120)
HP_EMPTY = (132, 124, 116)

MENU_COLORS = {
    "button": BUTTON,
    "button_disabled": BUTTON_DISABLED,
    "border": PANEL_BORDER,
    "text": BLACK,
    "text_disabled": TEXT_DISABLED,
}

ASSET_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../image"))
SPRITE_FILES = {
    "F1": "F1.png",
    "M1": "M1.png",
    "E1": "E1.png",
    "E2": "E2.png",
}

screen = None
font = None
title_font = None
menu_title_font = None
menu_button_font = None
UNIT_SPRITES = {}
TERRAIN_OVERLAYS = {}
IS_WEB = sys.platform == "emscripten"
FIRST_FRAME_LOGGED = False
panel_menu = None
menu_button = None
chapter_buttons = {}

CHAPTERS = {
    1: {
        "name": "Chapter 1",
        "players": [
            {
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
                "position": (3, 3),
            }
        ],
        "enemies": [
            {
                "name": "Enemy",
                "strength": 4,
                "defense": 4,
                "speed": 5,
                "move": 3,
                "max_hp": 16,
                "weapon": ("Iron Blade", 5, 1),
                "inventory": [("weapon", "Iron Blade", 5, 1)],
                "sprite_key": "E1",
                "position": (3, 6),
            }
        ],
        "terrain": [
            (TERRAIN_GRASS, 2, 2),
            (TERRAIN_GRASS, 4, 2),
            (TERRAIN_GRASS, 2, 4),
            (TERRAIN_FORT, 5, 5),
        ],
    },
    2: {
        "name": "Chapter 2",
        "players": [
            {
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
                "position": (2, 3),
            },
            {
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
                "position": (4, 3),
            },
        ],
        "enemies": [
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
                "position": (2, 7),
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
                "position": (5, 6),
            },
        ],
        "terrain": [
            (TERRAIN_GRASS, 1, 3),
            (TERRAIN_GRASS, 2, 4),
            (TERRAIN_GRASS, 4, 4),
            (TERRAIN_GRASS, 6, 5),
            (TERRAIN_FORT, 3, 5),
            (TERRAIN_FORT, 6, 6),
        ],
    },
}

def load_unit_sprite(filename):
    image_path = os.path.join(ASSET_DIR, filename)
    image = pygame.image.load(image_path).convert_alpha()
    max_size = CELL - 10
    width, height = image.get_size()
    scale = min(max_size / width, max_size / height)
    scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return pygame.transform.smoothscale(image, scaled_size)


def startup_log(message):
    if not IS_WEB:
        return

    print(message)
    try:
        import platform

        platform.window.console.log(message)
    except Exception:
        pass


def init_runtime():
    global pygame, screen, font, title_font, menu_title_font, menu_button_font

    if screen is not None:
        return

    import pygame as _pygame

    pygame = _pygame

    startup_log("BEFORE pygame.init()")
    pygame.init()
    startup_log("AFTER pygame.init()")
    startup_log("BEFORE display creation")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    startup_log("AFTER display creation")
    pygame.display.set_caption("Fire Emblem Style Battle")
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 30)
    menu_title_font = pygame.font.SysFont(None, 56)
    menu_button_font = pygame.font.SysFont(None, 34)


def init_ui():
    global panel_menu, menu_button, chapter_buttons

    startup_log("BEFORE UI/runtime object creation")
    panel_menu = VerticalMenu(PANEL_X + PANEL_PADDING, PANEL_ACTION_Y + 34, PANEL_WIDTH - PANEL_PADDING * 2)
    menu_button = pygame.Rect(240, 320, 280, 64)
    chapter_buttons = {
        1: pygame.Rect(235, 250, 290, 58),
        2: pygame.Rect(235, 335, 290, 58),
    }
    startup_log("AFTER UI/runtime object creation")


def init_assets():
    global UNIT_SPRITES, TERRAIN_OVERLAYS

    startup_log("BEFORE asset loading")
    UNIT_SPRITES = {
        key: load_unit_sprite(filename)
        for key, filename in SPRITE_FILES.items()
    }
    TERRAIN_OVERLAYS = build_terrain_overlays(CELL)
    startup_log("AFTER asset loading")


game_map = None
players = []
enemies = []
selected_unit = None
original_position = None
preview_target = None
turn = 1
phase = "START"
interaction_state = "idle"
battle_log = []
menu_actions = {}

scene = SCENE_MENU
selected_chapter_id = None


def init_state():
    global game_map, players, enemies, selected_unit, original_position, preview_target
    global turn, phase, interaction_state, battle_log, menu_actions
    global scene, selected_chapter_id

    game_map = Map()
    players = []
    enemies = []
    selected_unit = None
    original_position = None
    preview_target = None
    turn = 1
    phase = "START"
    interaction_state = "idle"
    battle_log = []
    menu_actions = {}
    scene = SCENE_MENU
    selected_chapter_id = None


def make_weapon(spec):
    name, attack, attack_range = spec
    return Weapon(name, attack, attack_range)


def make_item(spec):
    item_type = spec[0]
    if item_type == "weapon":
        return make_weapon(spec[1:])
    if item_type == "potion":
        return Potion(spec[1], spec[2])
    return None


def create_unit(spec):
    inventory = [make_item(item_spec) for item_spec in spec["inventory"]]
    weapon_name = spec["weapon"][0]
    equipped_weapon = None

    for item in inventory:
        if getattr(item, "item_type", None) == "weapon" and item.name == weapon_name:
            equipped_weapon = item
            break

    return Unit(
        spec["name"],
        spec["strength"],
        spec["defense"],
        spec["speed"],
        spec["move"],
        equipped_weapon,
        inventory=inventory,
        max_hp=spec["max_hp"],
        sprite_key=spec.get("sprite_key"),
    )


def load_chapter(chapter_id):
    global game_map, players, enemies, battle_log, turn, phase
    global interaction_state, selected_unit, original_position, preview_target, selected_chapter_id

    chapter = CHAPTERS[chapter_id]
    selected_chapter_id = chapter_id
    game_map = Map()
    players = []
    enemies = []

    for player_spec in chapter["players"]:
        unit = create_unit(player_spec)
        players.append(unit)
        px, py = player_spec["position"]
        game_map.place_unit(unit, px, py)

    for enemy_spec in chapter["enemies"]:
        unit = create_unit(enemy_spec)
        enemies.append(unit)
        ex, ey = enemy_spec["position"]
        game_map.place_unit(unit, ex, ey)

    for terrain_type, tx, ty in chapter.get("terrain", []):
        game_map.set_terrain(tx, ty, terrain_type)

    turn = 1
    phase = "START"
    interaction_state = "idle"
    selected_unit = None
    original_position = None
    preview_target = None
    battle_log = [f"{chapter['name']} loaded."]


def current_chapter_name():
    if selected_chapter_id is None:
        return "No Chapter"
    return CHAPTERS[selected_chapter_id]["name"]


def alive_units(units):
    return [unit for unit in units if unit.is_alive()]


def select_unit_for_planning(unit):
    global selected_unit, original_position, interaction_state, preview_target
    selected_unit = unit
    original_position = unit.get_position()
    selected_unit.has_moved = False
    interaction_state = "planning"
    preview_target = None


def update_selected_move_flag():
    if not selected_unit or original_position is None:
        return
    selected_unit.has_moved = selected_unit.get_position() != original_position


def revert_selected_to_original():
    if not selected_unit or original_position is None:
        return
    if selected_unit.get_position() == original_position:
        selected_unit.has_moved = False
        return

    ox, oy = original_position
    occupant = game_map.get_unit(ox, oy)
    if occupant is None:
        game_map.move_unit(selected_unit, ox, oy)
    update_selected_move_flag()


def clear_selection():
    global selected_unit, original_position, interaction_state, preview_target
    selected_unit = None
    original_position = None
    interaction_state = "idle"
    preview_target = None


def add_log(message):
    battle_log.append(message)


def apply_end_turn_effects(unit):
    if not unit or not unit.is_alive() or not unit.game_map:
        return

    x, y = unit.get_position()
    terrain_type = unit.game_map.get_terrain(x, y)
    healed = apply_end_turn_terrain_effect(unit, terrain_type)
    if healed > 0:
        add_log(f"{unit.name} recovered {healed} HP on Fort")


def append_combat_log(entries):
    for name, hit, dmg in entries:
        battle_log.append(f"{name} {'HIT' if hit else 'MISS'} dmg:{dmg}")


def get_move_range(unit, game_map_obj=None):
    game_map_obj = game_map_obj or game_map
    if unit is selected_unit and original_position is not None:
        origin_x, origin_y = original_position
    else:
        origin_x, origin_y = unit.get_position()

    cells = []
    for x in range(game_map_obj.size):
        for y in range(game_map_obj.size):
            distance = abs(x - origin_x) + abs(y - origin_y)
            if distance == 0 or distance > unit.move:
                continue
            if game_map_obj.get_unit(x, y) is None:
                cells.append((x, y))

    return cells


def get_attack_range(unit, game_map_obj=None):
    if not unit.weapon:
        return []

    game_map_obj = game_map_obj or game_map
    if unit is selected_unit and original_position is not None:
        origin_tile = original_position
    else:
        origin_tile = unit.get_position()

    attack_tiles = set()
    move_origins = get_move_range(unit, game_map_obj)
    move_origins.append(origin_tile)

    for origin in move_origins:
        attack_tiles.update(
            get_attack_tiles_from_position(origin, unit.weapon.range, game_map_obj.size)
        )

    return sorted(attack_tiles)


def get_post_move_attack_range(unit):
    return get_attack_range(unit, game_map)


def get_reachable_tiles_for_origin(unit):
    if unit is selected_unit and original_position is not None:
        return get_planning_move_range(unit, include_origin=True)
    return get_reachable_tiles(unit, game_map, include_origin=True)


def get_planning_move_range(unit, include_origin=False):
    if original_position is None:
        return []

    ox, oy = original_position
    cells = []
    for x in range(game_map.size):
        for y in range(game_map.size):
            distance = abs(x - ox) + abs(y - oy)
            if distance > unit.move:
                continue
            if distance == 0:
                if include_origin:
                    cells.append((x, y))
                continue

            occupant = game_map.get_unit(x, y)
            if occupant is None or occupant is unit:
                cells.append((x, y))

    return cells


def can_plan_move(unit, x, y):
    if original_position is None:
        return False
    if not game_map.in_bounds(x, y):
        return False

    ox, oy = original_position
    if abs(x - ox) + abs(y - oy) > unit.move:
        return False

    occupant = game_map.get_unit(x, y)
    return occupant is None or occupant is unit


def enemies_in_range(unit):
    return [enemy_unit for enemy_unit in alive_units(enemies) if in_range(unit, enemy_unit)]


def all_players_acted():
    active_players = alive_units(players)
    return bool(active_players) and all(unit.has_acted for unit in active_players)


def cleanup_dead_units():
    global phase
    if scene != SCENE_GAME or selected_chapter_id is None:
        return

    for group in (players, enemies):
        for unit in group[:]:
            if unit.is_alive():
                continue
            game_map.remove_unit(unit)
            group.remove(unit)

    if selected_unit and not selected_unit.is_alive():
        clear_selection()

    if not alive_units(enemies):
        phase = "VICTORY"
    elif not alive_units(players):
        phase = "DEFEAT"


def begin_player_phase():
    global phase, interaction_state, preview_target
    for unit in alive_units(players):
        unit.reset_turn()
    phase = "PLAYER"
    interaction_state = "idle"
    preview_target = None
    clear_selection()


def begin_enemy_phase():
    global phase, preview_target
    clear_selection()
    for unit in alive_units(enemies):
        unit.reset_turn()
    phase = "ENEMY"
    preview_target = None


def finish_selected_action():
    if not selected_unit:
        return
    acting_unit = selected_unit
    acting_unit.has_acted = True
    acting_unit.has_moved = False
    apply_end_turn_effects(acting_unit)
    clear_selection()
    if phase == "PLAYER" and all_players_acted():
        begin_enemy_phase()


def use_inventory_item(item):
    global interaction_state
    if not selected_unit:
        return

    if getattr(item, "item_type", None) == "weapon":
        if selected_unit.equip_weapon(item):
            add_log(f"{selected_unit.name} equipped {item.name}")
            interaction_state = "planning"
        return

    if getattr(item, "item_type", None) == "potion":
        healed = selected_unit.heal(item.heal_amount)
        if healed > 0:
            selected_unit.remove_item(item)
            add_log(f"{selected_unit.name} used {item.name} +{healed} HP")
            finish_selected_action()


def execute_attack(target):
    if not selected_unit or not target or not target.is_alive():
        return
    if target not in enemies_in_range(selected_unit):
        return

    entries = combat(selected_unit, target)
    append_combat_log(entries)
    finish_selected_action()
    cleanup_dead_units()


def run_enemy_phase():
    global turn
    if scene != SCENE_GAME or phase != "ENEMY":
        return

    for enemy_unit in alive_units(enemies):
        if not alive_units(players):
            break
        entries = enemy_action(enemy_unit, alive_units(players), game_map)
        append_combat_log(entries)
        apply_end_turn_effects(enemy_unit)
        cleanup_dead_units()
        if phase in {"VICTORY", "DEFEAT"}:
            return

    if phase == "ENEMY":
        turn += 1
        begin_player_phase()


def start_battle():
    global turn, battle_log
    turn = 1
    battle_log = [f"{current_chapter_name()} started."]
    begin_player_phase()


def return_to_chapter_select():
    global scene, selected_chapter_id, battle_log, phase
    clear_selection()
    selected_chapter_id = None
    battle_log = []
    phase = "START"
    scene = SCENE_CHAPTER_SELECT


def get_attack_preview(attacker, defender):
    if not attacker or not defender or defender not in alive_units(enemies):
        return None
    if defender not in enemies_in_range(attacker):
        return None
    return attack_preview(attacker, defender)


def build_action_menu():
    if not selected_unit:
        return []
    return [
        {
            "key": "attack",
            "label": "Attack",
            "enabled": bool(enemies_in_range(selected_unit)),
        },
        {
            "key": "item",
            "label": "Item",
            "enabled": bool(selected_unit.inventory),
        },
        {
            "key": "wait",
            "label": "Wait",
            "enabled": True,
        },
    ]


def build_item_menu():
    options = []
    if not selected_unit:
        return options

    for index, item in enumerate(selected_unit.inventory):
        enabled = True
        label = item_label(item)
        if item is selected_unit.weapon:
            label = f"{label} [Equipped]"
        if getattr(item, "item_type", None) == "potion" and selected_unit.hp >= selected_unit.max_hp:
            enabled = False
        options.append(
            {
                "key": f"item:{index}",
                "label": label,
                "enabled": enabled,
            }
        )

    options.append({"key": "back", "label": "Back", "enabled": True})
    return options


def update_panel_menu():
    global menu_actions
    menu_actions = {}

    if interaction_state == "planning":
        options = build_action_menu()
        menu_actions = {option["key"]: option["key"] for option in options}
    elif interaction_state == "item_menu":
        options = build_item_menu()
        for option in options:
            if option["key"].startswith("item:"):
                index = int(option["key"].split(":")[1])
                menu_actions[option["key"]] = selected_unit.inventory[index]
            else:
                menu_actions[option["key"]] = option["key"]
    else:
        options = []

    panel_menu.set_options(options)


def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL, y * CELL + BOARD_TOP, CELL, CELL)
            pygame.draw.rect(screen, GRID, rect, 1)


def draw_terrain():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            terrain_type = game_map.get_terrain(x, y)
            draw_terrain_tile(
                screen,
                TERRAIN_OVERLAYS,
                terrain_type,
                (x * CELL, y * CELL + BOARD_TOP),
            )


def draw_ranges():
    if not selected_unit or phase != "PLAYER":
        return

    move_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    move_overlay.fill((80, 150, 255, 110))
    attack_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    attack_overlay.fill((255, 90, 90, 130))

    for x, y in get_move_range(selected_unit, game_map):
        screen.blit(move_overlay, (x * CELL, y * CELL + BOARD_TOP))

    for x, y in get_attack_range(selected_unit, game_map):
        screen.blit(attack_overlay, (x * CELL, y * CELL + BOARD_TOP))


def draw_unit_hp_bar(unit, body_rect):
    columns = 10
    size = 3
    gap = 1
    rows = (unit.max_hp + columns - 1) // columns
    total_width = columns * size + (columns - 1) * gap
    total_height = rows * size + (rows - 1) * gap
    start_x = body_rect.centerx - total_width // 2
    start_y = body_rect.top - total_height - 4

    for hp_index in range(unit.max_hp):
        col = hp_index % columns
        row = hp_index // columns
        rect = pygame.Rect(
            start_x + col * (size + gap),
            start_y + row * (size + gap),
            size,
            size,
        )
        color = HP_GREEN if hp_index < unit.hp else HP_EMPTY
        pygame.draw.rect(screen, color, rect)


def draw_units():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            unit = game_map.get_unit(x, y)
            if not unit:
                continue

            faction_color = BLUE if unit in players else RED

            body = pygame.Rect(x * CELL + 5, y * CELL + BOARD_TOP + 5, 40, 40)
            if unit is selected_unit:
                pygame.draw.rect(screen, LIGHT_GOLD, body.inflate(12, 12), border_radius=6)

            sprite = UNIT_SPRITES.get(unit.sprite_key)
            if sprite:
                sprite_rect = sprite.get_rect(center=body.center)
                screen.blit(sprite, sprite_rect)
            else:
                pygame.draw.rect(screen, GREY, body, border_radius=6)

            draw_unit_hp_bar(unit, body)
            pygame.draw.rect(screen, faction_color, body, 2, border_radius=6)

            if unit is selected_unit:
                pygame.draw.rect(screen, GOLD, body.inflate(6, 6), 3)
            elif interaction_state == "targeting_attack" and unit is preview_target:
                pygame.draw.rect(screen, GOLD, body.inflate(4, 4), 2)


def draw_roster():
    y = 10
    for unit in players:
        if not unit.is_alive():
            continue
        weapon_name = unit.weapon.name if unit.weapon else "None"
        text = (
            f"{unit.name} HP:{unit.hp}/{unit.max_hp} ATK:{unit.get_attack()} "
            f"DEF:{unit.defense} WPN:{weapon_name}"
        )
        screen.blit(font.render(text, True, BLUE), (10, y))
        y += 28

    for unit in enemies:
        if not unit.is_alive():
            continue
        weapon_name = unit.weapon.name if unit.weapon else "None"
        text = (
            f"{unit.name} HP:{unit.hp}/{unit.max_hp} ATK:{unit.get_attack()} "
            f"DEF:{unit.defense} WPN:{weapon_name}"
        )
        screen.blit(font.render(text, True, RED), (10, y))
        y += 28


def draw_panel_section(title, top, height):
    rect = pygame.Rect(PANEL_X, top, PANEL_WIDTH, height)
    pygame.draw.rect(screen, BUTTON, rect, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=8)
    if title:
        screen.blit(title_font.render(title, True, BLACK), (rect.x + PANEL_PADDING, rect.y + 8))
    return rect


def draw_panel_lines(lines, rect, start_y=42):
    y = rect.y + start_y
    for line in lines:
        screen.blit(font.render(line, True, BLACK), (rect.x + PANEL_PADDING, y))
        y += PANEL_LINE_HEIGHT


def draw_header_panel():
    header_rect = draw_panel_section("", PANEL_HEADER_Y, PANEL_HEADER_HEIGHT)
    lines = [
        current_chapter_name(),
        f"Turn {turn}",
        f"Phase: {phase}",
    ]
    draw_panel_lines(lines, header_rect, start_y=12)


def draw_unit_info_panel():
    unit_rect = draw_panel_section("Unit", PANEL_UNIT_Y, PANEL_UNIT_HEIGHT)

    if selected_unit:
        weapon_name = selected_unit.weapon.name if selected_unit.weapon else "None"
        lines = [
            selected_unit.name,
            f"HP: {selected_unit.hp}/{selected_unit.max_hp}",
            f"Move: {selected_unit.move}",
            f"Weapon: {weapon_name}",
            f"State: moved={selected_unit.has_moved} acted={selected_unit.has_acted}",
        ]
        if original_position is not None:
            lines.insert(4, f"Origin: {original_position[0]}, {original_position[1]}")
    elif phase == "START":
        lines = ["Chapter loaded.", "Click Start Battle."]
    else:
        lines = ["Select a unit to act."]

    draw_panel_lines(lines, unit_rect)


def draw_action_panel():
    action_title = "Action"
    action_lines = []
    if interaction_state == "item_menu":
        action_title = "Items"
    elif interaction_state == "targeting_attack":
        action_title = "Attack"
        action_lines = ["Click an enemy in range."]
    elif phase == "START":
        action_title = "Action"
        action_lines = ["Start Battle begins the player phase."]
    elif interaction_state not in {"planning", "item_menu"}:
        action_lines = ["Move, then choose an action."]

    action_rect = draw_panel_section(action_title, PANEL_ACTION_Y, PANEL_ACTION_HEIGHT)
    if action_lines:
        draw_panel_lines(action_lines, action_rect)

    panel_menu.x = PANEL_X + PANEL_PADDING
    panel_menu.y = PANEL_ACTION_Y + 42
    panel_menu.width = PANEL_WIDTH - PANEL_PADDING * 2

    if interaction_state in {"planning", "item_menu"}:
        panel_menu.draw(screen, font, MENU_COLORS)


def draw_battle_preview_panel():
    preview_rect = draw_panel_section("Preview", PANEL_PREVIEW_Y, PANEL_PREVIEW_HEIGHT)
    preview = get_attack_preview(selected_unit, preview_target)

    if interaction_state != "targeting_attack":
        draw_panel_lines(["No battle preview."], preview_rect)
        return

    if not preview_target or not preview:
        draw_panel_lines(["Hover an enemy to preview combat."], preview_rect)
        return

    lines = [
        f"Target: {preview_target.name}",
        f"Hit {preview['attacker_hit']}  Dmg {preview['attacker_damage']}",
        f"Enemy HP {preview_target.hp} -> {preview['defender_hp']}",
    ]
    if preview["counter"]:
        lines.append(f"Counter {preview['defender_hit']} / {preview['defender_damage']}")
    draw_panel_lines(lines, preview_rect)


def draw_log_panel():
    log_rect = draw_panel_section("Log", PANEL_LOG_Y, PANEL_LOG_HEIGHT)
    entries = battle_log[-5:] if battle_log else ["No messages."]
    draw_panel_lines(entries, log_rect)


def draw_end_state():
    message = "Victory" if phase == "VICTORY" else "Game Over"
    overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    overlay.fill((20, 20, 20, 140))
    screen.blit(overlay, (0, BOARD_TOP))

    label = menu_title_font.render(message, True, WHITE)
    label_rect = label.get_rect(center=(BOARD_SIZE // 2, BOARD_TOP + BOARD_SIZE // 2))
    screen.blit(label, label_rect)


def draw_panel():
    update_panel_menu()

    panel_rect = pygame.Rect(PANEL_X - 10, 0, PANEL_WIDTH + 20, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (PANEL_X - 10, 0), (PANEL_X - 10, HEIGHT), 3)

    start_button = pygame.Rect(PANEL_X, 18, PANEL_WIDTH, 42)
    is_start_ready = phase == "START"
    is_return_ready = phase == "VICTORY"
    button_enabled = is_start_ready or is_return_ready
    button_label = "Return Menu" if is_return_ready else "Start Battle"
    pygame.draw.rect(screen, GREEN if button_enabled else BUTTON_DISABLED, start_button, border_radius=6)
    pygame.draw.rect(screen, PANEL_BORDER, start_button, 2, border_radius=6)
    screen.blit(title_font.render(button_label, True, BLACK), (PANEL_X + 18, 26))
    draw_header_panel()
    draw_unit_info_panel()
    draw_action_panel()
    draw_battle_preview_panel()
    draw_log_panel()

    if phase in {"VICTORY", "DEFEAT"}:
        draw_end_state()

    return start_button


def draw_game_scene():
    draw_grid()
    draw_terrain()
    draw_ranges()
    draw_units()
    draw_roster()
    return draw_panel()


def draw_menu_scene():
    title = menu_title_font.render("Tactical RPG", True, BLACK)
    subtitle = title_font.render("Fire Emblem Style", True, BLACK)
    pygame.draw.rect(screen, PANEL_BG, menu_button, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, menu_button, 2, border_radius=8)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 200)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 255)))
    screen.blit(menu_button_font.render("Start Game", True, BLACK), menu_button.move(62, 18))


def draw_chapter_select_scene():
    title = menu_title_font.render("Chapter Select", True, BLACK)
    subtitle = title_font.render("Choose a battle map", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 200)))

    for chapter_id, rect in chapter_buttons.items():
        pygame.draw.rect(screen, PANEL_BG, rect, border_radius=8)
        pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=8)
        label = menu_button_font.render(CHAPTERS[chapter_id]["name"], True, BLACK)
        screen.blit(label, label.get_rect(center=rect.center))


def handle_action_menu_click(key):
    global interaction_state, preview_target
    if key == "attack":
        interaction_state = "targeting_attack"
        preview_target = None
    elif key == "wait":
        finish_selected_action()
    elif key == "item":
        interaction_state = "item_menu"


def handle_item_menu_click(selection):
    global interaction_state
    if selection == "back":
        interaction_state = "planning"
        return
    use_inventory_item(selection)


def handle_panel_click(position, start_button):
    if start_button.collidepoint(position) and phase == "VICTORY":
        return_to_chapter_select()
        return

    if start_button.collidepoint(position) and phase == "START":
        start_battle()
        return

    if phase in {"VICTORY", "DEFEAT"}:
        return

    if interaction_state not in {"planning", "item_menu"}:
        return

    clicked = panel_menu.get_clicked(position)
    if clicked is None:
        return

    selection = menu_actions.get(clicked)
    if interaction_state == "planning":
        handle_action_menu_click(selection)
    elif interaction_state == "item_menu":
        handle_item_menu_click(selection)


def handle_board_click(gx, gy):
    global interaction_state, preview_target, selected_unit

    clicked = game_map.get_unit(gx, gy)

    if interaction_state == "targeting_attack":
        if clicked in alive_units(enemies):
            execute_attack(clicked)
        return

    if interaction_state == "item_menu":
        return

    if clicked in alive_units(players) and not clicked.has_acted:
        if selected_unit is clicked:
            interaction_state = "planning"
        else:
            if selected_unit and not selected_unit.has_acted:
                revert_selected_to_original()
            select_unit_for_planning(clicked)
        return

    if not selected_unit or selected_unit.has_acted:
        return

    if interaction_state == "targeting_attack":
        return

    if (gx, gy) == selected_unit.get_position():
        interaction_state = "planning"
        return

    if can_plan_move(selected_unit, gx, gy):
        game_map.move_unit(selected_unit, gx, gy)
        update_selected_move_flag()
        interaction_state = "planning"


def handle_mouse_motion(position):
    global preview_target
    if scene != SCENE_GAME or phase != "PLAYER" or interaction_state != "targeting_attack":
        preview_target = None
        return

    gx = position[0] // CELL
    gy = (position[1] - BOARD_TOP) // CELL
    if not (0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE):
        preview_target = None
        return

    hovered = game_map.get_unit(gx, gy)
    if hovered in enemies_in_range(selected_unit):
        preview_target = hovered
    else:
        preview_target = None


def handle_menu_click(position):
    global scene
    if menu_button.collidepoint(position):
        scene = SCENE_CHAPTER_SELECT


def handle_chapter_select_click(position):
    global scene
    for chapter_id, rect in chapter_buttons.items():
        if rect.collidepoint(position):
            load_chapter(chapter_id)
            scene = SCENE_GAME
            return


def handle_game_click(position, start_button):
    if position[0] >= PANEL_X - 10:
        handle_panel_click(position, start_button)
        return

    if phase in {"VICTORY", "DEFEAT"}:
        return

    if phase != "PLAYER":
        return

    gx = position[0] // CELL
    gy = (position[1] - BOARD_TOP) // CELL
    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
        handle_board_click(gx, gy)


def init_game():
    init_state()
    init_runtime()
    init_ui()
    init_assets()

def draw_frame():
    screen.fill(WHITE)

    start_button = None
    if scene == SCENE_MENU:
        draw_menu_scene()
    elif scene == SCENE_CHAPTER_SELECT:
        draw_chapter_select_scene()
    elif scene == SCENE_GAME:
        start_button = draw_game_scene()

    return start_button


def handle_events(start_button):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos

            if scene == SCENE_MENU:
                handle_menu_click(mouse_pos)
            elif scene == SCENE_CHAPTER_SELECT:
                handle_chapter_select_click(mouse_pos)
            elif scene == SCENE_GAME and start_button is not None:
                handle_game_click(mouse_pos, start_button)

    return running


def update_frame():
    cleanup_dead_units()
    run_enemy_phase()


def run_frame():
    global FIRST_FRAME_LOGGED

    if IS_WEB and not FIRST_FRAME_LOGGED:
        startup_log("INSIDE first frame")
        FIRST_FRAME_LOGGED = True

    start_button = draw_frame()
    running = handle_events(start_button)
    update_frame()
    pygame.display.flip()
    return running


def show_startup_error(error_type, error_message):
    global pygame, screen

    try:
        if pygame is None:
            import pygame as _pygame

            pygame = _pygame

        if not hasattr(pygame, "get_init") or not pygame.get_init():
            return

        if screen is None:
            screen = pygame.display.set_mode((WIDTH, HEIGHT))

        error_font = pygame.font.SysFont(None, 34)
        detail_font = pygame.font.SysFont(None, 24)
        screen.fill((35, 35, 35))
        title = error_font.render("Startup failed", True, (255, 120, 120))
        detail = detail_font.render(f"{error_type}: {error_message}", True, WHITE)
        screen.blit(title, (40, 60))
        screen.blit(detail, (40, 120))
        pygame.display.flip()
    except Exception as render_error:
        startup_log(f"Startup error screen failed: {render_error}")


def shutdown():
    global pygame, screen, font, title_font, menu_title_font, menu_button_font
    global UNIT_SPRITES, TERRAIN_OVERLAYS, panel_menu, menu_button, chapter_buttons
    global FIRST_FRAME_LOGGED

    if pygame is not None and hasattr(pygame, "quit"):
        pygame.quit()
    pygame = None
    screen = None
    font = None
    title_font = None
    menu_title_font = None
    menu_button_font = None
    UNIT_SPRITES = {}
    TERRAIN_OVERLAYS = {}
    panel_menu = None
    menu_button = None
    chapter_buttons = {}
    FIRST_FRAME_LOGGED = False


def main():
    init_game()
    try:
        running = True
        while running:
            running = run_frame()
    finally:
        shutdown()
