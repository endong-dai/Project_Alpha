"""
save_system.py
Local JSON save and load helpers.
"""

from datetime import datetime
import json
import os

import progression
import sandbox
import shop

MAX_SAVE_SLOTS = 3
AUTO_SAVE_SLOT = "auto"
SAVE_SLOT_FILES = {
    slot: os.path.normpath(os.path.join(os.path.dirname(__file__), f"../save_slot_{slot}.json"))
    for slot in range(1, MAX_SAVE_SLOTS + 1)
}
SAVE_SLOT_FILES[AUTO_SAVE_SLOT] = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "../save_auto.json")
)


def _default_chapter_progress():
    return {
        "clears": {"1": 0, "2": 0},
        "unlocked": [1, 2],
    }


def _build_chapter_state(shared_convoy, shared_shop_stock):
    return {
        "gold": shop.STARTING_GOLD,
        "convoy": shared_convoy,
        "shop_stock": shared_shop_stock,
        "chapter_progress": _default_chapter_progress(),
    }


def _attach_shared_state(chapter_state, sandbox_state):
    sandbox_state["convoy"] = chapter_state["convoy"]
    sandbox_state["shop_stock"] = chapter_state["shop_stock"]
    player_faction = sandbox_state.get("player_faction")
    if player_faction:
        sandbox_state["treasuries"][player_faction] = chapter_state["gold"]


def new_game_state():
    shared_convoy = []
    shared_shop_stock = shop.create_shop_stock()
    chapter_state = _build_chapter_state(shared_convoy, shared_shop_stock)
    sandbox_state = sandbox.create_sandbox_state()
    _attach_shared_state(chapter_state, sandbox_state)

    return {
        "chapter_state": chapter_state,
        "sandbox_state": sandbox_state,
        "roster": progression.create_initial_roster(),
    }


def _normalize_chapter_state(raw):
    shared_convoy = []
    for item_data in raw.get("convoy", []):
        item = progression.deserialize_item(item_data)
        if item is not None:
            shared_convoy.append(item)

    shared_shop_stock = shop.create_shop_stock()
    for item_id, stock in raw.get("shop_stock", {}).items():
        if item_id in shared_shop_stock:
            shared_shop_stock[item_id] = max(0, int(stock))

    chapter_state = _build_chapter_state(shared_convoy, shared_shop_stock)
    chapter_state["gold"] = max(0, int(raw.get("gold", shop.STARTING_GOLD)))

    saved_progress = raw.get("chapter_progress", {})
    progress = _default_chapter_progress()
    progress["clears"].update(
        {
            chapter_id: max(0, int(value))
            for chapter_id, value in saved_progress.get("clears", {}).items()
            if chapter_id in progress["clears"]
        }
    )
    unlocked = [
        int(chapter_id)
        for chapter_id in saved_progress.get("unlocked", progress["unlocked"])
        if int(chapter_id) in {1, 2}
    ]
    progress["unlocked"] = unlocked or [1, 2]
    chapter_state["chapter_progress"] = progress
    return chapter_state


def _normalize_sandbox_state(raw, chapter_state):
    default_state = sandbox.create_sandbox_state()
    saved_player_faction = raw.get("player_faction")
    if saved_player_faction not in sandbox.FACTION_LOOKUP:
        saved_player_faction = None
    sandbox_state = {
        "player_faction": saved_player_faction,
        "territories": default_state["territories"],
        "treasuries": default_state["treasuries"],
        "faction_sizes": raw.get("faction_sizes", default_state["faction_sizes"]),
        "field_team": [],
        "field_units": 0,
        "next_unit_id": 1,
    }

    saved_territories = raw.get("territories", {})
    normalized_territories = {}
    for territory_id, default_territory in default_state["territories"].items():
        saved = saved_territories.get(str(territory_id), saved_territories.get(territory_id, {}))
        territory = dict(default_territory)
        saved_type = saved.get("type", territory.get("type"))
        if saved_type in {sandbox.TILE_CITY, sandbox.TILE_EMPTY, sandbox.TILE_BLOCKED}:
            territory["type"] = saved_type
        saved_owner = saved.get("owner_faction", territory["owner_faction"])
        if territory["type"] == sandbox.TILE_CITY and saved_owner in sandbox.FACTION_LOOKUP:
            territory["owner_faction"] = saved_owner
        elif territory["type"] != sandbox.TILE_CITY:
            territory["owner_faction"] = None
        saved_name = saved.get("name")
        if isinstance(saved_name, str) and saved_name:
            territory["name"] = saved_name
        saved_units = saved.get("units")
        if territory["type"] != sandbox.TILE_CITY:
            territory["units"] = []
        elif isinstance(saved_units, list):
            territory["units"] = [sandbox.clone_named_unit(unit_data) for unit_data in saved_units[:sandbox.MAX_GARRISON_UNITS]]
        else:
            unit_count = sandbox.clamp_stationed_units(int(saved.get("stationed_units", territory["stationed_units"])))
            territory["units"] = sandbox.create_named_units(sandbox_state, unit_count)
        territory["stationed_units"] = len(territory["units"])
        normalized_territories[territory_id] = territory

    sandbox_state["territories"] = normalized_territories
    saved_field_team = raw.get("field_team")
    if isinstance(saved_field_team, list):
        sandbox_state["field_team"] = [
            sandbox.clone_named_unit(unit_data)
            for unit_data in saved_field_team[:sandbox.FIELD_TEAM_CAPACITY]
        ]
    else:
        field_units = sandbox.clamp_field_units(int(raw.get("field_units", sandbox.PLAYER_STARTING_FIELD_UNITS)))
        sandbox_state["field_team"] = sandbox.create_named_units(sandbox_state, field_units)

    for faction_id in sandbox_state["treasuries"]:
        sandbox_state["treasuries"][faction_id] = max(
            0,
            int(raw.get("treasuries", {}).get(faction_id, sandbox_state["treasuries"][faction_id])),
        )

    sandbox.sync_unit_counts(sandbox_state)
    _attach_shared_state(chapter_state, sandbox_state)
    return sandbox_state


def _normalize_roster(raw):
    default_roster = progression.create_initial_roster()
    normalized = {}

    for unit_id, default_record in default_roster.items():
        saved = raw.get(unit_id, {})
        inventory = []
        for item_data in saved.get("inventory", default_record["inventory"]):
            item = progression.deserialize_item(item_data)
            if item is not None:
                inventory.append(progression.serialize_item(item))

        normalized[unit_id] = {
            "unit_id": unit_id,
            "name": saved.get("name", default_record["name"]),
            "class_id": saved.get("class_id", default_record["class_id"]),
            "class_name": saved.get("class_name", default_record["class_name"]),
            "allowed_weapon_types": list(saved.get("allowed_weapon_types", default_record["allowed_weapon_types"])),
            "level": max(1, int(saved.get("level", default_record["level"]))),
            "exp": max(0, int(saved.get("exp", default_record["exp"]))),
            "hp": max(0, int(saved.get("hp", default_record["hp"]))),
            "max_hp": max(1, int(saved.get("max_hp", default_record["max_hp"]))),
            "strength": max(0, int(saved.get("strength", default_record["strength"]))),
            "magic": max(0, int(saved.get("magic", default_record["magic"]))),
            "defense": max(0, int(saved.get("defense", default_record["defense"]))),
            "resistance": max(0, int(saved.get("resistance", default_record["resistance"]))),
            "speed": max(0, int(saved.get("speed", default_record["speed"]))),
            "crit": max(0, int(saved.get("crit", default_record.get("crit", 5)))),
            "move": max(1, int(saved.get("move", default_record["move"]))),
            "sprite_key": saved.get("sprite_key", default_record["sprite_key"]),
            "inventory": inventory or list(default_record["inventory"]),
            "equipped_index": int(saved.get("equipped_index", default_record["equipped_index"])),
        }

        normalized[unit_id]["hp"] = min(normalized[unit_id]["hp"], normalized[unit_id]["max_hp"])

    return normalized


def _normalize_game_state(raw):
    chapter_state = _normalize_chapter_state(raw.get("chapter_state", {}))
    sandbox_state = _normalize_sandbox_state(raw.get("sandbox_state", {}), chapter_state)
    roster = _normalize_roster(raw.get("roster", {}))
    return {
        "chapter_state": chapter_state,
        "sandbox_state": sandbox_state,
        "roster": roster,
    }


def _serialize_game_state(game_state):
    sandbox.sync_unit_counts(game_state["sandbox_state"])
    return {
        "chapter_state": {
            "gold": game_state["chapter_state"]["gold"],
            "convoy": [progression.serialize_item(item) for item in game_state["chapter_state"]["convoy"]],
            "shop_stock": dict(game_state["chapter_state"]["shop_stock"]),
            "chapter_progress": game_state["chapter_state"]["chapter_progress"],
        },
        "sandbox_state": {
            "player_faction": game_state["sandbox_state"].get("player_faction"),
            "territories": {
                str(territory_id): {
                    "id": territory["id"],
                    "type": territory.get("type"),
                    "name": territory["name"],
                    "owner_faction": territory["owner_faction"],
                    "neighbors": list(territory["neighbors"]),
                    "grid": list(territory["grid"]),
                    "reward": territory["reward"],
                    "stationed_units": territory["stationed_units"],
                    "units": [sandbox.clone_named_unit(unit_data) for unit_data in territory.get("units", [])],
                }
                for territory_id, territory in game_state["sandbox_state"]["territories"].items()
            },
            "treasuries": dict(game_state["sandbox_state"]["treasuries"]),
            "faction_sizes": dict(game_state["sandbox_state"]["faction_sizes"]),
            "field_units": game_state["sandbox_state"]["field_units"],
            "field_team": [sandbox.clone_named_unit(unit_data) for unit_data in game_state["sandbox_state"].get("field_team", [])],
        },
        "roster": game_state["roster"],
    }


def _slot_path(slot):
    if slot not in SAVE_SLOT_FILES:
        raise ValueError(f"Invalid save slot: {slot}")
    return SAVE_SLOT_FILES[slot]


def _build_slot_summary(game_state, resume_context, timestamp):
    scene = resume_context.get("scene", "MENU")
    chapter_progress = game_state["chapter_state"]["chapter_progress"]
    sandbox_state = game_state["sandbox_state"]
    player_faction = sandbox_state.get("player_faction")
    territory_count = 0
    faction_name = "Unselected"
    if player_faction:
        faction_name = sandbox.get_faction_name(player_faction)
        territory_count = sum(
            1
            for territory in sandbox.iter_territories(sandbox_state)
            if territory.get("type") == sandbox.TILE_CITY and territory["owner_faction"] == player_faction
        )

    if scene == "CHAPTER_PREP":
        location = f"Chapter {resume_context.get('chapter_id', '?')} Prep"
        mode = "Chapter"
    elif scene == "SANDBOX_PREP":
        location = "Sandbox Prep"
        mode = "Sandbox"
    elif scene == "SANDBOX_MAP":
        location = "Sandbox Map"
        mode = "Sandbox"
    elif scene == "CHAPTER_SELECT":
        location = "Chapter Select"
        mode = "Chapter"
    else:
        location = "Main Menu"
        mode = "Menu"

    return {
        "mode": mode,
        "location": location,
        "gold": game_state["chapter_state"]["gold"],
        "timestamp": timestamp,
        "chapter_clears": dict(chapter_progress["clears"]),
        "sandbox_faction": faction_name,
        "sandbox_territories": territory_count,
    }


def _read_slot_info(slot):
    path = _slot_path(slot)
    info = {
        "slot": slot,
        "exists": False,
        "corrupt": False,
        "summary": None,
        "is_auto": slot == AUTO_SAVE_SLOT,
    }
    if not os.path.exists(path):
        return info

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError("Invalid save slot payload.")
        info["exists"] = True
        info["summary"] = raw.get("meta", {}).get("summary")
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        info["exists"] = True
        info["corrupt"] = True
    return info


def list_save_slots(include_auto=False):
    slots = []
    if include_auto:
        slots.append(_read_slot_info(AUTO_SAVE_SLOT))

    for slot in range(1, MAX_SAVE_SLOTS + 1):
        path = _slot_path(slot)
        slots.append(_read_slot_info(slot))
    return slots


def save_game_to_slot(slot, game_state, resume_context):
    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
    payload = {
        "meta": {
            "slot": slot,
            "summary": _build_slot_summary(game_state, resume_context, timestamp),
        },
        "resume": dict(resume_context),
        "game_state": _serialize_game_state(game_state),
    }

    try:
        with open(_slot_path(slot), "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return True
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return False


def clear_save_slot(slot):
    if slot == AUTO_SAVE_SLOT or slot not in SAVE_SLOT_FILES:
        return False

    path = _slot_path(slot)
    if not os.path.exists(path):
        return True

    try:
        os.remove(path)
        return True
    except OSError:
        return False


def load_game_from_slot(slot):
    path = _slot_path(slot)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = json.load(handle)
        if not isinstance(raw, dict):
            raise ValueError("Save data root must be a dictionary.")
        game_state = _normalize_game_state(raw.get("game_state", raw))
        return {
            "meta": raw.get("meta", {}),
            "resume": raw.get("resume", {}),
            "game_state": game_state,
        }
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None
