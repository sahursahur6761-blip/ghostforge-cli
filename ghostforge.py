#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
from datetime import datetime

# --- Constants ---
VAULT_FILE = 'vault.json'
VERSION = "1.0.0"

# --- ASCII Art & Aesthetic ---
BANNER = r"""
  ________.__                      __   ___________
 /  _____/|  |__   ____  _______ _/  |_ \_   _____/___________  ____   ____
/   \  ___|  |  \ /  _ \/  ___/ \   __\ |    __) \_  __ \_  __ \/  _ \ /  _ \
\    \_\  \   Y  (  <_> )___ \   |  |   |     \   |  | \/|  | \(  <_> |  <_> )
 \______  /___|  /\____/____  >  |__|   \___  /   |__|   |__|   \____/ \____/
        \/     \/           \/              \/
                                 CLI v""" + VERSION + """
"""

# --- Core Logic ---

def load_vault():
    if not os.path.exists(VAULT_FILE):
        default_vault = {
            "player": {
                "level": 1,
                "xp": 0,
                "gold": 0,
                "class": "Novice"
            },
            "missions": [],
            "bosses": [],
            "history": []
        }
        save_vault(default_vault)
        return default_vault

    try:
        with open(VAULT_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Error: Could not read Vault. It may be corrupted.")
        sys.exit(1)

def save_vault(data):
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"Error saving Vault: {e}")

def get_xp_for_level(level):
    return level * 100

def add_xp(vault, amount):
    vault['player']['xp'] += amount
    xp_needed = get_xp_for_level(vault['player']['level'])

    while vault['player']['xp'] >= xp_needed:
        vault['player']['xp'] -= xp_needed
        vault['player']['level'] += 1
        xp_needed = get_xp_for_level(vault['player']['level'])
        print(f"\n[!] LEVEL UP! You are now level {vault['player']['level']}!")

# --- Commands ---

def cmd_vault(args, vault):
    p = vault['player']
    print(BANNER)
    print(f"--- [ THE VAULT ] ---")
    print(f"Level:  {p['level']}")
    print(f"XP:     {p['xp']} / {get_xp_for_level(p['level'])}")
    print(f"Gold:   {p['gold']}")
    print(f"Class:  {p['class']}")
    print(f"---------------------")
    print(f"Missions Active: {len([m for m in vault['missions'] if not m['completed']])}")
    print(f"Bosses Slain:    {len([b for b in vault['bosses'] if b['defeated']])}")

def cmd_mission(args, vault):
    if args.action == 'list':
        if not vault['missions']:
            print("No missions in the log.")
        for i, m in enumerate(vault['missions']):
            status = "[X]" if m['completed'] else "[ ]"
            print(f"{i}: {status} {m['title']} ({m['reward']} XP)")

    elif args.action == 'add':
        new_mission = {
            "title": args.title,
            "reward": args.reward or 10,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }
        vault['missions'].append(new_mission)
        save_vault(vault)
        print(f"Mission added: {args.title}")

    elif args.action == 'complete':
        try:
            idx = int(args.id)
            if 0 <= idx < len(vault['missions']):
                if not vault['missions'][idx]['completed']:
                    vault['missions'][idx]['completed'] = True
                    xp = vault['missions'][idx]['reward']
                    print(f"Mission complete! Gained {xp} XP.")
                    add_xp(vault, xp)
                    save_vault(vault)
                else:
                    print("Mission already completed.")
            else:
                print("Invalid mission ID.")
        except ValueError:
            print("ID must be a number.")

def cmd_boss(args, vault):
    if args.action == 'list':
        if not vault['bosses']:
            print("No bosses encountered yet.")
        for i, b in enumerate(vault['bosses']):
            status = "[SLAYN]" if b['defeated'] else "[ALIVE]"
            print(f"{i}: {status} {b['name']} - {b['description']}")

    elif args.action == 'spawn':
        new_boss = {
            "name": args.name,
            "description": args.description or "A formidable challenge.",
            "reward": args.reward or 100,
            "defeated": False
        }
        vault['bosses'].append(new_boss)
        save_vault(vault)
        print(f"A new boss has appeared: {args.name}!")

    elif args.action == 'slay':
        try:
            idx = int(args.id)
            if 0 <= idx < len(vault['bosses']):
                if not vault['bosses'][idx]['defeated']:
                    vault['bosses'][idx]['defeated'] = True
                    xp = vault['bosses'][idx]['reward']
                    print(f"VICTORY! The boss {vault['bosses'][idx]['name']} has been defeated!")
                    print(f"Gained {xp} XP.")
                    add_xp(vault, xp)
                    save_vault(vault)
                else:
                    print("Boss is already dead.")
            else:
                print("Invalid boss ID.")
        except ValueError:
            print("ID must be a number.")

def main():
    parser = argparse.ArgumentParser(description="GhostForge CLI - Offline Project Manager & RPG")
    subparsers = parser.add_subparsers(dest='command')

    # Vault Command
    subparsers.add_parser('vault', help='View player stats and progress')

    # Mission Command
    m_parser = subparsers.add_parser('mission', help='Manage missions (tasks)')
    m_sub = m_parser.add_subparsers(dest='action')
    m_sub.add_parser('list', help='List all missions')
    m_add = m_sub.add_parser('add', help='Add a new mission')
    m_add.add_argument('title', help='Mission title')
    m_add.add_argument('--reward', type=int, help='XP reward')
    m_comp = m_sub.add_parser('complete', help='Mark a mission as complete')
    m_comp.add_argument('id', help='Mission ID')

    # Boss Command
    b_parser = subparsers.add_parser('boss', help='Manage bosses (milestones)')
    b_sub = b_parser.add_subparsers(dest='action')
    b_sub.add_parser('list', help='List all bosses')
    b_spawn = b_sub.add_parser('spawn', help='Spawn a new boss')
    b_spawn.add_argument('name', help='Boss name')
    b_spawn.add_argument('--description', help='Boss description')
    b_spawn.add_argument('--reward', type=int, help='XP reward')
    b_slay = b_sub.add_parser('slay', help='Defeat a boss')
    b_slay.add_argument('id', help='Boss ID')

    args = parser.parse_args()
    vault = load_vault()

    if args.command == 'vault':
        cmd_vault(args, vault)
    elif args.command == 'mission':
        cmd_mission(args, vault)
    elif args.command == 'boss':
        cmd_boss(args, vault)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
