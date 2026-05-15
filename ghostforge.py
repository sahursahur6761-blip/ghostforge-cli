#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
import shlex
import random
import shutil
from datetime import datetime, timedelta

# Try to import readline for better interactive experience
try:
    import readline
except ImportError:
    readline = None

# --- Constants ---
VAULT_FILE = 'vault.json'
BACKUP_DIR = '.forge_backups'
VERSION = "5.0.1"

# --- Theming Engine ---
THEMES = {
    "Cyberpunk": {
        "primary": "\033[36m", # Cyan
        "secondary": "\033[35m", # Magenta
        "accent": "\033[33m", # Yellow
        "banner": "▟████▙",
    },
    "Frost": {
        "primary": "\033[34m", # Blue
        "secondary": "\033[37m", # White
        "accent": "\033[36m", # Cyan
        "banner": "❄❄❄❄❄",
    },
    "Hellfire": {
        "primary": "\033[31m", # Red
        "secondary": "\033[33m", # Yellow
        "accent": "\033[35m", # Magenta
        "banner": "🔥🔥🔥🔥█",
    }
}

C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"

# --- ASCII Art & Aesthetic ---
def get_banner(theme_name="Cyberpunk"):
    t = THEMES.get(theme_name, THEMES["Cyberpunk"])
    p = t["primary"]
    s = t["secondary"]
    b = t["banner"]
    return rf"""{p}{C_BOLD}
   {b}      ▟█   ▟█      {b}      ▟███████     {b}
  ▟█    █    ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█          ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█  ▟███   ▟██████     ▟█    █     ▟███████    ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
   ▜████▛    ▜█  ▜█      ▜████▛     ▜███████▛    ▜████▛
{C_RESET}{s}{C_DIM}        🏰  T H E   C I T A D E L   U P D A T E   v{VERSION}  🏰
{C_RESET}"""

BOSS_PORTRAITS = {
    "The Bug King": r"""
      __      __
     (  \_  _/  )
      \   \/   /
  __ /        \ __
 (  (          )  )
  \  \        /  /
   \__\      /__/
    """,
    "Deadline Specter": r"""
      .---.
     /     \
    | () () |
     \  ^  /
      |||||
      |||||
    """
}

# --- Utility ---

def slow_print(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def get_vault_path():
    return os.path.join(os.getcwd(), VAULT_FILE)

# --- Core Logic ---

def load_vault():
    path = get_vault_path()
    if not os.path.exists(path):
        default_vault = {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "buffs": {},
                "theme": "Cyberpunk"
            },
            "campaigns": {
                "Default": {"missions": [], "bosses": []}
            },
            "active_campaign": "Default",
            "history": [],
            "journal": [],
            "daily_quest": None,
            "shop": [
                {"name": "Coffee of Focus", "price": 50, "effect": "XP_BOOST", "duration": 3, "desc": "+20% XP for 3 missions."},
                {"name": "Energy Drink", "price": 80, "effect": "GOLD_BOOST", "duration": 3, "desc": "+50% Gold for 3 missions."},
                {"name": "Rubber Duck", "price": 100, "effect": "WISDOM", "desc": "Instantly grants 20 XP."}
            ]
        }
        save_vault(default_vault)
        return default_vault

    try:
        with open(path, 'r') as f:
            v = json.load(f)
            # Migration
            if 'journal' not in v: v['journal'] = []
            p = v['player']
            if 'buffs' not in p: p['buffs'] = {}
            if 'sp' not in p: p['sp'] = 0
            if 'titles' not in p: p['titles'] = ["The Unforged"]
            return v
    except (json.JSONDecodeError, IOError):
        print(f"\033[31mError: Vault corrupted.\033[0m")
        sys.exit(1)

def save_vault(data):
    try:
        with open(get_vault_path(), 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"\033[31mError saving Vault: {e}\033[0m")

def get_xp_for_level(level):
    return level * 100

def add_xp(vault, amount):
    p = vault['player']
    bonus = int(amount * (p['skills'].get('efficiency', 0) * 0.05))
    if p['buffs'].get('XP_BOOST', 0) > 0:
        bonus += int(amount * 0.20)

    total_xp = amount + bonus
    p['xp'] += total_xp
    xp_needed = get_xp_for_level(p['level'])

    while p['xp'] >= xp_needed:
        p['xp'] -= xp_needed
        p['level'] += 1
        p['sp'] += 1
        xp_needed = get_xp_for_level(p['level'])
        slow_print(f"\n\033[33m\033[1m🌟 CITADEL ADVANCEMENT! Reached Level {p['level']}!\033[0m", 0.03)

def log_history(vault, message):
    vault['history'].append({
        "timestamp": datetime.now().isoformat(),
        "event": message
    })

# --- Shared Command Logic ---

def cmd_status(vault):
    p = vault['player']
    t = THEMES.get(p['theme'], THEMES["Cyberpunk"])
    prim, sec, acc = t["primary"], t["secondary"], t["accent"]

    xp_needed = get_xp_for_level(p['level'])
    percent = int((p['xp'] / xp_needed) * 20) if xp_needed > 0 else 0
    bar = f"{sec}" + "█" * percent + f"{C_RESET}{C_DIM}" + "░" * (20 - percent) + f"{C_RESET}"

    campaign = vault['active_campaign']
    missions = [m for m in vault['campaigns'][campaign]['missions'] if not m['completed']]

    print(f"\n{C_BOLD}--- CITADEL DASHBOARD ---{C_RESET}")
    print(f"{prim}LVL {p['level']}{C_RESET} | {bar} | {acc}⟁ {p['gold']}{C_RESET} | {prim}{p['class']}{C_RESET}")
    print(f"{C_DIM}Campaign:{C_RESET} {acc}{campaign}{C_RESET} | {C_DIM}Missions:{C_RESET} {len(missions)} active")
    if p['buffs']:
        active = [f"{b}({v})" for b,v in p['buffs'].items() if v > 0]
        if active: print(f"{sec}Buffs:{C_RESET} {', '.join(active)}")
    if vault.get('daily_quest'):
        print(f"{C_YELLOW}Daily Quest:{C_RESET} {vault['daily_quest']}")

def cmd_vault(vault):
    p = vault['player']
    print(f"\n{C_BOLD}--- VAULT PROFILE ---{C_RESET}")
    print(f"Level: {p['level']} | XP: {p['xp']} | SP: {p['sp']} | Gold: {p['gold']}")
    print(f"Class: {p['class']} | Titles: {', '.join(p['titles'])}")
    if p['inventory']:
        print(f"Inventory: {', '.join(p['inventory'])}")

def cmd_journal(vault, action=None, entry=None):
    if not action or action == 'list':
        print(f"\n{C_BOLD}--- DEV JOURNAL ---{C_RESET}")
        for i, e in enumerate(vault['journal']):
            print(f"{i}: {C_DIM}[{e['date']}]{C_RESET} {e['text']}")
    elif action == 'add':
        vault['journal'].append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "text": entry
        })
        print("Log recorded.")
        save_vault(vault)
    elif action == 'clear':
        vault['journal'] = []
        print("Journal purged.")
        save_vault(vault)

def cmd_mission(vault, action='list', params=None):
    params = params or []
    p = vault['player']
    c = vault['campaigns'][vault['active_campaign']]
    if action == 'list':
        print(f"\n{C_BOLD}--- MISSIONS ({vault['active_campaign']}) ---{C_RESET}")
        for i, m in enumerate(c['missions']):
            prio = m.get('priority', 'Med')
            s = "✔" if m['completed'] else "✘"
            print(f"{i}: {s} [{prio}] {m['title']} ({m['reward']} XP)")
    elif action == 'add':
        title = params[0] if len(params) > 0 else "Task"
        reward = int(params[1]) if len(params) > 1 else 20
        prio = params[2] if len(params) > 2 else "Med"
        c['missions'].append({"title": title, "reward": reward, "completed": False, "priority": prio})
        save_vault(vault)
        print(f"Mission logged: {title}")
    elif action == 'complete':
        mid = int(params[0]) if len(params) > 0 else -1
        if 0 <= mid < len(c['missions']):
            m = c['missions'][mid]
            if not m['completed']:
                m['completed'] = True
                xp = m['reward']
                # Economy calc
                gold_bonus = int((xp // 2) * (p['skills'].get('greed', 0) * 0.1))
                gold = (xp // 2) + gold_bonus
                if p['buffs'].get('GOLD_BOOST', 0) > 0: gold = int(gold * 1.5)

                print(f"Mission Success! +{xp} XP, +{gold} Gold.")
                p['gold'] += gold
                add_xp(vault, xp)
                log_history(vault, f"Mission: {m['title']}")

                # Tick buffs
                for b in list(p['buffs'].keys()):
                    if p['buffs'][b] > 0:
                        p['buffs'][b] -= 1
                save_vault(vault)
            else:
                print("Mission already completed.")

def cmd_boss(vault, action='list', params=None):
    params = params or []
    p = vault['player']
    c = vault['campaigns'][vault['active_campaign']]
    if action == 'list':
        print(f"\n{C_BOLD}--- BOSSES ({vault['active_campaign']}) ---{C_RESET}")
        for i, b in enumerate(c['bosses']):
            s = "[DEAD]" if b['defeated'] else "[ALIVE]"
            print(f"{i}: {s} {b['name']}")
    elif action == 'spawn':
        name = params[0] if len(params) > 0 else "Unnamed Terror"
        c['bosses'].append({"name": name, "defeated": False, "reward": 200})
        print(f"BOSS SPAWN: {name}")
        if name in BOSS_PORTRAITS: print(BOSS_PORTRAITS[name])
        save_vault(vault)
    elif action == 'slay':
        bid = int(params[0]) if len(params) > 0 else -1
        if 0 <= bid < len(c['bosses']):
            b = c['bosses'][bid]
            if not b['defeated']:
                b['defeated'] = True
                p['gold'] += 100
                add_xp(vault, b['reward'])
                log_history(vault, f"Slew: {b['name']}")
                print(f"VICTORY. {b['name']} defeated.")
                save_vault(vault)

def cmd_backup(vault):
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"vault_{timestamp}.json")
    shutil.copy2(VAULT_FILE, backup_path)
    print(f"Vault archived to {backup_path}")

def cmd_roll(vault, bet):
    p = vault['player']
    if p['gold'] < bet:
        print("Insufficient Gold.")
        return
    p['gold'] -= bet
    print(f"Rolling the dice...")
    time.sleep(0.5)
    roll = random.randint(1, 10)
    if roll == 10:
        win = bet * 10
        p['gold'] += win
        print(f"CRITICAL SUCCESS! +{win} Gold!")
    elif roll > 5:
        win = bet * 2
        p['gold'] += win
        print(f"Success. +{win} Gold.")
    else:
        print("Failure.")
    save_vault(vault)

# --- Interactive ---

def interactive_mode(vault):
    print(get_banner(vault['player']['theme']))
    cmd_status(vault)

    if readline:
        commands = ['vault', 'status', 'mission list', 'mission add', 'mission complete',
                    'boss list', 'boss spawn', 'boss slay', 'shop', 'journal', 'theme',
                    'campaign', 'backup', 'roll', 'clear', 'exit']
        def completer(text, state):
            options = [i for i in commands if i.startswith(text)]
            return options[state] if state < len(options) else None
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    while True:
        try:
            p = vault['player']
            t = THEMES.get(p['theme'], THEMES["Cyberpunk"])
            raw = input(f"{C_BOLD}{t['primary']}forge>{C_RESET} ").strip()
            if not raw: continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()

            if cmd in ['exit', 'quit']: break
            elif cmd == 'help':
                print("Commands: status, vault, journal [add|list], mission, boss, campaign, shop, theme, roll, backup, clear, exit")
            elif cmd == 'status': cmd_status(vault)
            elif cmd == 'vault': cmd_vault(vault)
            elif cmd == 'journal':
                action = parts[1] if len(parts) > 1 else 'list'
                entry = " ".join(parts[2:]) if len(parts) > 2 else None
                cmd_journal(vault, action, entry)
            elif cmd == 'mission':
                cmd_mission(vault, parts[1] if len(parts) > 1 else 'list', parts[2:])
            elif cmd == 'boss':
                cmd_boss(vault, parts[1] if len(parts) > 1 else 'list', parts[2:])
            elif cmd == 'campaign':
                action = parts[1] if len(parts) > 1 else 'list'
                name = parts[2] if len(parts) > 2 else None
                if action == 'list':
                    for c in vault['campaigns']: print(f"{'*' if c == vault['active_campaign'] else ' '} {c}")
                elif action == 'create' and name:
                    vault['campaigns'][name] = {"missions": [], "bosses": []}
                    save_vault(vault)
                elif action == 'switch' and name in vault['campaigns']:
                    vault['active_campaign'] = name
                    save_vault(vault)
            elif cmd == 'shop':
                if len(parts) > 2 and parts[1] == 'buy':
                    idx = int(parts[2])
                    item = vault['shop'][idx]
                    if p['gold'] >= item['price']:
                        p['gold'] -= item['price']
                        p['inventory'].append(item['name'])
                        print(f"Obtained {item['name']}.")
                        save_vault(vault)
                else:
                    for i, item in enumerate(vault['shop']):
                        print(f"{i}: {item['name']} ({item['price']} Gold) - {item['desc']}")
            elif cmd == 'backup': cmd_backup(vault)
            elif cmd == 'roll': cmd_roll(vault, int(parts[1]) if len(parts) > 1 else 10)
            elif cmd == 'theme':
                if len(parts) > 1:
                    vault['player']['theme'] = parts[1]
                    save_vault(vault)
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                print(f"Unknown command: {cmd}")
        except (EOFError, KeyboardInterrupt): break
        except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="GhostForge v5.0 - The Citadel")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    vault = load_vault()
    cmd = args.command.lower()
    params = args.params

    if cmd == 'forge':
        interactive_mode(vault)
    elif cmd == 'status':
        cmd_status(vault)
    elif cmd == 'backup':
        cmd_backup(vault)
    elif cmd == 'vault':
        cmd_vault(vault)
    elif cmd == 'journal':
        action = params[0] if params else 'list'
        entry = " ".join(params[1:]) if len(params) > 1 else None
        cmd_journal(vault, action, entry)
    elif cmd == 'mission':
        cmd_mission(vault, params[0] if params else 'list', params[1:])
    elif cmd == 'boss':
        cmd_boss(vault, params[0] if params else 'list', params[1:])
    elif cmd == 'help':
        parser.print_help()
    else:
        interactive_mode(vault)

if __name__ == "__main__":
    main()
