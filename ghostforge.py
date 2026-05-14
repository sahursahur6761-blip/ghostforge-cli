import os
import json
import sys
import argparse

# Constants
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_FILE = os.path.join(SCRIPT_DIR, 'vault.json')
HACKER_COLOR = '\033[32m'  # Green
BOSS_COLOR = '\033[31m'    # Red
MISSION_COLOR = '\033[34m' # Blue
RESET = '\033[0m'

BANNER = r"""
   ______ __                      __ ______
  / ____// /_   ____   _____ / /_/ ____/____   _____ ____ _ ___
 / / __ / __ \ / __ \ / ___// __// /_   / __ \ / ___// __ `// _ \
/ /_/ // / / // /_/ /(__  )/ /_ / __/  / /_/ // /   / /_/ //  __/
\____//_/ /_/ \____//____/ \__//_/     \____//_/    \__, / \___/
                                                   /____/
"""

def print_hacker(text, color=HACKER_COLOR, bold=False):
    if bold:
        # Assumes color is in format \033[Xm or \033[XXm
        code = color.lstrip('\033[').rstrip('m')
        print(f"\033[{code};1m{text}{RESET}")
    else:
        print(f"{color}{text}{RESET}")

def load_vault():
    if not os.path.exists(VAULT_FILE):
        return {
            "player": {
                "level": 1,
                "xp": 0,
                "xp_to_next": 100
            },
            "missions": []
        }
    try:
        with open(VAULT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {
            "player": {"level": 1, "xp": 0, "xp_to_next": 100},
            "missions": []
        }

def save_vault(data):
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print_hacker(f"[ERROR] Could not secure the vault: {e}", BOSS_COLOR)

def add_mission(vault, title, description, difficulty):
    # Ensure ID is unique even if missions are deleted
    max_id = max([m["id"] for m in vault["missions"]], default=0)
    mission = {
        "id": max_id + 1,
        "title": title,
        "description": description,
        "difficulty": difficulty,
        "status": "active"
    }
    vault["missions"].append(mission)
    save_vault(vault)
    print_hacker(f"[*] New mission accepted: {title}")

def list_missions(vault, show_all=False):
    print_hacker("=== MISSION LOG ===", MISSION_COLOR, bold=True)
    missions_to_show = vault["missions"] if show_all else [m for m in vault["missions"] if m["status"] == "active"]

    if not missions_to_show:
        print_hacker("No active missions. The grid is quiet.")
        return

    for m in missions_to_show:
        status_icon = "[✓]" if m["status"] == "complete" else "[ ]"
        print_hacker(f"{status_icon} {m['id']}: {m['title']} (Rank: {m['difficulty']})")

def delete_mission(vault, mission_id):
    original_count = len(vault["missions"])
    vault["missions"] = [m for m in vault["missions"] if m["id"] != mission_id]
    if len(vault["missions"]) < original_count:
        save_vault(vault)
        print_hacker(f"[-] Mission {mission_id} purged from the vault.")
    else:
        print_hacker(f"[!] Mission {mission_id} not found in the grid.", BOSS_COLOR)

def show_mission_details(vault, mission_id):
    for m in vault["missions"]:
        if m["id"] == mission_id:
            print_hacker(f"=== MISSION DATA: {m['id']} ===", MISSION_COLOR, bold=True)
            print_hacker(f"Title: {m['title']}")
            print_hacker(f"Rank: {m['difficulty']}")
            print_hacker(f"Status: {m['status']}")
            print_hacker(f"Intel: {m['description']}")
            return
    print_hacker(f"[!] Intel for mission {mission_id} is missing.", BOSS_COLOR)

def complete_mission(vault, mission_id):
    for m in vault["missions"]:
        if m["id"] == mission_id and m["status"] == "active":
            m["status"] = "complete"
            xp_gain = m["difficulty"] * 25
            vault["player"]["xp"] += xp_gain
            print_hacker(f"[+] Mission complete! Gained {xp_gain} XP.")
            check_level_up(vault)
            save_vault(vault)
            return
    print_hacker("[!] Mission not found or already neutralized.", BOSS_COLOR)

def check_level_up(vault):
    p = vault["player"]
    while p["xp"] >= p["xp_to_next"]:
        p["xp"] -= p["xp_to_next"]
        p["level"] += 1
        p["xp_to_next"] = int(p["xp_to_next"] * 1.5)
        print_hacker(f"[!!!] LEVEL UP! You are now Level {p['level']}.", BOSS_COLOR)

def show_status(vault):
    p = vault["player"]
    print_hacker("=== OPERATIVE STATUS ===", HACKER_COLOR, bold=True)
    print_hacker(f"Level: {p['level']}")
    print_hacker(f"XP: {p['xp']} / {p['xp_to_next']}")

    active = [m for m in vault["missions"] if m["status"] == "active"]
    completed = [m for m in vault["missions"] if m["status"] == "complete"]
    print_hacker(f"Missions: {len(active)} active, {len(completed)} completed")

def main():
    parser = argparse.ArgumentParser(description="GhostForge CLI - Offline RPG Project Manager")
    subparsers = parser.add_subparsers(dest="command")

    # Add Mission
    add_parser = subparsers.add_parser('mission', help='Accept a new mission')
    add_parser.add_argument('title', help='Mission title')
    add_parser.add_argument('--desc', default='No description provided.', help='Mission description')
    add_parser.add_argument('--rank', type=int, default=1, help='Mission rank (1-5)')

    # List Missions
    list_parser = subparsers.add_parser('list', help='List all missions')
    list_parser.add_argument('--all', action='store_true', help='Show all missions (including completed)')

    # View Mission
    view_parser = subparsers.add_parser('view', help='View mission intel')
    view_parser.add_argument('id', type=int, help='Mission ID')

    # Complete Mission
    comp_parser = subparsers.add_parser('complete', help='Neutralize a mission')
    comp_parser.add_argument('id', type=int, help='Mission ID')

    # Delete Mission
    del_parser = subparsers.add_parser('purge', help='Purge a mission from the grid')
    del_parser.add_argument('id', type=int, help='Mission ID')

    # Status
    subparsers.add_parser('status', help='Show operative status')

    args = parser.parse_args()

    # Print Banner for main commands
    if args.command:
        print_hacker(BANNER, BOSS_COLOR)
    else:
        print_hacker(BANNER, BOSS_COLOR)
        parser.print_help()
        sys.exit(0)

    vault = load_vault()

    if args.command == 'mission':
        add_mission(vault, args.title, args.desc, args.rank)
    elif args.command == 'list':
        list_missions(vault, args.all)
    elif args.command == 'view':
        show_mission_details(vault, args.id)
    elif args.command == 'complete':
        complete_mission(vault, args.id)
    elif args.command == 'purge':
        delete_mission(vault, args.id)
    elif args.command == 'status':
        show_status(vault)

if __name__ == "__main__":
    main()
