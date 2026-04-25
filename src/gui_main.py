import math
import os
import sys

pygame = None

from ai import choose_destination, choose_target
from combat import (
    apply_attack_result,
    attack_preview,
    effective_attack_range,
    get_attack_tiles,
    get_attack_tiles_from_position,
    in_range,
    roll_attack_result,
)
from inventory import Antidote, Potion, item_label
from map import Map
from menu import VerticalMenu
from movement import can_move, find_shortest_move_path, get_reachable_tiles, get_reachable_tiles_from_position
from movement import get_move_tiles as movement_get_move_tiles
import progression
import sandbox
import save_system
import shop
from terrain import (
    TERRAIN_FORT,
    TERRAIN_GRASS,
    apply_end_turn_terrain_effect,
    build_terrain_overlays,
    draw_terrain_tile,
    get_terrain_data,
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
LOG_LINE_HEIGHT = 20
LOG_FOOTER_HEIGHT = 34

SCENE_MENU = "MENU"
SCENE_MODE_SELECT = "MODE_SELECT"
SCENE_CHAPTER_SELECT = "CHAPTER_SELECT"
SCENE_FACTION_SELECT = "FACTION_SELECT"
SCENE_SANDBOX_MAP = "SANDBOX_MAP"
SCENE_SANDBOX_BATTLE = "SANDBOX_BATTLE"
SCENE_SHOP = "SHOP"
SCENE_SAVE_MENU = "SAVE_MENU"
SCENE_LOAD_MENU = "LOAD_MENU"
SCENE_GAME = "GAME"

PREP_INVENTORY_LIMIT = 5

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
small_font = None
tiny_font = None
title_font = None
menu_title_font = None
menu_button_font = None
UNIT_SPRITES = {}
TERRAIN_OVERLAYS = {}
IS_WEB = sys.platform == "emscripten"
FIRST_FRAME_LOGGED = False
panel_menu = None
main_menu_buttons = {}
mode_select_buttons = {}
chapter_buttons = {}
faction_buttons = {}
sandbox_territory_buttons = {}
sandbox_city_unit_buttons = []
sandbox_field_unit_buttons = []
save_slot_buttons = {}
chapter_return_button = None
chapter_shop_button = None
sandbox_save_button = None
chapter_save_button = None
sandbox_shop_button = None
sandbox_send_button = None
sandbox_recall_button = None
shop_back_button = None
sandbox_back_button = None
slot_back_button = None
slot_clear_button = None

CHAPTERS = {
    1: {
        "name": "Chapter 1",
        "enemy_level": 1,
        "players": [
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
                "position": (3, 3),
            }
        ],
        "enemies": [
            {
                "name": "Enemy",
                "level": 1,
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
        "enemy_level": 3,
        "players": [
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
                "position": (2, 3),
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
                "position": (4, 3),
            },
        ],
        "enemies": [
            {
                "name": "Bandit",
                "level": 3,
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
                "level": 3,
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
    global pygame, screen, font, small_font, tiny_font, title_font, menu_title_font, menu_button_font

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
    small_font = pygame.font.SysFont(None, 20)
    tiny_font = pygame.font.SysFont(None, 16)
    title_font = pygame.font.SysFont(None, 30)
    menu_title_font = pygame.font.SysFont(None, 56)
    menu_button_font = pygame.font.SysFont(None, 34)


def init_ui():
    global panel_menu, main_menu_buttons, mode_select_buttons, chapter_buttons
    global faction_buttons, sandbox_territory_buttons, sandbox_city_unit_buttons, sandbox_field_unit_buttons
    global save_slot_buttons
    global chapter_return_button, chapter_shop_button, chapter_save_button
    global sandbox_shop_button, sandbox_save_button, sandbox_send_button, sandbox_recall_button
    global shop_back_button, sandbox_back_button, slot_back_button, slot_clear_button

    startup_log("BEFORE UI/runtime object creation")
    panel_menu = VerticalMenu(PANEL_X + PANEL_PADDING, PANEL_ACTION_Y + 34, PANEL_WIDTH - PANEL_PADDING * 2)
    main_menu_buttons = {
        "new": pygame.Rect(240, 320, 280, 64),
        "load": pygame.Rect(240, 415, 280, 64),
    }
    mode_select_buttons = {
        "chapter": pygame.Rect(240, 305, 280, 64),
        "sandbox": pygame.Rect(240, 400, 280, 64),
    }
    chapter_buttons = {
        1: pygame.Rect(235, 250, 290, 58),
        2: pygame.Rect(235, 335, 290, 58),
    }
    chapter_return_button = pygame.Rect(235, 600, 290, 58)
    chapter_shop_button = pygame.Rect(235, 430, 290, 58)
    chapter_save_button = pygame.Rect(235, 515, 290, 58)
    faction_buttons = {}
    for index, faction in enumerate(sandbox.PLAYABLE_FACTIONS):
        row = index // 2
        col = index % 2
        x = 85 + col * 300
        y = 230 + row * 95
        if index == len(sandbox.PLAYABLE_FACTIONS) - 1 and len(sandbox.PLAYABLE_FACTIONS) % 2 == 1:
            x = 230
        faction_buttons[faction["id"]] = pygame.Rect(x, y, 210, 58)

    sandbox_territory_buttons = {}
    sandbox_city_unit_buttons = [
        pygame.Rect(56 + (index % 3) * 124, 538 + (index // 3) * 56, 108, 46)
        for index in range(sandbox.MAX_GARRISON_UNITS)
    ]
    sandbox_field_unit_buttons = [
        pygame.Rect(36 + index * 76, 710, 68, 54)
        for index in range(sandbox.FIELD_TEAM_CAPACITY)
    ]
    sandbox_shop_button = pygame.Rect(PANEL_X, 640, PANEL_WIDTH, 42)
    sandbox_save_button = pygame.Rect(PANEL_X, 690, PANEL_WIDTH, 42)
    sandbox_send_button = pygame.Rect(PANEL_X, 520, PANEL_WIDTH, 42)
    sandbox_recall_button = pygame.Rect(PANEL_X, 570, PANEL_WIDTH, 42)
    shop_back_button = pygame.Rect(PANEL_X, 18, PANEL_WIDTH, 42)
    sandbox_back_button = pygame.Rect(PANEL_X, 740, PANEL_WIDTH, 42)
    slot_back_button = pygame.Rect(235, 680, 290, 50)
    slot_clear_button = pygame.Rect(235, 620, 290, 46)
    save_slot_buttons = {
        save_system.AUTO_SAVE_SLOT: pygame.Rect(80, 150, 600, 94),
        1: pygame.Rect(80, 260, 600, 94),
        2: pygame.Rect(80, 370, 600, 94),
        3: pygame.Rect(80, 480, 600, 94),
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
battle_log_scroll = 0
menu_actions = {}

scene = SCENE_MENU
selected_chapter_id = None
battle_title = "No Battle"
battle_mode = "chapter"
chapter_state = {}
persistent_roster = {}
sandbox_state = None
selected_sandbox_territory_id = None
selected_sandbox_source_id = None
sandbox_battle_target_id = None
sandbox_battle_result = None
victory_saved = False
sandbox_result_applied = False
shop_return_scene = SCENE_MENU
shop_context = "chapter"
shop_message = ""
save_menu_mode = "save"
save_return_scene = SCENE_MENU
save_message = ""
pending_save_slot = None
active_save_slot = None
slot_clear_mode = False
combat_animation = None
combat_speed = 1
enemy_phase_queue = []
attack_confirmation_target = None
attack_confirmation_position = None
threat_enemy_unit = None
level_up_popups = []
pending_combat_resolution = None
action_panel_scroll = 0
action_entry_buttons = []
last_battle_sidebar_layout = None
hovered_board_tile = None
selected_board_tile = None
movement_preview_path = []

RANGE_DEBUG = False


def init_state():
    global game_map, players, enemies, selected_unit, original_position, preview_target
    global turn, phase, interaction_state, battle_log, battle_log_scroll, menu_actions
    global scene, selected_chapter_id, battle_title, battle_mode
    global chapter_state, persistent_roster, sandbox_state
    global selected_sandbox_territory_id, selected_sandbox_source_id, sandbox_battle_target_id, sandbox_battle_result
    global victory_saved, sandbox_result_applied
    global shop_return_scene, shop_context, shop_message
    global save_menu_mode, save_return_scene, save_message, pending_save_slot, active_save_slot, slot_clear_mode
    global combat_animation, combat_speed, enemy_phase_queue
    global attack_confirmation_target, attack_confirmation_position, threat_enemy_unit
    global level_up_popups, pending_combat_resolution
    global action_panel_scroll, action_entry_buttons, last_battle_sidebar_layout
    global hovered_board_tile, selected_board_tile, movement_preview_path
    global hovered_board_tile, selected_board_tile, movement_preview_path
    global hovered_board_tile, selected_board_tile, movement_preview_path
    global action_panel_scroll, action_entry_buttons, last_battle_sidebar_layout

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
    battle_log_scroll = 0
    menu_actions = {}
    scene = SCENE_MENU
    selected_chapter_id = None
    battle_title = "No Battle"
    battle_mode = "chapter"
    chapter_state = {}
    persistent_roster = {}
    sandbox_state = None
    selected_sandbox_territory_id = None
    selected_sandbox_source_id = None
    sandbox_battle_target_id = None
    sandbox_battle_result = None
    victory_saved = False
    sandbox_result_applied = False
    shop_return_scene = SCENE_MENU
    shop_context = "chapter"
    shop_message = ""
    save_menu_mode = "save"
    save_return_scene = SCENE_MENU
    save_message = ""
    pending_save_slot = None
    active_save_slot = None
    slot_clear_mode = False
    combat_animation = None
    combat_speed = 1
    enemy_phase_queue = []
    attack_confirmation_target = None
    attack_confirmation_position = None
    threat_enemy_unit = None
    level_up_popups = []
    pending_combat_resolution = None
    action_panel_scroll = 0
    action_entry_buttons = []
    last_battle_sidebar_layout = None
    hovered_board_tile = None
    selected_board_tile = None
    movement_preview_path = []
    hovered_board_tile = None
    selected_board_tile = None
    movement_preview_path = []
    hovered_board_tile = None
    selected_board_tile = None
    movement_preview_path = []
    action_panel_scroll = 0
    action_entry_buttons = []
    last_battle_sidebar_layout = None
    new_game_state()


def create_unit(spec):
    if "unit_id" in spec and spec["unit_id"] in persistent_roster:
        return progression.instantiate_player_unit(persistent_roster[spec["unit_id"]], spec["position"])
    return progression.create_enemy_unit(spec)


def create_chapter_state():
    return {
        "gold": shop.STARTING_GOLD,
        "convoy": [],
        "shop_stock": shop.create_shop_stock(),
        "chapter_progress": {
            "clears": {"1": 0, "2": 0},
            "unlocked": [1, 2],
        },
    }


def sync_sandbox_gold():
    if not chapter_state or not sandbox_state:
        return

    player_faction = sandbox.get_player_faction(sandbox_state)
    if player_faction:
        sandbox_state["treasuries"][player_faction] = chapter_state["gold"]
    sandbox_state["convoy"] = chapter_state["convoy"]
    sandbox_state["shop_stock"] = chapter_state["shop_stock"]


def sync_gold_from_sandbox():
    if not chapter_state or not sandbox_state:
        return

    player_faction = sandbox.get_player_faction(sandbox_state)
    if player_faction:
        chapter_state["gold"] = sandbox_state["treasuries"][player_faction]
        sandbox_state["treasuries"][player_faction] = chapter_state["gold"]


def apply_game_state(game_state):
    global chapter_state, persistent_roster, sandbox_state

    chapter_state = game_state["chapter_state"]
    persistent_roster = game_state["roster"]
    sandbox_state = game_state["sandbox_state"]
    sync_sandbox_gold()


def build_runtime_game_state():
    sync_sandbox_gold()
    return {
        "chapter_state": chapter_state,
        "sandbox_state": sandbox_state,
        "roster": persistent_roster,
    }


def new_game_state():
    game_state = save_system.new_game_state()
    apply_game_state(game_state)
    return game_state


def start_new_chapter_game():
    global scene, selected_chapter_id, selected_sandbox_territory_id, selected_sandbox_source_id
    global active_save_slot

    new_game_state()
    active_save_slot = None
    selected_chapter_id = None
    selected_sandbox_territory_id = None
    selected_sandbox_source_id = None
    scene = SCENE_CHAPTER_SELECT


def start_new_sandbox_game():
    global scene, selected_sandbox_territory_id, selected_sandbox_source_id
    global active_save_slot

    new_game_state()
    active_save_slot = None
    selected_sandbox_territory_id = None
    selected_sandbox_source_id = None
    scene = SCENE_FACTION_SELECT


def build_resume_context():
    if scene == SCENE_CHAPTER_SELECT:
        return {"scene": "CHAPTER_SELECT"}
    if scene == SCENE_SANDBOX_MAP:
        return {
            "scene": "SANDBOX_MAP",
            "selected_territory_id": selected_sandbox_territory_id,
        }
    if scene == SCENE_GAME and selected_chapter_id is not None:
        if phase == "START":
            return {"scene": "CHAPTER_PREP", "chapter_id": selected_chapter_id}
        return {"scene": "CHAPTER_SELECT"}
    if scene == SCENE_SANDBOX_BATTLE and sandbox_battle_target_id is not None:
        if phase == "START":
            return {"scene": "SANDBOX_PREP", "territory_id": sandbox_battle_target_id}
        return {
            "scene": "SANDBOX_MAP",
            "selected_territory_id": sandbox_battle_target_id,
        }
    return {"scene": "MENU"}


def restore_loaded_context(resume_context):
    global scene, selected_sandbox_territory_id, selected_sandbox_source_id

    resume_scene = resume_context.get("scene", "MENU")

    if resume_scene == "CHAPTER_SELECT":
        scene = SCENE_CHAPTER_SELECT
        return

    if resume_scene == "CHAPTER_PREP":
        chapter_id = resume_context.get("chapter_id")
        if chapter_id in CHAPTERS:
            load_chapter(chapter_id)
            return
        scene = SCENE_CHAPTER_SELECT
        return

    if resume_scene == "SANDBOX_MAP":
        player_faction = sandbox.get_player_faction(sandbox_state)
        if player_faction is None:
            scene = SCENE_FACTION_SELECT
            return
        selected_sandbox_territory_id = resume_context.get("selected_territory_id")
        if sandbox.get_territory(sandbox_state, selected_sandbox_territory_id) is None:
            owned_territories = [
                territory["id"]
                for territory in sandbox.iter_territories(sandbox_state)
                if territory["owner_faction"] == player_faction
            ]
            selected_sandbox_territory_id = owned_territories[0] if owned_territories else None
        selected_sandbox_source_id = (
            selected_sandbox_territory_id
            if selected_sandbox_territory_id is not None
            and sandbox.is_player_owned(sandbox_state, selected_sandbox_territory_id)
            else None
        )
        scene = SCENE_SANDBOX_MAP
        return

    if resume_scene == "SANDBOX_PREP":
        territory_id = resume_context.get("territory_id")
        if territory_id is not None and sandbox.get_territory(sandbox_state, territory_id) is not None:
            start_sandbox_battle(territory_id)
            return
        scene = SCENE_FACTION_SELECT
        return

    scene = SCENE_MENU


def load_game(slot):
    global active_save_slot

    loaded = save_system.load_game_from_slot(slot)
    if loaded is None:
        return False

    apply_game_state(loaded["game_state"])
    active_save_slot = slot
    restore_loaded_context(loaded.get("resume", {}))
    return True


def save_game(slot=None):
    global active_save_slot

    if slot is None:
        slot = active_save_slot
    if slot is None:
        return False

    success = save_system.save_game_to_slot(slot, build_runtime_game_state(), build_resume_context())
    if success:
        active_save_slot = slot
    return success


def get_mode_state(mode):
    return chapter_state


def get_gold_for_mode(mode):
    if not chapter_state:
        return 0
    return chapter_state["gold"]


def add_gold_for_mode(mode, amount):
    if not chapter_state:
        return False
    chapter_state["gold"] = max(0, chapter_state["gold"] + amount)
    sync_sandbox_gold()
    return True


def get_convoy_for_mode(mode):
    if not chapter_state:
        return []
    return chapter_state["convoy"]


def get_shop_stock_for_mode(mode):
    if not chapter_state:
        return {}
    return chapter_state["shop_stock"]


def get_preparation_mode():
    return "sandbox" if battle_mode == "sandbox" else "chapter"


def open_slot_menu(mode, return_scene):
    global scene, save_menu_mode, save_return_scene, save_message, pending_save_slot, slot_clear_mode

    save_menu_mode = mode
    save_return_scene = return_scene
    save_message = ""
    pending_save_slot = None
    slot_clear_mode = False
    scene = SCENE_SAVE_MENU if mode == "save" else SCENE_LOAD_MENU


def open_shop(return_scene, mode):
    global scene, shop_return_scene, shop_context, shop_message

    shop_return_scene = return_scene
    shop_context = mode
    shop_message = "Choose an item to add to convoy."
    scene = SCENE_SHOP


def close_shop():
    global scene
    scene = shop_return_scene


def close_slot_menu():
    global scene
    scene = save_return_scene


def handle_save_slot(slot):
    global pending_save_slot, save_message

    if slot == save_system.AUTO_SAVE_SLOT:
        save_message = "Auto Save is updated only after Victory."
        return

    slot_info = next(info for info in save_system.list_save_slots() if info["slot"] == slot)
    if slot_info["exists"] and pending_save_slot != slot:
        pending_save_slot = slot
        save_message = f"Slot {slot} already has data. Click again to overwrite."
        return

    if save_game(slot):
        save_message = f"Saved to Slot {slot}."
        close_slot_menu()
    else:
        save_message = f"Save to Slot {slot} failed."


def handle_load_slot(slot):
    global save_message

    slot_info = next(info for info in save_system.list_save_slots(include_auto=True) if info["slot"] == slot)
    if not slot_info["exists"] or slot_info["corrupt"]:
        slot_name = "Auto Save" if slot == save_system.AUTO_SAVE_SLOT else f"Slot {slot}"
        save_message = f"{slot_name} cannot be loaded."
        return

    if load_game(slot):
        slot_name = "Auto Save" if slot == save_system.AUTO_SAVE_SLOT else f"Slot {slot}"
        save_message = f"Loaded {slot_name}."
    else:
        slot_name = "Auto Save" if slot == save_system.AUTO_SAVE_SLOT else f"Slot {slot}"
        save_message = f"Load from {slot_name} failed."


def auto_save_game():
    return save_system.save_game_to_slot(
        save_system.AUTO_SAVE_SLOT,
        build_runtime_game_state(),
        build_resume_context(),
    )


def handle_clear_slot(slot):
    global pending_save_slot, save_message, active_save_slot, slot_clear_mode

    if slot == save_system.AUTO_SAVE_SLOT:
        save_message = "Auto Save cannot be cleared."
        return

    if pending_save_slot != slot:
        pending_save_slot = slot
        save_message = f"Click Slot {slot} again to clear it."
        return

    if save_system.clear_save_slot(slot):
        if active_save_slot == slot:
            active_save_slot = None
        save_message = f"Cleared Slot {slot}."
    else:
        save_message = f"Clear Slot {slot} failed."
    pending_save_slot = None
    slot_clear_mode = False


def buy_shop_item(item_id):
    global shop_message

    item_data = shop.get_item(item_id)
    stock = get_shop_stock_for_mode(shop_context)
    remaining = stock.get(item_id, 0)
    if remaining <= 0:
        shop_message = f"{item_data['name']} is out of stock."
        return

    if get_gold_for_mode(shop_context) < item_data["price"]:
        shop_message = "Not enough gold."
        return

    add_gold_for_mode(shop_context, -item_data["price"])
    stock[item_id] = remaining - 1
    get_convoy_for_mode(shop_context).append(shop.create_item(item_id))
    shop_message = f"Bought {item_data['name']}."


def load_battle_setup(setup):
    global game_map, players, enemies, battle_log, turn, phase
    global interaction_state, selected_unit, original_position, preview_target, battle_log_scroll
    global victory_saved, sandbox_result_applied
    global combat_animation, enemy_phase_queue
    global attack_confirmation_target, attack_confirmation_position, threat_enemy_unit
    global level_up_popups, pending_combat_resolution

    game_map = Map()
    players = []
    enemies = []

    for player_spec in setup["players"]:
        unit = create_unit(player_spec)
        players.append(unit)
        px, py = player_spec["position"]
        game_map.place_unit(unit, px, py)

    for enemy_spec in setup["enemies"]:
        unit = create_unit(enemy_spec)
        enemies.append(unit)
        ex, ey = enemy_spec["position"]
        game_map.place_unit(unit, ex, ey)

    for terrain_type, tx, ty in setup.get("terrain", []):
        game_map.set_terrain(tx, ty, terrain_type)

    turn = 1
    phase = "START"
    interaction_state = "idle"
    selected_unit = None
    original_position = None
    preview_target = None
    victory_saved = False
    sandbox_result_applied = False
    battle_log = [f"{setup['name']} loaded."]
    battle_log_scroll = 0
    combat_animation = None
    enemy_phase_queue = []
    attack_confirmation_target = None
    attack_confirmation_position = None
    threat_enemy_unit = None
    level_up_popups = []
    pending_combat_resolution = None


def load_chapter(chapter_id):
    global selected_chapter_id, battle_title, battle_mode, scene
    global sandbox_battle_target_id, sandbox_battle_result

    chapter = CHAPTERS[chapter_id]
    selected_chapter_id = chapter_id
    battle_title = chapter["name"]
    battle_mode = "chapter"
    sandbox_battle_target_id = None
    sandbox_battle_result = None
    load_battle_setup(chapter)
    scene = SCENE_GAME


def enter_sandbox_mode():
    global scene, selected_sandbox_territory_id, selected_sandbox_source_id

    selected_sandbox_territory_id = None
    selected_sandbox_source_id = None
    scene = SCENE_FACTION_SELECT


def choose_sandbox_faction(faction_id):
    global scene, selected_sandbox_territory_id, selected_sandbox_source_id

    sandbox.set_player_faction(sandbox_state, faction_id)
    sync_sandbox_gold()
    owned_territories = [
        territory["id"]
        for territory in sandbox.iter_territories(sandbox_state)
        if territory["owner_faction"] == faction_id
    ]
    selected_sandbox_territory_id = owned_territories[0] if owned_territories else None
    selected_sandbox_source_id = selected_sandbox_territory_id
    scene = SCENE_SANDBOX_MAP


def start_sandbox_battle(territory_id):
    global battle_title, battle_mode, scene, selected_chapter_id
    global sandbox_battle_target_id, sandbox_battle_result

    setup = sandbox.build_battle_setup(sandbox_state, territory_id)
    if setup is None:
        return

    battle_title = setup["name"]
    battle_mode = "sandbox"
    selected_chapter_id = None
    sandbox_battle_target_id = territory_id
    sandbox_battle_result = None
    load_battle_setup(setup)
    scene = SCENE_SANDBOX_BATTLE


def sync_roster_from_players():
    for unit in alive_units(players):
        if unit.unit_id in persistent_roster:
            persistent_roster[unit.unit_id] = progression.serialize_unit(unit)


def handle_victory_persistence():
    global victory_saved, sandbox_result_applied, selected_sandbox_territory_id, selected_sandbox_source_id

    if victory_saved:
        return

    sync_roster_from_players()

    if battle_mode == "chapter" and selected_chapter_id is not None:
        chapter_state["chapter_progress"]["clears"][str(selected_chapter_id)] += 1

    if battle_mode == "sandbox" and sandbox_battle_target_id is not None and not sandbox_result_applied:
        sandbox.apply_battle_result(sandbox_state, sandbox_battle_target_id, True)
        sandbox_result_applied = True
        selected_sandbox_territory_id = sandbox_battle_target_id
        selected_sandbox_source_id = (
            sandbox_battle_target_id
            if sandbox.is_player_owned(sandbox_state, sandbox_battle_target_id)
            else selected_sandbox_source_id
        )
        sync_gold_from_sandbox()

    auto_save_game()
    victory_saved = True


def current_chapter_name():
    if battle_title == "No Battle":
        return "No Chapter"
    return battle_title


def in_tactical_battle_scene():
    return scene in {SCENE_GAME, SCENE_SANDBOX_BATTLE}


def alive_units(units):
    return [unit for unit in units if unit.is_alive()]


def select_unit_for_planning(unit):
    global selected_unit, original_position, interaction_state, preview_target, action_panel_scroll
    selected_unit = unit
    original_position = unit.get_position()
    selected_unit.has_moved = False
    interaction_state = "planning"
    preview_target = None
    action_panel_scroll = 0
    clear_threat_enemy()
    clear_attack_forecast()


def select_unit_for_preparation(unit):
    global selected_unit, original_position, interaction_state, preview_target, action_panel_scroll

    selected_unit = unit
    original_position = unit.get_position()
    interaction_state = "prep_menu"
    preview_target = None
    action_panel_scroll = 0
    clear_attack_forecast()


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
    global attack_confirmation_target, attack_confirmation_position
    global movement_preview_path
    selected_unit = None
    original_position = None
    interaction_state = "idle"
    preview_target = None
    attack_confirmation_target = None
    attack_confirmation_position = None
    movement_preview_path = []


def clear_attack_forecast():
    global preview_target, attack_confirmation_target, attack_confirmation_position
    preview_target = None
    attack_confirmation_target = None
    attack_confirmation_position = None


def cancel_attack_targeting():
    global interaction_state
    if interaction_state != "targeting_attack":
        return
    if attack_confirmation_target is not None:
        clear_attack_forecast()
        return
    interaction_state = "planning"
    clear_attack_forecast()


def toggle_threat_enemy(unit):
    global threat_enemy_unit
    if threat_enemy_unit is unit:
        threat_enemy_unit = None
    else:
        threat_enemy_unit = unit


def clear_threat_enemy():
    global threat_enemy_unit
    threat_enemy_unit = None


def add_log(message):
    add_logs([message])


def add_logs(messages):
    global battle_log_scroll

    new_messages = [message for message in messages if message]
    if not new_messages:
        return

    if battle_log_scroll > 0:
        battle_log_scroll += len(new_messages)
    battle_log.extend(new_messages)
    clamp_log_scroll()


def get_log_visible_count():
    layout = last_battle_sidebar_layout or get_battle_sidebar_layout()
    return max(1, (layout["log_rect"].height - 50 - LOG_FOOTER_HEIGHT) // LOG_LINE_HEIGHT)


def get_max_log_scroll():
    return max(0, len(battle_log) - get_log_visible_count())


def clamp_log_scroll():
    global battle_log_scroll
    battle_log_scroll = max(0, min(battle_log_scroll, get_max_log_scroll()))


def scroll_battle_log(delta):
    global battle_log_scroll

    if phase == "START":
        return

    battle_log_scroll = max(0, min(battle_log_scroll + delta, get_max_log_scroll()))


def get_hovered_tactical_panel(mouse_pos):
    layout = last_battle_sidebar_layout
    if not layout:
        return None
    if layout["action_rect"].collidepoint(mouse_pos):
        return "action"
    if layout["log_rect"].collidepoint(mouse_pos):
        return "log"
    return None


def can_take_convoy_item(unit):
    return unit is not None and len(unit.inventory) < PREP_INVENTORY_LIMIT


def can_take_specific_item(unit, item):
    return can_take_convoy_item(unit)


def is_incompatible_weapon(unit, item):
    return (
        unit is not None
        and getattr(item, "item_type", None) == "weapon"
        and not unit.can_equip_weapon(item)
    )


def build_prep_menu():
    convoy = get_convoy_for_mode(get_preparation_mode())

    if not selected_unit:
        return [
            {"key": "shop", "label": "Shop", "enabled": True},
            {"key": "save_game", "label": "Save Game", "enabled": True},
        ]

    if interaction_state == "prep_equip":
        options = []
        for index, item in enumerate(selected_unit.inventory):
            label = item_label(item)
            if item is selected_unit.weapon:
                label = f"{label} [Equipped]"
            elif is_incompatible_weapon(selected_unit, item):
                label = f"{label} [Unusable]"
            options.append(
                {
                    "key": f"prep_equip:{index}",
                    "label": label,
                    "enabled": getattr(item, "item_type", None) == "weapon",
                    "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
                }
            )
        options.append({"key": "prep_back", "label": "Back", "enabled": True})
        return options

    if interaction_state == "prep_store":
        options = [
            {
                "key": f"prep_store:{index}",
                "label": f"Store {item_label(item)}",
                "enabled": True,
            }
            for index, item in enumerate(selected_unit.inventory)
        ]
        options.append({"key": "prep_back", "label": "Back", "enabled": True})
        return options

    if interaction_state == "prep_take":
        options = [
            {
                "key": f"prep_take:{index}",
                "label": (
                    f"Take {item_label(item)} [Carry Only]"
                    if is_incompatible_weapon(selected_unit, item)
                    else f"Take {item_label(item)}"
                ),
                "enabled": can_take_specific_item(selected_unit, item),
                "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
            }
            for index, item in enumerate(convoy)
        ]
        options.append({"key": "prep_back", "label": "Back", "enabled": True})
        return options

    has_weapons = any(getattr(item, "item_type", None) == "weapon" for item in selected_unit.inventory)
    return [
        {"key": "prep_equip", "label": "Equip Weapon", "enabled": has_weapons},
        {"key": "prep_store", "label": "Store Item", "enabled": bool(selected_unit.inventory)},
        {
            "key": "prep_take",
            "label": f"Take From Convoy ({len(convoy)})",
            "enabled": bool(convoy) and can_take_convoy_item(selected_unit),
        },
        {"key": "shop", "label": "Shop", "enabled": True},
        {"key": "save_game", "label": "Save Game", "enabled": True},
        {"key": "prep_clear", "label": "Done", "enabled": True},
    ]


def handle_prep_menu_click(selection):
    global interaction_state, action_panel_scroll

    if selection == "shop":
        open_shop(scene, get_preparation_mode())
        return

    if selection == "save_game":
        open_slot_menu("save", scene)
        return

    if selection == "prep_clear":
        clear_selection()
        return

    if selection == "prep_back":
        interaction_state = "prep_menu"
        action_panel_scroll = 0
        return

    if selection in {"prep_equip", "prep_store", "prep_take"}:
        interaction_state = selection
        action_panel_scroll = 0
        return

    if not selected_unit:
        return

    convoy = get_convoy_for_mode(get_preparation_mode())

    if selection.startswith("prep_equip:"):
        index = int(selection.split(":")[1])
        if 0 <= index < len(selected_unit.inventory):
            item = selected_unit.inventory[index]
            if selected_unit.equip_weapon(item):
                add_log(f"{selected_unit.name} equipped {item.name}")
            elif getattr(item, "item_type", None) == "weapon":
                add_log(f"{selected_unit.name} cannot equip {item.name}")
        interaction_state = "prep_menu"
        action_panel_scroll = 0
        return

    if selection.startswith("prep_store:"):
        index = int(selection.split(":")[1])
        if 0 <= index < len(selected_unit.inventory):
            item = selected_unit.inventory[index]
            if selected_unit.remove_item(item):
                convoy.append(item)
                add_log(f"{selected_unit.name} stored {item.name}")
        interaction_state = "prep_menu"
        action_panel_scroll = 0
        return

    if selection.startswith("prep_take:"):
        index = int(selection.split(":")[1])
        if 0 <= index < len(convoy) and can_take_specific_item(selected_unit, convoy[index]):
            item = convoy.pop(index)
            selected_unit.inventory.append(item)
            if selected_unit.weapon is None and selected_unit.can_equip_weapon(item):
                selected_unit.equip_weapon(item)
            add_log(f"{selected_unit.name} took {item.name}")
        interaction_state = "prep_menu"
        action_panel_scroll = 0


def apply_end_turn_effects(unit):
    if not unit or not unit.is_alive() or not unit.game_map:
        return

    x, y = unit.get_position()
    terrain_type = unit.game_map.get_terrain(x, y)
    delta = apply_end_turn_terrain_effect(unit, terrain_type)
    if delta > 0:
        add_log(f"{unit.name} recovered {delta} HP on {terrain_type.replace('_', ' ').title()}")
    elif delta < 0:
        add_log(f"{unit.name} suffered {-delta} terrain damage on {terrain_type.replace('_', ' ').title()}")


def append_combat_log(entries):
    add_logs(
        [
            f"{name} {'CRIT' if critical else 'HIT' if hit else 'MISS'} dmg:{dmg}"
            for name, hit, dmg, critical in entries
        ]
    )


def queue_level_up_popups(level_up_results):
    if not level_up_results:
        return
    level_up_popups.extend(level_up_results)


def complete_post_combat_resolution(owner, acting_unit):
    if phase in {"VICTORY", "DEFEAT"}:
        return
    if owner == "player":
        if selected_unit is acting_unit:
            finish_selected_action()
        else:
            clear_selection()
            if phase == "PLAYER" and all_players_acted():
                begin_enemy_phase()
    else:
        finish_enemy_turn(acting_unit)


def get_combat_speed_durations():
    speed_scale = max(1, combat_speed)
    return {
        "lunge": 320 / speed_scale,
        "impact": 220 / speed_scale,
        "return": 320 / speed_scale,
        "pause": 140 / speed_scale,
    }


def get_attack_direction(attacker, defender):
    ax, ay = attacker.get_position()
    dx = defender.x - ax
    dy = defender.y - ay
    magnitude = max(1, abs(dx) + abs(dy))
    return dx / magnitude, dy / magnitude


def create_attack_swing(attacker, defender):
    return {
        "attacker": attacker,
        "defender": defender,
        "attack_result": roll_attack_result(attacker, defender),
        "stage": "lunge",
        "elapsed": 0,
        "impact_applied": False,
    }


def start_combat_animation(attacker, defender, owner):
    global combat_animation, preview_target

    if (
        combat_animation is not None
        or attacker is None
        or defender is None
        or not attacker.is_alive()
        or not defender.is_alive()
        or not attacker.weapon
    ):
        return False

    combat_animation = {
        "owner": owner,
        "acting_unit": attacker,
        "primary_attacker": attacker,
        "primary_defender": defender,
        "awarded_exp": {attacker: 0, defender: 0},
        "current_swing": create_attack_swing(attacker, defender),
        "sequence_index": 0,
        "counter_allowed": in_range(defender, attacker),
        "attacker_follow_up": attacker.speed - defender.speed >= 4,
        "defender_follow_up": defender.speed - attacker.speed >= 4 and in_range(defender, attacker),
        "last_tick": pygame.time.get_ticks(),
    }
    preview_target = defender
    return True


def resolve_animation_impact():
    swing = combat_animation["current_swing"]
    if swing["impact_applied"]:
        return

    applied = apply_attack_result(
        swing["attacker"],
        swing["defender"],
        swing["attack_result"],
        combat_animation["awarded_exp"],
    )
    append_combat_log([applied["attack"]])
    add_logs(applied["events"])
    queue_level_up_popups(applied.get("level_ups", []))
    swing["impact_applied"] = True


def finish_enemy_turn(enemy_unit):
    global turn

    apply_end_turn_effects(enemy_unit)
    if enemy_phase_queue and enemy_phase_queue[0] is enemy_unit:
        enemy_phase_queue.pop(0)
    elif enemy_unit in enemy_phase_queue:
        enemy_phase_queue.remove(enemy_unit)

    if phase == "ENEMY" and not enemy_phase_queue:
        turn += 1
        begin_player_phase()


def finish_combat_animation():
    global combat_animation, pending_combat_resolution

    if combat_animation is None:
        return

    owner = combat_animation["owner"]
    acting_unit = combat_animation["acting_unit"]
    combat_animation = None
    cleanup_dead_units()
    pending_combat_resolution = {"owner": owner, "acting_unit": acting_unit}
    if level_up_popups:
        return
    complete_post_combat_resolution(owner, acting_unit)
    pending_combat_resolution = None


def advance_combat_animation_stage():
    if combat_animation is None:
        return

    swing = combat_animation["current_swing"]
    if swing["stage"] == "lunge":
        swing["stage"] = "impact"
        swing["elapsed"] = 0
        resolve_animation_impact()
        return

    if swing["stage"] == "impact":
        swing["stage"] = "return"
        swing["elapsed"] = 0
        return

    if swing["stage"] == "return":
        swing["stage"] = "pause"
        swing["elapsed"] = 0
        return

    primary_attacker = combat_animation["primary_attacker"]
    primary_defender = combat_animation["primary_defender"]
    next_index = combat_animation["sequence_index"] + 1

    if next_index == 1:
        if (
            combat_animation["counter_allowed"]
            and primary_defender.is_alive()
            and primary_attacker.is_alive()
            and primary_defender.has_usable_weapon()
            and in_range(primary_defender, primary_attacker)
        ):
            combat_animation["sequence_index"] = next_index
            combat_animation["current_swing"] = create_attack_swing(primary_defender, primary_attacker)
            return
        next_index += 1

    if next_index == 2:
        if (
            combat_animation["attacker_follow_up"]
            and primary_attacker.is_alive()
            and primary_defender.is_alive()
            and primary_attacker.has_usable_weapon()
            and in_range(primary_attacker, primary_defender)
        ):
            combat_animation["sequence_index"] = next_index
            combat_animation["current_swing"] = create_attack_swing(primary_attacker, primary_defender)
            return
        if (
            combat_animation["defender_follow_up"]
            and primary_defender.is_alive()
            and primary_attacker.is_alive()
            and primary_defender.has_usable_weapon()
            and in_range(primary_defender, primary_attacker)
        ):
            combat_animation["sequence_index"] = next_index
            combat_animation["current_swing"] = create_attack_swing(primary_defender, primary_attacker)
            return

    finish_combat_animation()


def update_combat_animation():
    if combat_animation is None:
        return

    now = pygame.time.get_ticks()
    elapsed = max(0, now - combat_animation["last_tick"])
    combat_animation["last_tick"] = now
    durations = get_combat_speed_durations()

    while combat_animation is not None and elapsed >= 0:
        swing = combat_animation["current_swing"]
        duration = durations[swing["stage"]]
        remaining = duration - swing["elapsed"]
        step = min(elapsed, remaining)
        swing["elapsed"] += step
        elapsed -= step

        if swing["elapsed"] < duration:
            break

        advance_combat_animation_stage()
        if elapsed <= 0:
            break


def dismiss_level_up_popup():
    global pending_combat_resolution

    if not level_up_popups:
        return

    level_up_popups.pop(0)
    if not level_up_popups and pending_combat_resolution is not None:
        complete_post_combat_resolution(
            pending_combat_resolution["owner"],
            pending_combat_resolution["acting_unit"],
        )
        pending_combat_resolution = None


def get_unit_draw_offset(unit):
    if combat_animation is None:
        return 0, 0

    swing = combat_animation["current_swing"]
    attacker = swing["attacker"]
    defender = swing["defender"]
    direction_x, direction_y = get_attack_direction(attacker, defender)
    lunge_distance = CELL * 0.5
    durations = get_combat_speed_durations()
    progress = 0.0
    if durations[swing["stage"]] > 0:
        progress = min(1.0, swing["elapsed"] / durations[swing["stage"]])

    if unit is attacker:
        if swing["stage"] == "lunge":
            scale = progress
        elif swing["stage"] == "impact":
            scale = 1.0
        elif swing["stage"] == "return":
            scale = 1.0 - progress
        else:
            scale = 0.0
        return direction_x * lunge_distance * scale, direction_y * lunge_distance * scale

    if unit is defender and swing["stage"] == "impact" and swing["attack_result"]["hit"]:
        amplitude = 4
        wave = math.sin(progress * math.pi * 8)
        return -direction_y * amplitude * wave, direction_x * amplitude * wave

    return 0, 0


def is_animation_blocking_input():
    return combat_animation is not None


def debug_range_snapshot(unit, move_tiles, attack_tiles):
    if not RANGE_DEBUG or unit is None:
        return
    right_edge_move_tiles = sorted(tile for tile in move_tiles if tile[0] == GRID_SIZE - 1)
    right_edge_attack_tiles = sorted(tile for tile in attack_tiles if tile[0] == GRID_SIZE - 1)
    print(
        f"[range-debug] {unit.name} move={unit.move} "
        f"move_tiles={len(move_tiles)} attack_tiles={len(attack_tiles)} "
        f"right_move={right_edge_move_tiles} right_attack={right_edge_attack_tiles}"
    )


def get_move_tiles(unit, game_map_obj, units=None):
    if unit is None:
        return set()
    if unit is selected_unit and original_position is not None:
        move_tiles = movement_get_move_tiles(
            unit,
            game_map_obj,
            units=units,
            origin=original_position,
            include_origin=False,
        )
    else:
        move_tiles = movement_get_move_tiles(unit, game_map_obj, units=units, include_origin=False)
    assert all(game_map_obj.in_bounds(*tile) for tile in move_tiles)
    return move_tiles


def get_attack_tiles(unit, game_map_obj, units=None):
    del units
    if unit is None or not unit.has_usable_weapon():
        return set()

    if unit is selected_unit and original_position is not None:
        origin_tile = original_position
    else:
        origin_tile = unit.get_position()

    move_tiles = get_move_tiles(unit, game_map_obj)
    attack_tiles = set(get_attack_tiles_from_position(origin_tile, unit.weapon, game_map_obj))
    for origin in move_tiles:
        attack_tiles.update(get_attack_tiles_from_position(origin, unit.weapon, game_map_obj))

    attack_tiles.discard(origin_tile)
    attack_tiles = {tile for tile in attack_tiles if game_map_obj.in_bounds(*tile)}
    debug_range_snapshot(unit, move_tiles, attack_tiles)
    return attack_tiles


def get_move_range(unit, game_map_obj=None):
    game_map_obj = game_map_obj or game_map
    return sorted(get_move_tiles(unit, game_map_obj))


def get_attack_range(unit, game_map_obj=None):
    game_map_obj = game_map_obj or game_map
    return sorted(get_attack_tiles(unit, game_map_obj))


def get_enemy_threat_ranges(unit):
    if not unit or not unit.is_alive():
        return [], []

    move_set = movement_get_move_tiles(unit, game_map, include_origin=True)
    threat_tiles = set(get_attack_tiles(unit, game_map))
    current_tile = unit.get_position()
    if current_tile is not None:
        threat_tiles.update(get_attack_tiles_from_position(current_tile, unit.weapon, game_map))
    threat_only = sorted(threat_tiles - move_set)
    return sorted(move_set), threat_only


def find_shortest_move_path_for_preview(unit, destination):
    if unit is None or original_position is None:
        return []
    if destination == original_position:
        return [original_position]
    return find_shortest_move_path(unit, game_map, original_position, destination)


def draw_path_arrows():
    if len(movement_preview_path) < 2:
        return

    outer_color = (242, 205, 88)
    inner_color = (108, 82, 26)
    centers = [
        (tile_x * CELL + CELL // 2, tile_y * CELL + BOARD_TOP + CELL // 2)
        for tile_x, tile_y in movement_preview_path
    ]

    for start, end in zip(centers, centers[1:]):
        pygame.draw.line(screen, outer_color, start, end, 8)
        pygame.draw.line(screen, inner_color, start, end, 3)

    if len(centers) >= 2:
        start = centers[-2]
        end = centers[-1]
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = max(1, math.hypot(dx, dy))
        ux = dx / length
        uy = dy / length
        left = (end[0] - ux * 12 - uy * 8, end[1] - uy * 12 + ux * 8)
        right = (end[0] - ux * 12 + uy * 8, end[1] - uy * 12 - ux * 8)
        pygame.draw.polygon(screen, outer_color, [end, left, right])
        pygame.draw.polygon(screen, inner_color, [end, left, right], 2)

    destination = centers[-1]
    pygame.draw.circle(screen, WHITE, destination, 7)
    pygame.draw.circle(screen, inner_color, destination, 7, 2)


def get_post_move_attack_range(unit):
    return get_attack_range(unit, game_map)


def get_reachable_tiles_for_origin(unit):
    if unit is selected_unit and original_position is not None:
        return get_planning_move_range(unit, include_origin=True)
    return get_reachable_tiles(unit, game_map, include_origin=True)


def get_planning_move_range(unit, include_origin=False):
    if original_position is None:
        return []
    return get_reachable_tiles_from_position(unit, game_map, original_position, include_origin=include_origin)


def can_plan_move(unit, x, y):
    return (x, y) in get_planning_move_range(unit, include_origin=False)


def get_attack_positions_for_target(unit, target, game_map_obj=None):
    if not unit or not target or not unit.weapon:
        return []

    game_map_obj = game_map_obj or game_map
    tx, ty = target.get_position()
    move_origins = list(get_move_tiles(unit, game_map_obj))
    if unit is selected_unit and original_position is not None:
        move_origins.append(original_position)
    else:
        move_origins.append(unit.get_position())
    positions = []

    for origin_x, origin_y in move_origins:
        attack_tiles = get_attack_tiles_from_position((origin_x, origin_y), unit.weapon, game_map_obj)
        if (tx, ty) in attack_tiles:
            positions.append((origin_x, origin_y))

    return positions


def get_reachable_attack_targets(unit):
    if not unit:
        return []

    return [
        enemy_unit
        for enemy_unit in alive_units(enemies)
        if get_attack_positions_for_target(unit, enemy_unit)
    ]


def find_best_attack_position(unit, target, game_map_obj=None):
    if not unit or not target:
        return None

    game_map_obj = game_map_obj or game_map
    positions = get_attack_positions_for_target(unit, target, game_map_obj)
    if not positions:
        return None

    if original_position is not None and unit is selected_unit:
        origin_x, origin_y = original_position
    else:
        origin_x, origin_y = unit.get_position()

    target_x, target_y = target.get_position()
    return min(
        positions,
        key=lambda position: (
            abs(position[0] - origin_x) + abs(position[1] - origin_y),
            abs(position[0] - target_x) + abs(position[1] - target_y),
            position[1],
            position[0],
        ),
    )


def try_direct_attack_target(target):
    global interaction_state, preview_target, attack_confirmation_target, attack_confirmation_position

    if (
        not selected_unit
        or selected_unit.has_acted
        or not target
        or target not in alive_units(enemies)
        or interaction_state == "item_menu"
        or phase != "PLAYER"
        or is_animation_blocking_input()
    ):
        return False

    best_position = find_best_attack_position(selected_unit, target, game_map)
    if best_position is None:
        return False

    interaction_state = "targeting_attack"
    preview_target = target
    attack_confirmation_target = target
    attack_confirmation_position = best_position
    return True


def enemies_in_range(unit):
    return [enemy_unit for enemy_unit in alive_units(enemies) if in_range(unit, enemy_unit)]


def all_players_acted():
    active_players = alive_units(players)
    return bool(active_players) and all(unit.has_acted for unit in active_players)


def cleanup_dead_units():
    global phase, sandbox_battle_result
    if not in_tactical_battle_scene():
        return

    previous_phase = phase

    for group in (players, enemies):
        for unit in group[:]:
            if unit.is_alive():
                continue
            add_log(f"{unit.name} was defeated.")
            game_map.remove_unit(unit)
            group.remove(unit)

    if selected_unit and not selected_unit.is_alive():
        clear_selection()

    if not alive_units(enemies):
        phase = "VICTORY"
    elif not alive_units(players):
        phase = "DEFEAT"

    if battle_mode == "sandbox" and phase in {"VICTORY", "DEFEAT"} and sandbox_battle_result is None:
        sandbox_battle_result = phase

    if previous_phase != "VICTORY" and phase == "VICTORY":
        add_log("Victory achieved.")
        handle_victory_persistence()
    elif previous_phase != "DEFEAT" and phase == "DEFEAT":
        add_log("Defeat.")


def begin_player_phase():
    global phase, interaction_state, preview_target, enemy_phase_queue
    for unit in alive_units(players):
        unit.reset_turn()
    phase = "PLAYER"
    interaction_state = "idle"
    preview_target = None
    enemy_phase_queue = []
    clear_selection()
    add_log(f"Turn {turn}: Player Phase")


def begin_enemy_phase():
    global phase, preview_target, enemy_phase_queue
    clear_selection()
    for unit in alive_units(enemies):
        unit.reset_turn()
    phase = "ENEMY"
    preview_target = None
    enemy_phase_queue = alive_units(enemies)
    add_log(f"Turn {turn}: Enemy Phase")


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
        else:
            add_log(f"{selected_unit.name} cannot equip {item.name}")
        return

    if getattr(item, "item_type", None) == "potion":
        healed = selected_unit.heal(item.heal_amount)
        if healed > 0:
            selected_unit.remove_item(item)
            add_log(f"{selected_unit.name} used {item.name} +{healed} HP")
            finish_selected_action()
        return

    if getattr(item, "item_type", None) == "antidote":
        add_log(f"{selected_unit.name} has no status ailment.")
        interaction_state = "planning"


def execute_attack(target):
    if not selected_unit or not target or not target.is_alive():
        return
    if target is attack_confirmation_target and attack_confirmation_position is not None:
        if selected_unit.get_position() != attack_confirmation_position:
            game_map.move_unit(selected_unit, attack_confirmation_position[0], attack_confirmation_position[1])
            update_selected_move_flag()
    if target not in enemies_in_range(selected_unit):
        return
    clear_attack_forecast()
    start_combat_animation(selected_unit, target, "player")


def run_enemy_phase():
    global turn

    if not in_tactical_battle_scene() or phase != "ENEMY":
        return
    if level_up_popups or pending_combat_resolution is not None:
        return
    if combat_animation is not None:
        return

    while enemy_phase_queue:
        enemy_unit = enemy_phase_queue[0]
        if not enemy_unit.is_alive():
            enemy_phase_queue.pop(0)
            continue
        if not alive_units(players):
            cleanup_dead_units()
            return

        target = choose_target(enemy_unit, alive_units(players))
        if target is None:
            enemy_unit.has_acted = True
            finish_enemy_turn(enemy_unit)
            continue

        destination = choose_destination(enemy_unit, target, game_map)
        if destination != enemy_unit.get_position():
            game_map.move_unit(enemy_unit, destination[0], destination[1])
            enemy_unit.has_moved = True

        enemy_unit.has_acted = True
        if in_range(enemy_unit, target):
            start_combat_animation(enemy_unit, target, "enemy")
            return

        finish_enemy_turn(enemy_unit)

    if phase == "ENEMY":
        turn += 1
        begin_player_phase()


def start_battle():
    global turn, battle_log, battle_log_scroll, combat_animation, enemy_phase_queue
    global level_up_popups, pending_combat_resolution, threat_enemy_unit
    turn = 1
    battle_log = [f"{battle_title} started."]
    battle_log_scroll = 0
    combat_animation = None
    enemy_phase_queue = []
    level_up_popups = []
    pending_combat_resolution = None
    threat_enemy_unit = None
    begin_player_phase()


def return_to_chapter_select():
    global scene, selected_chapter_id, battle_log, battle_log_scroll, phase, battle_title, battle_mode
    global combat_animation, enemy_phase_queue
    global level_up_popups, pending_combat_resolution, threat_enemy_unit
    clear_selection()
    selected_chapter_id = None
    battle_log = []
    battle_log_scroll = 0
    phase = "START"
    battle_title = "No Battle"
    battle_mode = "chapter"
    combat_animation = None
    enemy_phase_queue = []
    level_up_popups = []
    pending_combat_resolution = None
    threat_enemy_unit = None
    scene = SCENE_CHAPTER_SELECT


def return_to_sandbox_map():
    global scene, battle_log, battle_log_scroll, phase, battle_title, battle_mode
    global sandbox_battle_target_id, sandbox_battle_result
    global selected_sandbox_territory_id, selected_sandbox_source_id, sandbox_result_applied
    global combat_animation, enemy_phase_queue
    global level_up_popups, pending_combat_resolution, threat_enemy_unit

    if sandbox_battle_target_id is not None and sandbox_battle_result is not None and not sandbox_result_applied:
        sandbox.apply_battle_result(
            sandbox_state,
            sandbox_battle_target_id,
            sandbox_battle_result == "VICTORY",
        )
        selected_sandbox_territory_id = sandbox_battle_target_id
        if sandbox.is_player_owned(sandbox_state, sandbox_battle_target_id):
            selected_sandbox_source_id = sandbox_battle_target_id
        sandbox_result_applied = True
        sync_gold_from_sandbox()

    clear_selection()
    battle_log = []
    battle_log_scroll = 0
    phase = "START"
    battle_title = "No Battle"
    battle_mode = "chapter"
    sandbox_battle_target_id = None
    sandbox_battle_result = None
    sandbox_result_applied = False
    combat_animation = None
    enemy_phase_queue = []
    level_up_popups = []
    pending_combat_resolution = None
    threat_enemy_unit = None
    scene = SCENE_SANDBOX_MAP


def get_attack_preview(attacker, defender):
    if not attacker or not defender or defender not in alive_units(enemies):
        return None
    attack_position = attack_confirmation_position if defender is attack_confirmation_target else None
    if attack_position is None and defender not in enemies_in_range(attacker):
        return None
    if attack_position is None:
        return attack_preview(attacker, defender)

    original_x, original_y = attacker.get_position()
    attacker.set_position(attack_position[0], attack_position[1])
    try:
        return attack_preview(attacker, defender)
    finally:
        attacker.set_position(original_x, original_y)


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
        elif is_incompatible_weapon(selected_unit, item):
            label = f"{label} [Unusable]"
        if getattr(item, "item_type", None) == "potion" and selected_unit.hp >= selected_unit.max_hp:
            enabled = False
        options.append(
            {
                "key": f"item:{index}",
                "label": label,
                "enabled": enabled,
                "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
            }
        )

    options.append({"key": "back", "label": "Back", "enabled": True})
    return options


def get_scrollable_action_options():
    convoy = get_convoy_for_mode(get_preparation_mode())

    if interaction_state == "item_menu" and selected_unit:
        options = []
        for index, item in enumerate(selected_unit.inventory):
            line_one, line_two = item_summary_lines(item, selected_unit)
            options.append(
                {
                    "key": f"item:{index}",
                    "lines": [line_one, line_two],
                    "enabled": not (
                        getattr(item, "item_type", None) == "potion" and selected_unit.hp >= selected_unit.max_hp
                    ),
                    "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
                }
            )
        options.append({"key": "back", "lines": ["Back"], "enabled": True, "text_color": BLACK})
        return options

    if interaction_state == "prep_equip" and selected_unit:
        options = []
        for index, item in enumerate(selected_unit.inventory):
            line_one, line_two = item_summary_lines(item, selected_unit)
            if item is selected_unit.weapon:
                line_two = f"Equipped | {line_two}" if line_two else "Equipped"
            options.append(
                {
                    "key": f"prep_equip:{index}",
                    "lines": [line_one, line_two],
                    "enabled": getattr(item, "item_type", None) == "weapon",
                    "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
                }
            )
        options.append({"key": "prep_back", "lines": ["Back"], "enabled": True, "text_color": BLACK})
        return options

    if interaction_state == "prep_store" and selected_unit:
        options = []
        for index, item in enumerate(selected_unit.inventory):
            line_one, line_two = item_summary_lines(item, selected_unit)
            options.append(
                {
                    "key": f"prep_store:{index}",
                    "lines": [line_one, line_two],
                    "enabled": True,
                    "text_color": BLACK,
                }
            )
        options.append({"key": "prep_back", "lines": ["Back"], "enabled": True, "text_color": BLACK})
        return options

    if interaction_state == "prep_take" and selected_unit:
        options = []
        for index, item in enumerate(convoy):
            line_one, line_two = item_summary_lines(item, selected_unit)
            options.append(
                {
                    "key": f"prep_take:{index}",
                    "lines": [line_one, line_two],
                    "enabled": can_take_specific_item(selected_unit, item),
                    "text_color": RED if is_incompatible_weapon(selected_unit, item) else BLACK,
                }
            )
        options.append({"key": "prep_back", "lines": ["Back"], "enabled": True, "text_color": BLACK})
        return options

    return []


def is_scrollable_action_state():
    return interaction_state in {"item_menu", "prep_equip", "prep_store", "prep_take"}


def update_panel_menu():
    global menu_actions
    menu_actions = {}
    panel_menu.button_height = 42
    panel_menu.gap = 10

    if phase == "START":
        options = build_prep_menu()
        menu_actions = {option["key"]: option["key"] for option in options}
    elif interaction_state == "planning":
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
    clamp_action_panel_scroll()


def get_action_list_top(action_rect):
    has_intro_text = phase == "START" and (
        selected_unit is None
        or interaction_state in {"prep_equip", "prep_store", "prep_take"}
        or interaction_state == "prep_menu"
    )
    return action_rect.y + (92 if has_intro_text else 40)


def get_action_visible_count():
    layout = last_battle_sidebar_layout or get_battle_sidebar_layout()
    action_rect = layout["action_rect"]
    list_top = get_action_list_top(action_rect)
    list_bottom = action_rect.bottom - 10
    entry_height = 42
    return max(1, (list_bottom - list_top) // entry_height)


def get_max_action_scroll():
    options = get_scrollable_action_options()
    return max(0, len(options) - get_action_visible_count())


def clamp_action_panel_scroll():
    global action_panel_scroll
    action_panel_scroll = max(0, min(action_panel_scroll, get_max_action_scroll()))


def scroll_action_panel(delta):
    global action_panel_scroll
    action_panel_scroll = max(0, min(action_panel_scroll + delta, get_max_action_scroll()))


def draw_scrollable_action_list(action_rect):
    global action_entry_buttons

    action_entry_buttons = []
    options = get_scrollable_action_options()
    clamp_action_panel_scroll()
    visible = get_action_visible_count()
    start_index = action_panel_scroll
    end_index = min(len(options), start_index + visible)
    visible_options = options[start_index:end_index]

    entry_y = get_action_list_top(action_rect)
    entry_height = 40
    entry_gap = 6
    entry_rects = []
    for option in visible_options:
        rect = pygame.Rect(action_rect.x + PANEL_PADDING, entry_y, action_rect.width - PANEL_PADDING * 2 - 10, entry_height)
        fill = BUTTON if option.get("enabled", True) else BUTTON_DISABLED
        pygame.draw.rect(screen, fill, rect, border_radius=6)
        pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=6)
        text_color = option.get("text_color", BLACK) if option.get("enabled", True) else TEXT_DISABLED
        lines = option.get("lines", [option.get("label", "")])
        draw_panel_lines(lines[:2], rect, start_y=6, render_font=tiny_font, color=text_color, line_height=14, padding=8)
        entry_rects.append({"key": option["key"], "rect": rect, "enabled": option.get("enabled", True)})
        entry_y += entry_height + entry_gap

    action_entry_buttons = entry_rects

    if len(options) > visible:
        track = pygame.Rect(action_rect.right - 8, action_rect.y + 40, 4, action_rect.height - 52)
        pygame.draw.rect(screen, BUTTON_DISABLED, track, border_radius=2)
        thumb_height = max(18, int(track.height * (visible / len(options))))
        thumb_range = max(1, track.height - thumb_height)
        thumb_offset = 0 if get_max_action_scroll() == 0 else int((action_panel_scroll / get_max_action_scroll()) * thumb_range)
        thumb = pygame.Rect(track.x, track.y + thumb_offset, track.width, thumb_height)
        pygame.draw.rect(screen, PANEL_BORDER, thumb, border_radius=2)


def get_action_entry_clicked(position):
    for entry in action_entry_buttons:
        if entry["enabled"] and entry["rect"].collidepoint(position):
            return entry["key"]
    return None


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
    if threat_enemy_unit is not None and threat_enemy_unit.is_alive():
        threat_move_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        threat_move_overlay.fill((255, 175, 175, 75))
        threat_attack_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        threat_attack_overlay.fill((255, 90, 90, 95))
        move_tiles, threat_tiles = get_enemy_threat_ranges(threat_enemy_unit)
        for x, y in move_tiles:
            screen.blit(threat_move_overlay, (x * CELL, y * CELL + BOARD_TOP))
        for x, y in threat_tiles:
            screen.blit(threat_attack_overlay, (x * CELL, y * CELL + BOARD_TOP))

    if not selected_unit or phase != "PLAYER":
        return

    move_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    move_overlay.fill((80, 150, 255, 110))
    attack_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    attack_overlay.fill((255, 90, 90, 130))
    confirm_overlay = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
    confirm_overlay.fill((255, 220, 120, 145))

    for x, y in get_move_range(selected_unit, game_map):
        screen.blit(move_overlay, (x * CELL, y * CELL + BOARD_TOP))

    for x, y in get_attack_range(selected_unit, game_map):
        screen.blit(attack_overlay, (x * CELL, y * CELL + BOARD_TOP))

    if attack_confirmation_position is not None:
        screen.blit(
            confirm_overlay,
            (attack_confirmation_position[0] * CELL, attack_confirmation_position[1] * CELL + BOARD_TOP),
        )


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
            offset_x, offset_y = get_unit_draw_offset(unit)
            body.move_ip(int(round(offset_x)), int(round(offset_y)))
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


def draw_context_strip():
    strip_rect = pygame.Rect(10, 10, BOARD_SIZE - 20, 76)
    primary_unit, secondary_unit = get_context_units()

    if primary_unit is None and secondary_unit is None:
        title_rect = draw_panel_section_rect(strip_rect)
        title_text = title_font.render(current_chapter_name(), True, BLACK)
        subtitle_text = small_font.render(
            "Select a unit to inspect battle details.",
            True,
            BLACK,
        )
        screen.blit(title_text, title_text.get_rect(center=(title_rect.centerx, title_rect.y + 24)))
        screen.blit(subtitle_text, subtitle_text.get_rect(center=(title_rect.centerx, title_rect.y + 50)))
        return

    gap = 10
    left_rect = pygame.Rect(strip_rect.x, strip_rect.y, (strip_rect.width - gap) // 2, strip_rect.height)
    right_rect = pygame.Rect(left_rect.right + gap, strip_rect.y, strip_rect.width - left_rect.width - gap, strip_rect.height)

    if primary_unit is not None and secondary_unit is None:
        single_rect = draw_panel_section_rect(strip_rect)
        draw_panel_lines(get_context_unit_lines(primary_unit), single_rect, start_y=12, render_font=small_font, line_height=18)
        return

    if primary_unit is not None:
        left_panel = draw_panel_section_rect(left_rect)
        draw_panel_lines(get_context_unit_lines(primary_unit), left_panel, start_y=12, render_font=small_font, line_height=18)

    if secondary_unit is not None:
        right_panel = draw_panel_section_rect(right_rect)
        draw_panel_lines(get_context_unit_lines(secondary_unit), right_panel, start_y=12, render_font=small_font, line_height=18)


def draw_panel_section_rect(rect, title="", title_render_font=None):
    pygame.draw.rect(screen, BUTTON, rect, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=8)
    if title:
        render_font = title_render_font or title_font
        title_surface = render_font.render(title, True, BLACK)
        title_rect = title_surface.get_rect(midleft=(rect.x + PANEL_PADDING, rect.y + 16))
        screen.blit(title_surface, title_rect)
    return rect


def draw_panel_section(title, top, height):
    rect = pygame.Rect(PANEL_X, top, PANEL_WIDTH, height)
    return draw_panel_section_rect(rect, title)


def wrap_text(text, render_font, max_width):
    words = text.split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if render_font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_panel_lines(lines, rect, start_y=42, render_font=None, color=BLACK, line_height=None, padding=None):
    render_font = render_font or small_font
    line_height = line_height or PANEL_LINE_HEIGHT
    padding = PANEL_PADDING if padding is None else padding
    y = rect.y + start_y
    max_width = rect.width - padding * 2 - 6
    max_y = rect.bottom - 8
    for line in lines:
        wrapped_lines = wrap_text(str(line), render_font, max_width)
        for wrapped in wrapped_lines:
            if y + render_font.get_height() > max_y:
                return
            screen.blit(render_font.render(wrapped, True, color), (rect.x + padding, y))
            y += line_height


def ellipsize_text(text, render_font, max_width):
    if render_font.size(text)[0] <= max_width:
        return text
    ellipsis = "..."
    trimmed = text
    while trimmed and render_font.size(trimmed + ellipsis)[0] > max_width:
        trimmed = trimmed[:-1]
    return (trimmed + ellipsis) if trimmed else ellipsis


def item_summary_lines(item, unit=None):
    if getattr(item, "item_type", None) == "weapon":
        line_one = f"{item.name} ({item.durability}/{item.max_durability})"
        line_two = (
            f"{item.weapon_type.title()} | MT {item.might} | RNG {item.range} | CRT {getattr(item, 'crit_bonus', 0)}"
        )
        if unit is not None and is_incompatible_weapon(unit, item):
            line_two = f"Carry only | {line_two}"
        return line_one, line_two
    if getattr(item, "item_type", None) == "potion":
        return item.name, f"Heal {item.heal_amount}"
    if getattr(item, "item_type", None) == "antidote":
        return item.name, "Cure"
    return getattr(item, "name", "Item"), ""


def get_context_units():
    if attack_confirmation_target is not None and selected_unit is not None:
        return selected_unit, attack_confirmation_target
    if preview_target in alive_units(enemies) and selected_unit is not None and interaction_state == "targeting_attack":
        return selected_unit, preview_target
    if selected_unit is not None:
        return selected_unit, None
    if threat_enemy_unit is not None and threat_enemy_unit.is_alive():
        return None, threat_enemy_unit
    return None, None


def get_context_unit_lines(unit):
    if not unit:
        return []
    return [
        f"{unit.name} | {unit.unit_class}",
        f"Lv {unit.level}  HP {unit.hp}/{unit.max_hp}  CRT {unit.crit}",
        ellipsize_text(format_weapon_display(unit.weapon), tiny_font, 210),
    ]


def format_weapon_display(weapon):
    if not weapon:
        return "None"
    return f"{weapon.name} ({weapon.durability}/{weapon.max_durability})"


def get_tile_terrain_info(tile):
    if tile is None or game_map is None:
        return None
    x, y = tile
    terrain_type = game_map.get_terrain(x, y)
    terrain = get_terrain_data(terrain_type)
    terrain_name = terrain_type.replace("_", " ").title()
    lines = [terrain_name, f"Move {terrain.get('move_cost', 1)}"]
    if terrain.get("defense", 0):
        lines.append(f"Def +{terrain['defense']}")
    if terrain.get("avoid", 0):
        lines.append(f"Avoid {terrain['avoid']:+d}")
    if terrain.get("heal", 0):
        lines.append(f"Heal +{terrain['heal']}")
    if terrain.get("hit", 0):
        lines.append(f"Hit {terrain['hit']:+d}")
    if terrain.get("range_bonus", 0):
        lines.append(f"Range +{terrain['range_bonus']}")
    if terrain.get("hp_delta", 0):
        lines.append(f"HP {terrain['hp_delta']:+d}/turn")
    if len(lines) == 2:
        lines.append("No bonus")
    return {
        "tile": tile,
        "terrain_type": terrain_type,
        "lines": lines,
    }


def get_hovered_or_selected_terrain():
    if hovered_board_tile is not None:
        return get_tile_terrain_info(hovered_board_tile)
    if selected_board_tile is not None:
        return get_tile_terrain_info(selected_board_tile)
    if selected_unit is not None:
        return get_tile_terrain_info(selected_unit.get_position())
    return None


def get_terrain_display_lines(unit):
    if not unit or not unit.game_map:
        return ["Terrain: None"]

    info = get_tile_terrain_info(unit.get_position())
    if not info:
        return ["Terrain: None"]
    return [f"Terrain: {info['lines'][0]}", *info["lines"][1:4]]


def get_battle_sidebar_layout():
    top = 18
    gap = 8
    section_gap = 10
    button_height = 36
    button_width = PANEL_WIDTH
    start_button = None
    return_button = None
    end_turn_button = None

    if phase == "START":
        half_width = (button_width - gap) // 2
        start_button = pygame.Rect(PANEL_X, top, half_width, button_height)
        return_button = pygame.Rect(PANEL_X + half_width + gap, top, button_width - half_width - gap, button_height)
        content_top = top + button_height + section_gap
    else:
        start_button = pygame.Rect(PANEL_X, top, button_width, button_height)
        content_top = top + button_height + section_gap
        if battle_mode == "sandbox":
            end_turn_button = pygame.Rect(PANEL_X, content_top, button_width, button_height)
            content_top = end_turn_button.bottom + section_gap

    header_rect = pygame.Rect(PANEL_X, content_top, PANEL_WIDTH, 64)
    unit_rect = pygame.Rect(PANEL_X, header_rect.bottom + section_gap, PANEL_WIDTH, 132)
    terrain_rect = pygame.Rect(PANEL_X, unit_rect.bottom + section_gap, PANEL_WIDTH, 96)
    if phase == "START":
        action_rect = pygame.Rect(PANEL_X, terrain_rect.bottom + section_gap, PANEL_WIDTH, HEIGHT - terrain_rect.bottom - section_gap - 18)
        preview_rect = pygame.Rect(PANEL_X, action_rect.bottom, PANEL_WIDTH, 0)
        log_rect = pygame.Rect(PANEL_X, action_rect.bottom, PANEL_WIDTH, 0)
    else:
        action_rect = pygame.Rect(PANEL_X, terrain_rect.bottom + section_gap, PANEL_WIDTH, 148)
        preview_rect = pygame.Rect(PANEL_X, action_rect.bottom + section_gap, PANEL_WIDTH, 116)
        log_rect = pygame.Rect(PANEL_X, preview_rect.bottom + section_gap, PANEL_WIDTH, HEIGHT - preview_rect.bottom - section_gap - 18)

    return {
        "start_button": start_button,
        "return_button": return_button,
        "end_turn_button": end_turn_button,
        "header_rect": header_rect,
        "unit_rect": unit_rect,
        "terrain_rect": terrain_rect,
        "action_rect": action_rect,
        "preview_rect": preview_rect,
        "log_rect": log_rect,
    }


def draw_header_panel(layout):
    header_rect = draw_panel_section_rect(layout["header_rect"])
    if phase == "START":
        mode = get_preparation_mode()
        lines = [
            current_chapter_name(),
            f"Gold: {get_gold_for_mode(mode)}",
            f"Convoy: {len(get_convoy_for_mode(mode))} items",
            f"Phase: {phase}",
        ]
    else:
        lines = [
            current_chapter_name(),
            f"Turn {turn}",
            f"Phase: {phase}",
        ]
    draw_panel_lines(lines, header_rect, start_y=12, render_font=small_font, line_height=18)


def draw_unit_info_panel(layout):
    unit_rect = draw_panel_section_rect(layout["unit_rect"], "Unit")

    if phase == "START" and selected_unit:
        lines = [
            f"Name: {selected_unit.name}",
            f"Class: {selected_unit.unit_class}",
            f"Lv:{selected_unit.level} Exp:{selected_unit.exp}",
            f"HP:{selected_unit.hp}/{selected_unit.max_hp}",
            f"STR:{selected_unit.strength} MAG:{selected_unit.magic} CRT:{selected_unit.crit}",
            f"DEF:{selected_unit.defense} RES:{selected_unit.resistance}",
            f"Wpn: {format_weapon_display(selected_unit.weapon)}",
        ]
    elif selected_unit:
        lines = [
            f"Name: {selected_unit.name}",
            f"Class: {selected_unit.unit_class}",
            f"Lv:{selected_unit.level} Exp:{selected_unit.exp}",
            f"HP:{selected_unit.hp}/{selected_unit.max_hp}",
            f"STR:{selected_unit.strength} MAG:{selected_unit.magic} CRT:{selected_unit.crit}",
            f"DEF:{selected_unit.defense} RES:{selected_unit.resistance}",
            f"Wpn: {format_weapon_display(selected_unit.weapon)}",
        ]
    elif preview_target and preview_target.is_alive():
        lines = [
            f"Name: {preview_target.name}",
            f"Class: {preview_target.unit_class}",
            f"Lv:{preview_target.level} HP:{preview_target.hp}/{preview_target.max_hp}",
            f"STR:{preview_target.strength} MAG:{preview_target.magic} CRT:{preview_target.crit}",
            f"DEF:{preview_target.defense} RES:{preview_target.resistance}",
            f"Wpn: {format_weapon_display(preview_target.weapon)}",
        ]
    elif phase == "START":
        lines = ["Battle loaded.", "Click a player unit to manage inventory."]
    else:
        lines = ["Select a unit or enemy to inspect."]

    draw_panel_lines(lines, unit_rect, start_y=30, render_font=tiny_font, line_height=16)


def draw_terrain_panel(layout):
    terrain_rect = draw_panel_section_rect(layout["terrain_rect"], "Terrain")
    terrain_info = get_hovered_or_selected_terrain()

    if terrain_info is None:
        lines = ["No terrain selected."]
    else:
        tile = terrain_info["tile"]
        lines = [
            f"Tile: {tile[0] + 1}, {tile[1] + 1}",
            *terrain_info["lines"][:4],
        ]
    draw_panel_lines(lines, terrain_rect, start_y=30, render_font=tiny_font, line_height=15)


def draw_action_panel(layout):
    global action_entry_buttons
    action_title = "Action"
    action_lines = []
    action_rect = layout["action_rect"]

    if phase == "START":
        action_title = "Preparation"
        if selected_unit is None:
            action_lines = [
                "Click a player unit to edit inventory.",
                "Shop buys items for convoy.",
                "Start Battle begins the player phase.",
            ]
        elif interaction_state == "prep_equip":
            action_lines = ["Choose a weapon to equip."]
        elif interaction_state == "prep_store":
            action_lines = ["Store an item in convoy."]
        elif interaction_state == "prep_take":
            action_lines = [
                "Take an item from convoy.",
                f"Slots: {len(selected_unit.inventory)}/{PREP_INVENTORY_LIMIT}",
            ]
        else:
            action_lines = [
                "Adjust carried items before battle.",
                f"Slots: {len(selected_unit.inventory)}/{PREP_INVENTORY_LIMIT}",
            ]
    elif interaction_state == "item_menu":
        action_title = "Items"
    elif interaction_state == "targeting_attack":
        action_title = "Attack"
        action_lines = [
            "First click shows forecast.",
            "Click the same target again to attack.",
        ]
    elif interaction_state not in {"planning", "item_menu"}:
        action_lines = ["Move, then choose an action."]

    action_rect = draw_panel_section_rect(action_rect, action_title)
    if action_lines:
        draw_panel_lines(action_lines, action_rect, render_font=tiny_font, line_height=16)

    panel_menu.x = PANEL_X + PANEL_PADDING
    panel_menu.y = get_action_list_top(action_rect)
    panel_menu.width = PANEL_WIDTH - PANEL_PADDING * 2
    panel_menu.button_height = 34
    panel_menu.gap = 8

    if is_scrollable_action_state():
        draw_scrollable_action_list(action_rect)
    elif phase == "START" or interaction_state in {"planning", "item_menu"}:
        action_entry_buttons = []
        panel_menu.draw(screen, font, MENU_COLORS)
    else:
        action_entry_buttons = []


def draw_battle_preview_panel(layout):
    if phase == "START":
        return
    preview_rect = draw_panel_section_rect(layout["preview_rect"], "Forecast")
    preview = get_attack_preview(selected_unit, preview_target)

    if interaction_state != "targeting_attack":
        draw_panel_lines(["No battle preview."], preview_rect)
        return

    if not preview_target or not preview:
        draw_panel_lines(["Hover an enemy to preview combat."], preview_rect)
        return

    left_rect = pygame.Rect(preview_rect.x + 8, preview_rect.y + 26, preview_rect.width // 2 - 12, 62)
    right_rect = pygame.Rect(preview_rect.centerx + 4, preview_rect.y + 26, preview_rect.width // 2 - 12, 62)
    player_lines = [
        f"{preview['attacker']['name']} | {selected_unit.unit_class}",
        f"Wpn {preview['attacker']['weapon']} {preview['attacker']['weapon_durability']}",
        f"HP {preview['attacker']['hp']}  Atk {preview['attacker']['atk']}",
        f"Hit {preview['attacker']['hit']}  Crit {preview['attacker']['crit']}  x{preview['attacker_hits']}",
    ]
    if preview["counter"]:
        enemy_bottom = f"Hit {preview['defender']['hit']}  Crit {preview['defender']['crit']}  x{preview['defender_hits']}"
    else:
        enemy_bottom = "Counter: No"
    enemy_lines = [
        f"{preview['defender']['name']} | {preview_target.unit_class}",
        f"Wpn {preview['defender']['weapon']} {preview['defender']['weapon_durability']}",
        f"HP {preview['defender']['hp']}  Atk {preview['defender']['atk']}",
        enemy_bottom,
    ]
    draw_panel_lines(player_lines, left_rect, start_y=0, render_font=tiny_font, line_height=14, padding=0)
    draw_panel_lines(enemy_lines, right_rect, start_y=0, render_font=tiny_font, line_height=14, padding=0)

    footer_line = (
        f"P x{preview['attacker_hits']} / E x{preview['defender_hits']} | Follow-up: {preview['follow_up']}"
    )
    draw_panel_lines([footer_line], preview_rect, start_y=92, render_font=tiny_font, line_height=14)


def draw_log_panel(layout):
    if phase == "START":
        return {}
    log_rect = draw_panel_section_rect(layout["log_rect"], "Log")
    clamp_log_scroll()
    visible_count = get_log_visible_count()
    if battle_log:
        end_index = len(battle_log) - battle_log_scroll
        start_index = max(0, end_index - visible_count)
        entries = battle_log[start_index:end_index]
    else:
        entries = ["No messages."]
    draw_panel_lines(entries, log_rect, start_y=36)

    if len(battle_log) > visible_count:
        track = pygame.Rect(log_rect.right - 10, log_rect.y + 34, 4, log_rect.height - 44)
        pygame.draw.rect(screen, BUTTON_DISABLED, track, border_radius=2)
        max_scroll = get_max_log_scroll()
        thumb_height = max(18, int(track.height * (visible_count / len(battle_log))))
        thumb_range = max(1, track.height - thumb_height)
        thumb_offset = 0 if max_scroll == 0 else int((battle_log_scroll / max_scroll) * thumb_range)
        thumb = pygame.Rect(track.x, track.y + thumb_offset, track.width, thumb_height)
        pygame.draw.rect(screen, PANEL_BORDER, thumb, border_radius=2)

    footer_y = log_rect.bottom - LOG_FOOTER_HEIGHT + 6
    label = small_font.render("Speed", True, BLACK)
    screen.blit(label, (log_rect.x + PANEL_PADDING, footer_y + 2))

    button_y = footer_y - 2
    speed_1x = pygame.Rect(log_rect.x + 66, button_y, 42, 24)
    speed_2x = pygame.Rect(log_rect.x + 114, button_y, 42, 24)
    for speed_value, rect in ((1, speed_1x), (2, speed_2x)):
        active = combat_speed == speed_value
        pygame.draw.rect(screen, LIGHT_GOLD if active else BUTTON, rect, border_radius=6)
        pygame.draw.rect(screen, GOLD if active else PANEL_BORDER, rect, 2, border_radius=6)
        label_surface = small_font.render(f"{speed_value}x", True, BLACK)
        screen.blit(label_surface, label_surface.get_rect(center=rect.center))

    return {"speed_1x": speed_1x, "speed_2x": speed_2x}


def draw_end_state():
    message = "Victory" if phase == "VICTORY" else "Game Over"
    overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    overlay.fill((20, 20, 20, 140))
    screen.blit(overlay, (0, BOARD_TOP))

    label = menu_title_font.render(message, True, WHITE)
    label_rect = label.get_rect(center=(BOARD_SIZE // 2, BOARD_TOP + BOARD_SIZE // 2))
    screen.blit(label, label_rect)

    if battle_mode == "sandbox":
        treasury_delta = f"+{sandbox.CAPTURE_REWARD} Gold" if phase == "VICTORY" else f"-{sandbox.CAPTURE_REWARD} Gold"
        delta_label = title_font.render(treasury_delta, True, GOLD if phase == "VICTORY" else LIGHT_RED)
        delta_rect = delta_label.get_rect(center=(BOARD_SIZE // 2, BOARD_TOP + BOARD_SIZE // 2 + 42))
        screen.blit(delta_label, delta_rect)


def draw_level_up_popup():
    if not level_up_popups:
        return

    popup = level_up_popups[0]
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((18, 18, 18, 120))
    screen.blit(overlay, (0, 0))

    rect = pygame.Rect(140, 250, 480, 210)
    pygame.draw.rect(screen, PANEL_BG, rect, border_radius=12)
    pygame.draw.rect(screen, GOLD, rect, 3, border_radius=12)

    title = menu_title_font.render("Level Up", True, BLACK)
    subtitle = title_font.render(
        f"{popup['unit_name']}  Lv {popup['old_level']} -> {popup['new_level']}",
        True,
        BLACK,
    )
    screen.blit(title, title.get_rect(center=(rect.centerx, rect.y + 36)))
    screen.blit(subtitle, subtitle.get_rect(center=(rect.centerx, rect.y + 82)))

    draw_panel_lines(popup["stat_lines"], rect, start_y=110, render_font=font, line_height=22, padding=28)
    prompt = small_font.render("Click to continue", True, BLACK)
    screen.blit(prompt, prompt.get_rect(center=(rect.centerx, rect.bottom - 22)))


def draw_panel():
    global last_battle_sidebar_layout

    update_panel_menu()
    layout = get_battle_sidebar_layout()
    last_battle_sidebar_layout = layout

    panel_rect = pygame.Rect(PANEL_X - 10, 0, PANEL_WIDTH + 20, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (PANEL_X - 10, 0), (PANEL_X - 10, HEIGHT), 3)

    start_button = layout["start_button"]
    shop_button = layout["return_button"]
    end_turn_button = layout["end_turn_button"]
    is_start_ready = phase == "START"
    is_return_ready = phase == "VICTORY" or (battle_mode == "sandbox" and phase in {"VICTORY", "DEFEAT"})
    button_enabled = is_start_ready or is_return_ready
    if is_return_ready:
        button_label = "Return Map" if battle_mode == "sandbox" else "Return Menu"
    else:
        button_label = "Start Battle"
    pygame.draw.rect(screen, GREEN if button_enabled else BUTTON_DISABLED, start_button, border_radius=6)
    pygame.draw.rect(screen, PANEL_BORDER, start_button, 2, border_radius=6)
    start_button_font = small_font
    start_label = start_button_font.render(button_label, True, BLACK)
    screen.blit(start_label, start_label.get_rect(center=start_button.center))

    if shop_button is not None:
        pygame.draw.rect(screen, BUTTON, shop_button, border_radius=6)
        pygame.draw.rect(screen, PANEL_BORDER, shop_button, 2, border_radius=6)
        shop_label = small_font.render(
            "Return Chapter"
            if phase == "START" and battle_mode == "chapter"
            else "Return Map"
            if phase == "START" and battle_mode == "sandbox"
            else "Shop",
            True,
            BLACK,
        )
        screen.blit(shop_label, shop_label.get_rect(center=shop_button.center))

    if end_turn_button is not None:
        end_turn_enabled = phase == "PLAYER"
        pygame.draw.rect(
            screen,
            BUTTON if end_turn_enabled else BUTTON_DISABLED,
            end_turn_button,
            border_radius=6,
        )
        pygame.draw.rect(screen, PANEL_BORDER, end_turn_button, 2, border_radius=6)
        end_turn_label = font.render(
            "End Turn",
            True,
            BLACK if end_turn_enabled else TEXT_DISABLED,
        )
        screen.blit(end_turn_label, end_turn_label.get_rect(center=end_turn_button.center))

    draw_header_panel(layout)
    draw_unit_info_panel(layout)
    draw_terrain_panel(layout)
    draw_action_panel(layout)
    draw_battle_preview_panel(layout)
    speed_buttons = draw_log_panel(layout)

    if phase in {"VICTORY", "DEFEAT"}:
        draw_end_state()

    draw_level_up_popup()

    return {
        "start": start_button,
        "end_turn": end_turn_button,
        "shop": shop_button,
        "speed_1x": speed_buttons.get("speed_1x"),
        "speed_2x": speed_buttons.get("speed_2x"),
    }


def draw_game_scene():
    draw_context_strip()
    draw_grid()
    draw_terrain()
    draw_ranges()
    draw_path_arrows()
    draw_units()
    return draw_panel()


def get_best_button_font(label, rect):
    for render_font in (menu_button_font, title_font, font, small_font, tiny_font):
        if render_font.size(label)[0] <= rect.width - 16:
            return render_font
    return tiny_font


def draw_button(rect, label, fill_color=BUTTON, text_color=BLACK):
    pygame.draw.rect(screen, fill_color, rect, border_radius=8)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=8)
    render_font = get_best_button_font(label, rect)
    label_surface = render_font.render(label, True, text_color)
    screen.blit(label_surface, label_surface.get_rect(center=rect.center))


def draw_menu_scene():
    title = menu_title_font.render("Project Alpha", True, BLACK)
    subtitle = title_font.render("Fire Emblem Style Tactical RPG", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 170)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 220)))
    draw_button(main_menu_buttons["new"], "New Game")
    draw_button(main_menu_buttons["load"], "Load Game")


def draw_mode_select_scene():
    title = menu_title_font.render("Choose Mode", True, BLACK)
    subtitle = title_font.render("Start a fresh Chapter or Sandbox campaign", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 190)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 240)))
    draw_button(mode_select_buttons["chapter"], "Chapter Mode")
    draw_button(mode_select_buttons["sandbox"], "Sandbox Mode")
    draw_button(slot_back_button, "Return Menu")


def draw_chapter_select_scene():
    title = menu_title_font.render("Chapter Select", True, BLACK)
    subtitle = title_font.render("Choose a battle map", True, BLACK)
    economy = title_font.render(
        f"Gold: {chapter_state['gold']}  Convoy: {len(chapter_state['convoy'])}",
        True,
        BLACK,
    )
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 150)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 200)))
    screen.blit(economy, economy.get_rect(center=(WIDTH // 2, 465)))

    unlocked_chapters = set(chapter_state["chapter_progress"]["unlocked"])
    for chapter_id, rect in chapter_buttons.items():
        pygame.draw.rect(screen, PANEL_BG, rect, border_radius=8)
        pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=8)
        label_text = f"{CHAPTERS[chapter_id]['name']} (Enemy Lv{CHAPTERS[chapter_id]['enemy_level']})"
        label_color = BLACK if chapter_id in unlocked_chapters else TEXT_DISABLED
        label = font.render(label_text, True, label_color)
        screen.blit(label, label.get_rect(center=rect.center))

    draw_button(chapter_shop_button, "Shop", fill_color=BUTTON)
    draw_button(chapter_save_button, "Save Game", fill_color=BUTTON)
    draw_button(chapter_return_button, "Return Mode", fill_color=BUTTON)


def draw_faction_select_scene():
    title = menu_title_font.render("Choose a Faction", True, BLACK)
    subtitle = title_font.render("Choose one of the seven kingdoms to lead", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 140)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 190)))

    for faction in sandbox.PLAYABLE_FACTIONS:
        rect = faction_buttons[faction["id"]]
        draw_button(rect, faction["name"], fill_color=faction["color"])

    draw_button(sandbox_back_button, "Return Mode", fill_color=BUTTON)


def get_sandbox_layout():
    global sandbox_shop_button, sandbox_save_button, sandbox_back_button
    global sandbox_city_unit_buttons, sandbox_field_unit_buttons

    left_margin = 18
    top_margin = 18
    sidebar_width = 200
    sidebar_x = WIDTH - sidebar_width - 20
    map_width = sidebar_x - left_margin - 16
    map_rect = pygame.Rect(left_margin, top_margin, map_width, 472)
    city_rect = pygame.Rect(left_margin, map_rect.bottom + 14, (map_width - 12) // 2, HEIGHT - map_rect.bottom - 32)
    attack_rect = pygame.Rect(city_rect.right + 12, map_rect.bottom + 14, map_rect.right - city_rect.right - 12, HEIGHT - map_rect.bottom - 32)

    sidebar_gap = 12
    sidebar_top = 42
    section_title_gap = 10

    faction_rect = pygame.Rect(sidebar_x, sidebar_top, sidebar_width, 82)
    territory_rect = pygame.Rect(sidebar_x, faction_rect.bottom + sidebar_gap, sidebar_width, 140)
    orders_rect = pygame.Rect(sidebar_x, territory_rect.bottom + sidebar_gap, sidebar_width, 158)
    neighbors_rect = pygame.Rect(sidebar_x, orders_rect.bottom + sidebar_gap, sidebar_width, 96)

    button_height = 40
    sandbox_shop_button = pygame.Rect(sidebar_x, neighbors_rect.bottom + sidebar_gap, sidebar_width, button_height)
    sandbox_save_button = pygame.Rect(sidebar_x, sandbox_shop_button.bottom + section_title_gap, sidebar_width, button_height)
    sandbox_back_button = pygame.Rect(sidebar_x, sandbox_save_button.bottom + section_title_gap, sidebar_width, button_height)

    city_button_width = city_rect.width - 24
    sandbox_city_unit_buttons = [
        pygame.Rect(city_rect.x + 12, city_rect.y + 70 + index * 28, city_button_width, 24)
        for index in range(sandbox.MAX_GARRISON_UNITS)
    ]

    field_slot_gap = 8
    field_slot_width = (attack_rect.width - 24 - field_slot_gap) // 2
    field_slot_height = 42
    sandbox_field_unit_buttons = []
    for index in range(sandbox.FIELD_TEAM_CAPACITY):
        row = index // 2
        col = index % 2
        slot_x = attack_rect.x + 12 + col * (field_slot_width + field_slot_gap)
        slot_y = attack_rect.y + 86 + row * (field_slot_height + 10)
        sandbox_field_unit_buttons.append(
            pygame.Rect(slot_x, slot_y, field_slot_width, field_slot_height)
        )

    return {
        "left_map_area": map_rect,
        "bottom_city_units_area": city_rect,
        "bottom_attack_team_area": attack_rect,
        "right_sidebar": pygame.Rect(sidebar_x, top_margin, sidebar_width, HEIGHT - top_margin * 2),
        "sidebar_panels": {
            "faction": faction_rect,
            "territory": territory_rect,
            "orders": orders_rect,
            "neighbors": neighbors_rect,
        },
        "buttons": {
            "shop": sandbox_shop_button,
            "save": sandbox_save_button,
            "return": sandbox_back_button,
        },
    }


def draw_slot_menu_scene():
    slot_infos = save_system.list_save_slots(include_auto=True)
    title_text = "Save Game" if save_menu_mode == "save" else "Load Game"
    subtitle_text = (
        "Choose a slot to overwrite."
        if save_menu_mode == "save"
        else "Choose a save to restore."
    )
    if slot_clear_mode:
        subtitle_text = "Clear mode: choose a manual slot to erase."

    title = menu_title_font.render(title_text, True, BLACK)
    subtitle = title_font.render(subtitle_text, True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 88)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 132)))

    for info in slot_infos:
        rect = save_slot_buttons[info["slot"]]
        fill_color = BUTTON
        if info["corrupt"]:
            fill_color = LIGHT_RED
        elif not info["exists"]:
            fill_color = BUTTON_DISABLED
        pygame.draw.rect(screen, fill_color, rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=10)

        slot_name = "Auto Save" if info["slot"] == save_system.AUTO_SAVE_SLOT else f"Slot {info['slot']}"
        slot_label = title_font.render(slot_name, True, BLACK)
        screen.blit(slot_label, (rect.x + 18, rect.y + 14))

        if not info["exists"]:
            summary_lines = ["Empty Auto Save" if info["slot"] == save_system.AUTO_SAVE_SLOT else "Empty"]
        elif info["corrupt"]:
            summary_lines = ["Unreadable save data"]
        else:
            summary = info["summary"] or {}
            summary_lines = [
                f"{summary.get('mode', 'Unknown')} | {summary.get('location', 'Unknown')}",
                f"Gold: {summary.get('gold', 0)}",
                f"Saved: {summary.get('timestamp', 'Unknown')}",
            ]
            if summary.get("mode") == "Sandbox":
                summary_lines.append(
                    f"Faction: {summary.get('sandbox_faction', 'Unknown')}  Territories: {summary.get('sandbox_territories', 0)}"
                )
            elif summary.get("mode") == "Chapter":
                clears = summary.get("chapter_clears", {})
                summary_lines.append(f"Clears: C1 {clears.get('1', 0)}  C2 {clears.get('2', 0)}")

        for index, line in enumerate(summary_lines):
            screen.blit(font.render(line, True, BLACK), (rect.x + 18, rect.y + 46 + index * 20))

    if save_message:
        message = font.render(save_message, True, RED if "failed" in save_message.lower() else BLACK)
        screen.blit(message, message.get_rect(center=(WIDTH // 2, 612)))

    clear_label = "Cancel Clear" if slot_clear_mode else "Clear Slot"
    draw_button(slot_clear_button, clear_label, fill_color=LIGHT_RED if slot_clear_mode else BUTTON)
    draw_button(slot_back_button, "Back", fill_color=BUTTON)


def get_sandbox_grid_metrics(map_rect):
    grid_gap = 4
    usable_width = map_rect.width - 28
    usable_height = map_rect.height - 86
    cell_size = min(
        (usable_width - grid_gap * (sandbox.GRID_COLS - 1)) // sandbox.GRID_COLS,
        (usable_height - grid_gap * (sandbox.GRID_ROWS - 1)) // sandbox.GRID_ROWS,
    )
    cell_size = max(28, cell_size)
    total_width = sandbox.GRID_COLS * cell_size + grid_gap * (sandbox.GRID_COLS - 1)
    total_height = sandbox.GRID_ROWS * cell_size + grid_gap * (sandbox.GRID_ROWS - 1)
    start_x = map_rect.x + (map_rect.width - total_width) // 2
    start_y = map_rect.y + 74 + (usable_height - total_height) // 2
    return {
        "cell_size": cell_size,
        "gap": grid_gap,
        "start_x": start_x,
        "start_y": start_y,
    }


def get_sandbox_tile_rect(tile, map_rect):
    metrics = get_sandbox_grid_metrics(map_rect)
    row, col = tile["grid"]
    x = metrics["start_x"] + col * (metrics["cell_size"] + metrics["gap"])
    y = metrics["start_y"] + row * (metrics["cell_size"] + metrics["gap"])
    return pygame.Rect(x, y, metrics["cell_size"], metrics["cell_size"])


def get_sandbox_tile_short_label(tile):
    if tile["type"] == sandbox.TILE_EMPTY:
        return "+500"
    if tile["type"] == sandbox.TILE_BLOCKED:
        return ""
    return tile["name"]


def draw_sandbox_map_scene():
    global sandbox_territory_buttons

    layout = get_sandbox_layout()
    selected_territory = None
    selected_source = None
    valid_target_ids = set()
    can_assign_garrison = False
    can_recall_garrison = False
    dispatchable_units = 0
    city_units = []
    field_team = sandbox.get_field_team(sandbox_state)
    if selected_sandbox_territory_id is not None:
        selected_territory = sandbox.get_territory(sandbox_state, selected_sandbox_territory_id)
    if selected_sandbox_source_id is not None:
        selected_source = sandbox.get_territory(sandbox_state, selected_sandbox_source_id)
        if selected_source is not None and sandbox.is_player_owned(sandbox_state, selected_sandbox_source_id):
            valid_target_ids = set(sandbox.get_valid_targets_from_source(sandbox_state, selected_sandbox_source_id))
            can_assign_garrison = sandbox.can_assign_field_unit(sandbox_state, selected_sandbox_source_id)
            can_recall_garrison = sandbox.can_recall_field_unit(sandbox_state, selected_sandbox_source_id)
            dispatchable_units = sandbox.get_dispatchable_units(sandbox_state, selected_sandbox_source_id)
            city_units = sandbox.get_territory_units(sandbox_state, selected_sandbox_source_id)
        else:
            selected_source = None

    screen.fill(WHITE)
    map_rect = draw_panel_section_rect(layout["left_map_area"])
    city_rect = draw_panel_section_rect(layout["bottom_city_units_area"], "City Units", title_render_font=font)
    attack_rect = draw_panel_section_rect(layout["bottom_attack_team_area"], "Attack Team", title_render_font=font)

    title = title_font.render("Sandbox Conquest", True, BLACK)
    subtitle = small_font.render("Select an owned city, then expand to adjacent targets", True, BLACK)
    screen.blit(title, title.get_rect(center=(map_rect.centerx, map_rect.y + 26)))
    screen.blit(subtitle, subtitle.get_rect(center=(map_rect.centerx, map_rect.y + 54)))

    grid_metrics = get_sandbox_grid_metrics(map_rect)
    sandbox_territory_buttons = {}

    for row in range(sandbox.GRID_ROWS + 1):
        y = grid_metrics["start_y"] - 2 + row * (grid_metrics["cell_size"] + grid_metrics["gap"])
        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (grid_metrics["start_x"] - 2, y),
            (
                grid_metrics["start_x"] + sandbox.GRID_COLS * grid_metrics["cell_size"] + (sandbox.GRID_COLS - 1) * grid_metrics["gap"] + 2,
                y,
            ),
            1,
        )

    for col in range(sandbox.GRID_COLS + 1):
        x = grid_metrics["start_x"] - 2 + col * (grid_metrics["cell_size"] + grid_metrics["gap"])
        pygame.draw.line(
            screen,
            PANEL_BORDER,
            (x, grid_metrics["start_y"] - 2),
            (
                x,
                grid_metrics["start_y"] + sandbox.GRID_ROWS * grid_metrics["cell_size"] + (sandbox.GRID_ROWS - 1) * grid_metrics["gap"] + 2,
            ),
            1,
        )

    for territory in sandbox.iter_territories(sandbox_state):
        territory_id = territory["id"]
        rect = get_sandbox_tile_rect(territory, map_rect)
        sandbox_territory_buttons[territory_id] = rect
        if territory["type"] == sandbox.TILE_CITY:
            color = sandbox.get_faction_color(territory["owner_faction"])
        elif territory["type"] == sandbox.TILE_EMPTY:
            color = LIGHT_GOLD
        else:
            color = BUTTON_DISABLED

        border_color = PANEL_BORDER
        if territory_id in valid_target_ids:
            border_color = GREEN if territory["type"] == sandbox.TILE_EMPTY else RED
        if territory_id == selected_sandbox_territory_id:
            border_color = GOLD
        pygame.draw.rect(screen, color, rect, border_radius=6)
        pygame.draw.rect(screen, border_color, rect, 2 if territory_id != selected_sandbox_territory_id else 4, border_radius=6)
        if territory_id == selected_sandbox_source_id:
            pygame.draw.rect(screen, BLUE, rect.inflate(-6, -6), 2, border_radius=5)

        label_text = get_sandbox_tile_short_label(territory)
        if label_text:
            label_font = tiny_font
            while label_font.size(label_text)[0] > rect.width - 6 and label_font != small_font:
                label_text = label_text[:-1]
            label_surface = tiny_font.render(label_text, True, BLACK if territory["type"] != sandbox.TILE_BLOCKED else TEXT_DISABLED)
            screen.blit(label_surface, label_surface.get_rect(center=(rect.centerx, rect.centery - 4)))

        coord_label = tiny_font.render(territory["coord"], True, BLACK if territory["type"] != sandbox.TILE_BLOCKED else TEXT_DISABLED)
        screen.blit(coord_label, coord_label.get_rect(center=(rect.centerx, rect.bottom - 10)))

        if territory["type"] == sandbox.TILE_CITY:
            stationed_units = sandbox.get_stationed_units(sandbox_state, territory_id)
            units_bg = pygame.Rect(rect.right - 18, rect.y + 3, 15, 15)
            pygame.draw.rect(screen, WHITE, units_bg, border_radius=11)
            pygame.draw.rect(screen, PANEL_BORDER, units_bg, 1, border_radius=11)
            units_label = tiny_font.render(str(stationed_units), True, BLACK)
            screen.blit(units_label, units_label.get_rect(center=units_bg.center))

    reserve_count = small_font.render(f"Ready: {len(field_team)}/{sandbox.FIELD_TEAM_CAPACITY}", True, BLACK)
    if selected_source is not None:
        if city_units:
            dispatch_hint_text = "Click a city unit to dispatch it to the attack team."
        else:
            dispatch_hint_text = "This city is empty. No units are available to dispatch."
    else:
        dispatch_hint_text = "Select an owned city to view dispatchable units."
    screen.blit(reserve_count, (attack_rect.right - reserve_count.get_width() - 12, attack_rect.y + 10))
    draw_panel_lines([dispatch_hint_text], city_rect, start_y=34, render_font=tiny_font, line_height=18)
    for index, rect in enumerate(sandbox_city_unit_buttons):
        active = index < len(city_units)
        enabled = active and can_recall_garrison
        fill_color = LIGHT_GOLD if active else BUTTON_DISABLED
        text_color = BLACK if active else TEXT_DISABLED
        pygame.draw.rect(screen, fill_color, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD if enabled else PANEL_BORDER, rect, 2, border_radius=10)
        token_label = small_font.render(city_units[index]["name"] if active else "Empty", True, text_color)
        screen.blit(token_label, token_label.get_rect(center=rect.center))

    for index, rect in enumerate(sandbox_field_unit_buttons):
        available = index < len(field_team)
        fill_color = LIGHT_BLUE if available else BUTTON_DISABLED
        text_color = BLACK if available else TEXT_DISABLED
        pygame.draw.rect(screen, fill_color, rect, border_radius=10)
        pygame.draw.rect(screen, GOLD if available and can_assign_garrison else PANEL_BORDER, rect, 2, border_radius=10)
        token_label = small_font.render(field_team[index]["name"] if available else "Empty", True, text_color)
        index_label = tiny_font.render(f"Slot {index + 1}", True, text_color)
        screen.blit(token_label, token_label.get_rect(center=(rect.centerx, rect.centery - 8)))
        screen.blit(index_label, index_label.get_rect(center=(rect.centerx, rect.centery + 12)))
    draw_panel_lines(
        ["Click an attack-team unit to return it to the selected city."],
        attack_rect,
        start_y=34,
        render_font=tiny_font,
        line_height=18,
    )

    panel_rect = pygame.Rect(PANEL_X - 10, 0, PANEL_WIDTH + 20, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (PANEL_X - 10, 0), (PANEL_X - 10, HEIGHT), 3)

    faction_rect = draw_panel_section_rect(layout["sidebar_panels"]["faction"], "Faction", title_render_font=font)
    player_faction = sandbox.get_faction(sandbox.get_player_faction(sandbox_state))
    faction_lines = [
        player_faction["name"],
        f"Gold: {get_gold_for_mode('sandbox')}",
        f"Cities: {sum(1 for territory in sandbox.iter_territories(sandbox_state) if territory['type'] == sandbox.TILE_CITY and territory['owner_faction'] == player_faction['id'])}",
    ]
    draw_panel_lines(faction_lines, faction_rect, start_y=30, render_font=small_font, line_height=20)

    territory_rect = draw_panel_section_rect(layout["sidebar_panels"]["territory"], "Territory", title_render_font=font)
    if selected_territory is None:
        territory_lines = ["Select a tile.", "Owned cities can be used as sources."]
    else:
        if selected_territory["type"] == sandbox.TILE_CITY:
            owner_label = sandbox.get_faction_name(selected_territory["owner_faction"])
            units_label = sandbox.get_stationed_units(sandbox_state, selected_territory["id"])
        elif selected_territory["type"] == sandbox.TILE_EMPTY:
            owner_label = "None"
            units_label = 0
        else:
            owner_label = "Blocked"
            units_label = 0
        territory_lines = [
            f"{selected_territory['name']} ({selected_territory['coord']})",
            f"Type: {selected_territory['type'].title()}",
            f"Owner: {owner_label}",
            f"Reward: {selected_territory['reward']}",
            f"Units: {units_label}",
            f"Dispatchable: {dispatchable_units if selected_territory['id'] == selected_sandbox_source_id else 0}",
            f"Target: {'Valid' if selected_territory['id'] in valid_target_ids else 'No'}",
        ]
    draw_panel_lines(territory_lines, territory_rect, start_y=30, render_font=small_font, line_height=19)

    orders_rect = draw_panel_section_rect(layout["sidebar_panels"]["orders"], "Orders", title_render_font=font)
    draw_panel_lines(
        [
            "1. Select an owned city as your source.",
            "2. Adjacent enemy cities can be attacked.",
            "3. Adjacent +500 tiles capture instantly.",
            "4. City units and attack team still transfer below.",
            f"City capacity: {sandbox.MIN_GARRISON_UNITS}-{sandbox.MAX_GARRISON_UNITS}.",
        ],
        orders_rect,
        start_y=30,
        render_font=tiny_font,
        line_height=18,
    )

    neighbors_rect = draw_panel_section_rect(layout["sidebar_panels"]["neighbors"], "Neighbors", title_render_font=font)
    if selected_territory is None:
        neighbor_lines = ["No tile selected."]
    else:
        neighbor_lines = [
            f"{sandbox.get_territory(sandbox_state, neighbor_id)['name']} ({sandbox.get_territory(sandbox_state, neighbor_id)['coord']})"
            for neighbor_id in selected_territory["neighbors"][:4]
        ]
        if selected_source is not None:
            neighbor_lines.append(f"Targets: {len(valid_target_ids)}")
    draw_panel_lines(neighbor_lines, neighbors_rect, start_y=30, render_font=tiny_font, line_height=18)

    draw_button(layout["buttons"]["shop"], "Shop", fill_color=BUTTON)
    draw_button(layout["buttons"]["save"], "Save Game", fill_color=BUTTON)
    draw_button(layout["buttons"]["return"], "Return Mode", fill_color=BUTTON)


def draw_shop_scene():
    panel_menu.x = 46
    panel_menu.y = 180
    panel_menu.width = 420
    panel_menu.button_height = 22
    panel_menu.gap = 4
    panel_menu.set_options(
        [
            {
                "key": item["id"],
                "label": shop.stock_label(item["id"], get_shop_stock_for_mode(shop_context).get(item["id"], 0)),
                "enabled": get_shop_stock_for_mode(shop_context).get(item["id"], 0) > 0,
            }
            for item in shop.SHOP_ITEMS
        ]
    )

    title = menu_title_font.render("Armory & Supply", True, BLACK)
    subtitle = title_font.render("Buy equipment for convoy before battle", True, BLACK)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 72)))
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 114)))

    list_rect = pygame.Rect(28, 148, 456, 610)
    pygame.draw.rect(screen, BUTTON, list_rect, border_radius=10)
    pygame.draw.rect(screen, PANEL_BORDER, list_rect, 2, border_radius=10)
    panel_menu.draw(screen, small_font, MENU_COLORS)

    panel_rect = pygame.Rect(PANEL_X - 10, 0, PANEL_WIDTH + 20, HEIGHT)
    pygame.draw.rect(screen, PANEL_BG, panel_rect)
    pygame.draw.line(screen, PANEL_BORDER, (PANEL_X - 10, 0), (PANEL_X - 10, HEIGHT), 3)
    draw_button(shop_back_button, "Return", fill_color=BUTTON)

    wallet_rect = draw_panel_section("Wallet", PANEL_HEADER_Y, PANEL_HEADER_HEIGHT)
    draw_panel_lines(
        [
            f"Context: {'Sandbox' if shop_context == 'sandbox' else 'Chapter'}",
            f"Gold: {get_gold_for_mode(shop_context)}",
            f"Convoy: {len(get_convoy_for_mode(shop_context))} items",
        ],
        wallet_rect,
        start_y=12,
    )

    info_rect = draw_panel_section("Stock", PANEL_UNIT_Y, PANEL_UNIT_HEIGHT)
    draw_panel_lines(
        [
            "Each item starts with 9 stock.",
            "Purchased items go to convoy.",
            "Killer weapons grant CRT +30.",
            "Open prep to assign loadouts.",
        ],
        info_rect,
    )

    convoy_rect = draw_panel_section("Convoy", PANEL_ACTION_Y, PANEL_ACTION_HEIGHT)
    convoy_lines = [item_label(item) for item in get_convoy_for_mode(shop_context)[-5:]]
    if not convoy_lines:
        convoy_lines = ["No stored items."]
    draw_panel_lines(convoy_lines, convoy_rect)

    message_rect = draw_panel_section("Status", PANEL_PREVIEW_Y, PANEL_PREVIEW_HEIGHT + 30)
    draw_panel_lines([shop_message or "Choose an item to buy."], message_rect)


def handle_action_menu_click(key):
    global interaction_state, preview_target, action_panel_scroll
    if key == "attack":
        interaction_state = "targeting_attack"
        clear_attack_forecast()
    elif key == "wait":
        finish_selected_action()
    elif key == "item":
        interaction_state = "item_menu"
        clear_attack_forecast()
        action_panel_scroll = 0


def handle_item_menu_click(selection):
    global interaction_state, action_panel_scroll
    if selection == "back":
        interaction_state = "planning"
        action_panel_scroll = 0
        return
    use_inventory_item(selection)


def handle_tactical_cancel():
    global interaction_state, preview_target

    if level_up_popups:
        dismiss_level_up_popup()
        return

    if is_animation_blocking_input():
        return

    if interaction_state == "targeting_attack":
        cancel_attack_targeting()
        return

    if interaction_state == "item_menu":
        interaction_state = "planning"
        clear_attack_forecast()
        return

    if threat_enemy_unit is not None:
        clear_threat_enemy()
        preview_target = None
        return

    if phase == "START" and selected_unit is not None:
        clear_selection()


def handle_panel_click(position, panel_controls):
    global combat_speed

    start_button = panel_controls["start"]
    end_turn_button = panel_controls["end_turn"]
    shop_button = panel_controls["shop"]
    speed_1x = panel_controls.get("speed_1x")
    speed_2x = panel_controls.get("speed_2x")

    if speed_1x is not None and speed_1x.collidepoint(position):
        combat_speed = 1
        return

    if speed_2x is not None and speed_2x.collidepoint(position):
        combat_speed = 2
        return

    if is_animation_blocking_input():
        return

    if end_turn_button is not None and end_turn_button.collidepoint(position):
        if battle_mode == "sandbox" and phase == "PLAYER":
            begin_enemy_phase()
        return

    if shop_button is not None and shop_button.collidepoint(position):
        if phase == "START" and battle_mode == "chapter":
            return_to_chapter_select()
            return
        if phase == "START" and battle_mode == "sandbox":
            return_to_sandbox_map()
            return
        open_shop(scene, get_preparation_mode())
        return

    if start_button.collidepoint(position) and phase in {"VICTORY", "DEFEAT"}:
        if battle_mode == "sandbox":
            return_to_sandbox_map()
        elif phase == "VICTORY":
            return_to_chapter_select()
        return

    if start_button.collidepoint(position) and phase == "START":
        start_battle()
        return

    if phase == "START":
        clicked = get_action_entry_clicked(position) if is_scrollable_action_state() else panel_menu.get_clicked(position)
        if clicked is not None:
            handle_prep_menu_click(clicked)
        return

    if phase in {"VICTORY", "DEFEAT"}:
        return

    if interaction_state not in {"planning", "item_menu"}:
        return

    clicked = get_action_entry_clicked(position) if is_scrollable_action_state() else panel_menu.get_clicked(position)
    if clicked is None:
        return

    selection = menu_actions.get(clicked)
    if interaction_state == "planning":
        handle_action_menu_click(selection)
    elif interaction_state == "item_menu":
        handle_item_menu_click(selection)


def handle_board_click(gx, gy):
    global interaction_state, preview_target, selected_unit
    global attack_confirmation_target, attack_confirmation_position
    global selected_board_tile, hovered_board_tile, movement_preview_path

    if is_animation_blocking_input():
        return

    selected_board_tile = (gx, gy)
    hovered_board_tile = (gx, gy)
    clicked = game_map.get_unit(gx, gy)

    if clicked in alive_units(enemies):
        movement_preview_path = []
        if interaction_state == "targeting_attack":
            if attack_confirmation_target is clicked:
                execute_attack(clicked)
                return
            if clicked in enemies_in_range(selected_unit):
                preview_target = clicked
                attack_confirmation_target = clicked
                attack_confirmation_position = selected_unit.get_position()
                return
            if try_direct_attack_target(clicked):
                return
            return
        preview_target = clicked
        toggle_threat_enemy(clicked)
        clear_attack_forecast()
        if threat_enemy_unit is clicked:
            preview_target = clicked
        return

    if interaction_state == "item_menu":
        return

    if clicked in alive_units(players) and not clicked.has_acted:
        movement_preview_path = []
        if selected_unit is clicked:
            interaction_state = "planning"
            clear_attack_forecast()
        else:
            if selected_unit and not selected_unit.has_acted:
                revert_selected_to_original()
            select_unit_for_planning(clicked)
        return

    if interaction_state == "targeting_attack":
        movement_preview_path = []
        cancel_attack_targeting()
        return

    if not selected_unit or selected_unit.has_acted:
        movement_preview_path = []
        return

    if (gx, gy) == selected_unit.get_position():
        interaction_state = "planning"
        movement_preview_path = []
        clear_attack_forecast()
        return

    if can_plan_move(selected_unit, gx, gy):
        game_map.move_unit(selected_unit, gx, gy)
        update_selected_move_flag()
        interaction_state = "planning"
        movement_preview_path = []
        clear_attack_forecast()


def handle_mouse_motion(position):
    global preview_target, hovered_board_tile, movement_preview_path
    if (
        not in_tactical_battle_scene()
        or is_animation_blocking_input()
    ):
        hovered_board_tile = None
        movement_preview_path = []
        if attack_confirmation_target is None and threat_enemy_unit is None:
            preview_target = None
        elif attack_confirmation_target is None and threat_enemy_unit is not None:
            preview_target = threat_enemy_unit
        return

    gx = position[0] // CELL
    gy = (position[1] - BOARD_TOP) // CELL
    if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
        hovered_board_tile = (gx, gy)
    else:
        hovered_board_tile = None

    if phase != "PLAYER":
        movement_preview_path = []
        if attack_confirmation_target is None and threat_enemy_unit is None:
            preview_target = None
        elif attack_confirmation_target is None and threat_enemy_unit is not None:
            preview_target = threat_enemy_unit
        return

    if interaction_state != "targeting_attack":
        if (
            selected_unit is not None
            and not selected_unit.has_acted
            and hovered_board_tile is not None
            and can_plan_move(selected_unit, hovered_board_tile[0], hovered_board_tile[1])
        ):
            movement_preview_path = find_shortest_move_path_for_preview(selected_unit, hovered_board_tile)
        else:
            movement_preview_path = []
        if threat_enemy_unit is not None:
            preview_target = threat_enemy_unit
        elif attack_confirmation_target is None:
            preview_target = None
        return

    movement_preview_path = []
    if attack_confirmation_target is not None:
        preview_target = attack_confirmation_target
        return

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
    if main_menu_buttons["new"].collidepoint(position):
        scene = SCENE_MODE_SELECT
        return
    if main_menu_buttons["load"].collidepoint(position):
        open_slot_menu("load", SCENE_MENU)
        return


def handle_mode_select_click(position):
    global scene

    if slot_back_button.collidepoint(position):
        scene = SCENE_MENU
        return

    if mode_select_buttons["chapter"].collidepoint(position):
        start_new_chapter_game()
        return

    if mode_select_buttons["sandbox"].collidepoint(position):
        start_new_sandbox_game()


def handle_chapter_select_click(position):
    global scene

    if chapter_return_button.collidepoint(position):
        scene = SCENE_MODE_SELECT
        return

    if chapter_shop_button.collidepoint(position):
        open_shop(SCENE_CHAPTER_SELECT, "chapter")
        return

    if chapter_save_button.collidepoint(position):
        open_slot_menu("save", SCENE_CHAPTER_SELECT)
        return

    unlocked_chapters = set(chapter_state["chapter_progress"]["unlocked"])
    for chapter_id, rect in chapter_buttons.items():
        if rect.collidepoint(position):
            if chapter_id not in unlocked_chapters:
                return
            load_chapter(chapter_id)
            return


def handle_faction_select_click(position):
    global scene

    if sandbox_back_button.collidepoint(position):
        scene = SCENE_MODE_SELECT
        return

    for faction_id, rect in faction_buttons.items():
        if rect.collidepoint(position):
            choose_sandbox_faction(faction_id)
            return


def handle_sandbox_map_click(position):
    global scene, selected_sandbox_territory_id, selected_sandbox_source_id

    if sandbox_back_button.collidepoint(position):
        scene = SCENE_FACTION_SELECT
        return

    if sandbox_save_button.collidepoint(position):
        open_slot_menu("save", SCENE_SANDBOX_MAP)
        return

    if sandbox_shop_button.collidepoint(position):
        open_shop(SCENE_SANDBOX_MAP, "sandbox")
        return

    if selected_sandbox_source_id is not None:
        city_units = sandbox.get_territory_units(sandbox_state, selected_sandbox_source_id)
        for index, rect in enumerate(sandbox_city_unit_buttons):
            if rect.collidepoint(position) and index < len(city_units):
                sandbox.recall_field_unit(sandbox_state, selected_sandbox_source_id, index)
                return

    for territory_id, rect in sandbox_territory_buttons.items():
        if rect.collidepoint(position):
            selected_sandbox_territory_id = territory_id
            if sandbox.is_player_owned(sandbox_state, territory_id):
                selected_sandbox_source_id = territory_id
                return
            valid_targets = set(
                sandbox.get_valid_targets_from_source(sandbox_state, selected_sandbox_source_id)
            ) if selected_sandbox_source_id is not None else set()
            if territory_id in valid_targets:
                if sandbox.is_empty_reward_tile(sandbox_state, territory_id):
                    if sandbox.capture_empty_tile(sandbox_state, territory_id):
                        sync_gold_from_sandbox()
                        selected_sandbox_source_id = territory_id
                    return
                start_sandbox_battle(territory_id)
            return

    if selected_sandbox_source_id is None:
        return

    field_team = sandbox.get_field_team(sandbox_state)
    for index, rect in enumerate(sandbox_field_unit_buttons):
        if rect.collidepoint(position) and index < len(field_team):
            sandbox.assign_field_unit(sandbox_state, selected_sandbox_source_id, index)
            return


def handle_shop_click(position):
    if shop_back_button.collidepoint(position):
        close_shop()
        return

    clicked = panel_menu.get_clicked(position)
    if clicked is not None:
        buy_shop_item(clicked)


def handle_slot_menu_click(position):
    global pending_save_slot, save_message, slot_clear_mode

    if slot_back_button.collidepoint(position):
        close_slot_menu()
        return

    if slot_clear_button.collidepoint(position):
        slot_clear_mode = not slot_clear_mode
        pending_save_slot = None
        save_message = "Select a manual slot to clear." if slot_clear_mode else ""
        return

    for slot, rect in save_slot_buttons.items():
        if not rect.collidepoint(position):
            continue
        if slot_clear_mode:
            handle_clear_slot(slot)
            return
        if save_menu_mode == "save":
            handle_save_slot(slot)
        else:
            pending_save_slot = None
            save_message = ""
            handle_load_slot(slot)
        return


def handle_game_click(position, panel_controls):
    if position[0] >= PANEL_X - 10:
        handle_panel_click(position, panel_controls)
        return

    if is_animation_blocking_input():
        return

    if phase == "START":
        gx = position[0] // CELL
        gy = (position[1] - BOARD_TOP) // CELL
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            clicked = game_map.get_unit(gx, gy)
            if clicked in alive_units(players):
                select_unit_for_preparation(clicked)
            else:
                clear_selection()
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
    elif scene == SCENE_MODE_SELECT:
        draw_mode_select_scene()
    elif scene == SCENE_CHAPTER_SELECT:
        draw_chapter_select_scene()
    elif scene == SCENE_FACTION_SELECT:
        draw_faction_select_scene()
    elif scene in {SCENE_SAVE_MENU, SCENE_LOAD_MENU}:
        draw_slot_menu_scene()
    elif scene == SCENE_SANDBOX_MAP:
        draw_sandbox_map_scene()
    elif scene == SCENE_SHOP:
        draw_shop_scene()
    elif scene in {SCENE_GAME, SCENE_SANDBOX_BATTLE}:
        start_button = draw_game_scene()

    return start_button


def handle_events(start_button):
    running = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEWHEEL and in_tactical_battle_scene() and phase != "START":
            hovered_panel = get_hovered_tactical_panel(pygame.mouse.get_pos())
            if hovered_panel == "log":
                scroll_battle_log(event.y)
            elif hovered_panel == "action" and is_scrollable_action_state():
                scroll_action_panel(-event.y)

        if event.type == pygame.MOUSEWHEEL and in_tactical_battle_scene() and phase == "START":
            hovered_panel = get_hovered_tactical_panel(pygame.mouse.get_pos())
            if hovered_panel == "action" and is_scrollable_action_state():
                scroll_action_panel(-event.y)

        if event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event.pos)

        if event.type == pygame.KEYDOWN and in_tactical_battle_scene():
            if event.key == pygame.K_ESCAPE:
                handle_tactical_cancel()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if in_tactical_battle_scene() and level_up_popups:
                dismiss_level_up_popup()
                continue

            if in_tactical_battle_scene() and event.button == 3:
                handle_tactical_cancel()
                continue

            mouse_pos = event.pos

            if scene == SCENE_MENU:
                handle_menu_click(mouse_pos)
            elif scene == SCENE_MODE_SELECT:
                handle_mode_select_click(mouse_pos)
            elif scene == SCENE_CHAPTER_SELECT:
                handle_chapter_select_click(mouse_pos)
            elif scene == SCENE_FACTION_SELECT:
                handle_faction_select_click(mouse_pos)
            elif scene in {SCENE_SAVE_MENU, SCENE_LOAD_MENU}:
                handle_slot_menu_click(mouse_pos)
            elif scene == SCENE_SANDBOX_MAP:
                handle_sandbox_map_click(mouse_pos)
            elif scene == SCENE_SHOP:
                handle_shop_click(mouse_pos)
            elif scene in {SCENE_GAME, SCENE_SANDBOX_BATTLE} and start_button is not None:
                handle_game_click(mouse_pos, start_button)

    return running


def update_frame():
    if combat_animation is not None:
        update_combat_animation()
        return

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
    global pygame, screen, font, small_font, tiny_font, title_font, menu_title_font, menu_button_font
    global UNIT_SPRITES, TERRAIN_OVERLAYS, panel_menu, main_menu_buttons, chapter_buttons
    global faction_buttons, sandbox_territory_buttons, sandbox_city_unit_buttons, sandbox_field_unit_buttons, save_slot_buttons
    global chapter_return_button, chapter_shop_button, chapter_save_button
    global sandbox_shop_button, sandbox_save_button, sandbox_send_button, sandbox_recall_button
    global shop_back_button, sandbox_back_button, slot_back_button
    global chapter_state, persistent_roster, sandbox_state
    global victory_saved, sandbox_result_applied, shop_message, FIRST_FRAME_LOGGED, battle_log_scroll
    global save_menu_mode, save_return_scene, save_message, pending_save_slot, active_save_slot

    if pygame is not None and hasattr(pygame, "quit"):
        pygame.quit()
    pygame = None
    screen = None
    font = None
    small_font = None
    tiny_font = None
    title_font = None
    menu_title_font = None
    menu_button_font = None
    UNIT_SPRITES = {}
    TERRAIN_OVERLAYS = {}
    panel_menu = None
    main_menu_buttons = {}
    chapter_buttons = {}
    faction_buttons = {}
    sandbox_territory_buttons = {}
    sandbox_city_unit_buttons = []
    sandbox_field_unit_buttons = []
    save_slot_buttons = {}
    chapter_return_button = None
    chapter_shop_button = None
    chapter_save_button = None
    sandbox_shop_button = None
    sandbox_save_button = None
    sandbox_send_button = None
    sandbox_recall_button = None
    shop_back_button = None
    sandbox_back_button = None
    slot_back_button = None
    chapter_state = {}
    persistent_roster = {}
    sandbox_state = None
    victory_saved = False
    sandbox_result_applied = False
    shop_message = ""
    save_menu_mode = "save"
    save_return_scene = SCENE_MENU
    save_message = ""
    pending_save_slot = None
    active_save_slot = None
    battle_log_scroll = 0
    FIRST_FRAME_LOGGED = False


def main():
    init_game()
    try:
        running = True
        while running:
            running = run_frame()
    finally:
        shutdown()
