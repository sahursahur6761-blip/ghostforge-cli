#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
from datetime import datetime

# --- Constants ---
VAULT_FILE = 'vault.json'
VERSION = "1.1.0"

# --- ANSI Colors ---
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BOLD = "\033[1m"
C_RESET = "\033[0m"

# --- ASCII Art & Aesthetic ---
BANNER = rf"""{C_CYAN}{C_BOLD}
  ________.__                      __   ___________
 /  _____/|  |__   ____  _______ _/  |_ \_   _____/___________  ____   ____
/   \  ___|  |  \ /  _ \/  ___/ \   __\ |    __) \_  __ \_  __ \/  _ \ /  _ \
\    \_\  \   Y  (  <_> )___ \   |  |   |     \   |  | \/|  | \(  <_> |  <_> )
 \______  /___|  /\____/____  >  |__|   \___  /   |__|   |__|   \____/ \____/
        \/     \/           \/              \/
                                 CLI v{VERSION}
{C_RESET}"""

# --- Core Logic ---

def load_vault():
    if not os.path.exists(VAULT_FILE):
        default_vault = {
            "player": {
                "level": 1,
                "xp": 0,
                "gold": 0,
                "class": "Novice",
                "inventory": []
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
        print(f"{C_RED}Error: Could not read Vault. It may be corrupted.{C_RESET}")
        sys.exit(1)

def save_vault(data):
    try:
        with open(VAULT_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"{C_RED}Error saving Vault: {e}{C_RESET}")

def get_xp_for_level(level):
    return level * 100

def add_xp(vault, amount):
    vault['player']['xp'] += amount
    xp_needed = get_xp_for_level(vault['player']['level'])

    while vault['player']['xp'] >= xp_needed:
        vault['player']['xp'] -= xp_needed
        vault['player']['level'] += 1
        xp_needed = get_xp_for_level(vault['player']['level'])
        print(f"\n{C_YELLOW}{C_BOLD}[!] LEVEL UP! You are now level {vault['player']['level']}!{C_RESET}")

        # Level up rewards
        if vault['player']['level'] == 5:
            vault['player']['class'] = "Apprentice Coder"
            print(f"{C_MAGENTA}Promotion: You are now an {vault['player']['class']}!{C_RESET}")

def log_history(vault, message):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "event": message
    }
    vault['history'].append(entry)

# --- Commands ---

def cmd_vault(vault):
    p = vault['player']
    print(BANNER)
    print(f"{C_BOLD}--- [ THE VAULT ] ---{C_RESET}")
    print(f"{C_CYAN}Level:{C_RESET}  {p['level']}")
    print(f"{C_CYAN}XP:{C_RESET}     {p['xp']} / {get_xp_for_level(p['level'])}")
    print(f"{C_CYAN}Gold:{C_RESET}   {p['gold']}")
    print(f"{C_CYAN}Class:{C_RESET}  {p['class']}")
    if p.get('inventory'):
        print(f"{C_CYAN}Items:{C_RESET}  {', '.join(p['inventory'])}")
    print(f"{C_BOLD}---------------------{C_RESET}")
    print(f"Missions Active: {len([m for m in vault['missions'] if not m['completed']])}")
    print(f"Bosses Slain:    {len([b for b in vault['bosses'] if b['defeated']])}")

def cmd_mission_list(vault):
    if not vault['missions']:
        print(f"{C_YELLOW}No missions in the log.{C_RESET}")
        return
    print(f"\n{C_BOLD}--- MISSION LOG ---{C_RESET}")
    for i, m in enumerate(vault['missions']):
        status = f"{C_GREEN}[DONE]{C_RESET}" if m['completed'] else f"{C_RED}[TODO]{C_RESET}"
        print(f"{i}: {status} {m['title']} ({m['reward']} XP)")

def cmd_mission_add(vault, title, reward):
    new_mission = {
        "title": title,
        "reward": reward or 10,
        "completed": False,
        "created_at": datetime.now().isoformat()
    }
    vault['missions'].append(new_mission)
    save_vault(vault)
    print(f"{C_GREEN}Mission added: {title}{C_RESET}")

def cmd_mission_complete(vault, mid):
    try:
        idx = int(mid)
        if 0 <= idx < len(vault['missions']):
            mission = vault['missions'][idx]
            if not mission['completed']:
                mission['completed'] = True
                xp = mission['reward']
                print(f"{C_GREEN}Mission complete! Gained {xp} XP.{C_RESET}")
                add_xp(vault, xp)
                log_history(vault, f"Completed mission: {mission['title']}")
                save_vault(vault)
            else:
                print(f"{C_YELLOW}Mission already completed.{C_RESET}")
        else:
            print(f"{C_RED}Invalid mission ID.{C_RESET}")
    except ValueError:
        print(f"{C_RED}ID must be a number.{C_RESET}")

def cmd_boss_list(vault):
    if not vault['bosses']:
        print(f"{C_YELLOW}No bosses encountered yet.{C_RESET}")
        return
    print(f"\n{C_BOLD}--- BOSS LIST ---{C_RESET}")
    for i, b in enumerate(vault['bosses']):
        status = f"{C_MAGENTA}[SLAYN]{C_RESET}" if b['defeated'] else f"{C_RED}[ALIVE]{C_RESET}"
        print(f"{i}: {status} {b['name']} - {b['description']}")

def cmd_boss_spawn(vault, name, description, reward):
    new_boss = {
        "name": name,
        "description": description or "A formidable challenge.",
        "reward": reward or 100,
        "defeated": False
    }
    vault['bosses'].append(new_boss)
    save_vault(vault)
    print(f"{C_RED}{C_BOLD}A new boss has appeared: {name}!{C_RESET}")

def cmd_boss_slay(vault, bid):
    try:
        idx = int(bid)
        if 0 <= idx < len(vault['bosses']):
            boss = vault['bosses'][idx]
            if not boss['defeated']:
                boss['defeated'] = True
                xp = boss['reward']
                print(f"{C_MAGENTA}{C_BOLD}VICTORY! The boss {boss['name']} has been defeated!{C_RESET}")
                print(f"{C_GREEN}Gained {xp} XP.{C_RESET}")
                add_xp(vault, xp)
                log_history(vault, f"Slew boss: {boss['name']}")

                # Boss Loot
                loot = "Artifact of " + boss['name']
                vault['player'].setdefault('inventory', []).append(loot)
                print(f"{C_YELLOW}Loot found: {loot}{C_RESET}")

                save_vault(vault)
            else:
                print(f"{C_YELLOW}Boss is already dead.{C_RESET}")
        else:
            print(f"{C_RED}Invalid boss ID.{C_RESET}")
    except ValueError:
        print(f"{C_RED}ID must be a number.{C_RESET}")

def interactive_mode(vault):
    print(BANNER)
    print(f"{C_GREEN}Entering Forge Mode... Type 'help' for commands, 'exit' to quit.{C_RESET}")
    while True:
        try:
            line = input(f"{C_BOLD}GhostForge>{C_RESET} ").strip()
            if not line: continue
            parts = line.split()
            cmd = parts[0].lower()

            if cmd == 'exit' or cmd == 'quit':
                break
            elif cmd == 'help':
                print("Commands: vault, mission list, mission add <title> [reward], mission complete <id>,")
                print("          boss list, boss spawn <name> [desc] [reward], boss slay <id>, clear, exit")
            elif cmd == 'vault':
                cmd_vault(vault)
            elif cmd == 'mission':
                if len(parts) < 2:
                    print("Usage: mission list | add <title> [reward] | complete <id>")
                    continue
                sub = parts[1].lower()
                if sub == 'list': cmd_mission_list(vault)
                elif sub == 'add':
                    if len(parts) < 3: print("Missing title")
                    else:
                        title = parts[2]
                        reward = int(parts[3]) if len(parts) > 3 else 10
                        cmd_mission_add(vault, title, reward)
                elif sub == 'complete':
                    if len(parts) < 3: print("Missing ID")
                    else: cmd_mission_complete(vault, parts[2])
            elif cmd == 'boss':
                if len(parts) < 2:
                    print("Usage: boss list | spawn <name> | slay <id>")
                    continue
                sub = parts[1].lower()
                if sub == 'list': cmd_boss_list(vault)
                elif sub == 'spawn':
                    if len(parts) < 3: print("Missing name")
                    else: cmd_boss_spawn(vault, parts[2], "Manual spawn", 100)
                elif sub == 'slay':
                    if len(parts) < 3: print("Missing ID")
                    else: cmd_boss_slay(vault, parts[2])
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                print(f"Unknown command: {cmd}")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting Forge.")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="GhostForge CLI - Offline Project Manager & RPG")
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('vault', help='View player stats and progress')
    subparsers.add_parser('forge', help='Enter interactive mode')

    m_parser = subparsers.add_parser('mission', help='Manage missions')
    m_sub = m_parser.add_subparsers(dest='action')
    m_sub.add_parser('list', help='List all missions')
    m_add = m_sub.add_parser('add', help='Add a new mission')
    m_add.add_argument('title', help='Mission title')
    m_add.add_argument('--reward', type=int, help='XP reward')
    m_comp = m_sub.add_parser('complete', help='Mark a mission as complete')
    m_comp.add_argument('id', help='Mission ID')

    b_parser = subparsers.add_parser('boss', help='Manage bosses')
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

    if not args.command or args.command == 'forge':
        interactive_mode(vault)
    elif args.command == 'vault':
        cmd_vault(vault)
    elif args.command == 'mission':
        if args.action == 'list': cmd_mission_list(vault)
        elif args.action == 'add': cmd_mission_add(vault, args.title, args.reward)
        elif args.action == 'complete': cmd_mission_complete(vault, args.id)
    elif args.command == 'boss':
        if args.action == 'list': cmd_boss_list(vault)
        elif args.action == 'spawn': cmd_boss_spawn(vault, args.name, args.description, args.reward)
        elif args.action == 'slay': cmd_boss_slay(vault, args.id)

if __name__ == "__main__":
    main()
