#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
import shlex
import random
from datetime import datetime, timedelta

# Try to import readline for better interactive experience
try:
    import readline
except ImportError:
    readline = None

# --- Constants ---
VAULT_FILE = 'vault.json'
VERSION = "4.0.0"

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
        "banner": "🔥🔥🔥🔥🔥",
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
{C_RESET}{s}{C_DIM}        ⚡  T H E   C A M P A I G N   U P D A T E   v{VERSION}  ⚡
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

def animate_victory():
    frames = ["  ( •_•)>⌐■-■  ", "  (⌐■_■)  ", "  ( •_•)>⌐■-■  ", "  (⌐■_■) VICTORY! "]
    for _ in range(2):
        for frame in frames:
            sys.stdout.write("\r" + frame)
            sys.stdout.flush()
            time.sleep(0.3)
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
                "buffs": {}, # {effect_name: missions_left}
                "theme": "Cyberpunk"
            },
            "campaigns": {
                "Default": {"missions": [], "bosses": []}
            },
            "active_campaign": "Default",
            "history": [],
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
            p = v['player']
            # Migration/Defaults for v4
            if 'campaigns' not in v:
                v['campaigns'] = {"Default": {"missions": v.get('missions', []), "bosses": v.get('bosses', [])}}
                v['active_campaign'] = "Default"
                if 'missions' in v: del v['missions']
                if 'bosses' in v: del v['bosses']
            if 'buffs' not in p: p['buffs'] = {}
            if 'theme' not in p: p['theme'] = "Cyberpunk"
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
    # Efficiency Skill: +5% XP per rank
    bonus = int(amount * (p['skills'].get('efficiency', 0) * 0.05))
    # Buff: Coffee of Focus (+20% XP)
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
        slow_print(f"\n\033[33m\033[1m🌟 LEVEL UP! You are now Level {p['level']}!\033[0m", 0.03)

def log_history(vault, message):
    vault['history'].append({
        "timestamp": datetime.now().isoformat(),
        "event": message
    })

# --- Features ---

def cmd_vault(vault):
    p = vault['player']
    t = THEMES.get(p['theme'], THEMES["Cyberpunk"])
    prim = t["primary"]
    sec = t["secondary"]
    acc = t["accent"]

    print(get_banner(p['theme']))
    print(f"{C_BOLD}--- PLAYER PROFILE ---{C_RESET}")
    print(f"{prim}Class:{C_RESET}  {p['class']}  {C_DIM}({p['titles'][-1]}){C_RESET}")
    print(f"{prim}Level:{C_RESET}  {p['level']}  {sec}(SP: {p['sp']}){C_RESET}")
    print(f"{prim}Theme:{C_RESET}  {p['theme']}")

    xp_needed = get_xp_for_level(p['level'])
    percent = int((p['xp'] / xp_needed) * 20) if xp_needed > 0 else 0
    bar = "█" * percent + "░" * (20 - percent)
    print(f"{prim}XP:{C_RESET}     [{sec}{bar}{C_RESET}] {p['xp']}/{xp_needed}")

    print(f"{prim}Gold:{C_RESET}   {acc}⟁ {p['gold']}{C_RESET}")

    if p['buffs']:
        buff_str = ", ".join([f"{b}({p['buffs'][b]})" for b in p['buffs'] if p['buffs'][b] > 0])
        if buff_str: print(f"{prim}Buffs:{C_RESET}  {acc}{buff_str}{C_RESET}")

    if p.get('inventory'):
        print(f"{prim}Items:{C_RESET}  {', '.join(p['inventory'])}")
    print(f"{C_BOLD}----------------------{C_RESET}")

    print(f"{C_BOLD}CAMPAIGN:{C_RESET} {acc}{vault['active_campaign']}{C_RESET}")

    # Activity Pulse (simplified heatmap)
    print(f"{C_BOLD}PROJECT PULSE{C_RESET}")
    now = datetime.now()
    heatmap = ""
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        c = len([h for h in vault['history'] if datetime.fromisoformat(h['timestamp']).date() == day])
        char = "░" if c == 0 else "▒" if c < 3 else "▓" if c < 6 else "█"
        heatmap += char
    print(f" {heatmap} {C_DIM}(30d Activity){C_RESET}")

def cmd_theme(vault, theme_name=None):
    if not theme_name:
        print("Available Themes: " + ", ".join(THEMES.keys()))
    elif theme_name in THEMES:
        vault['player']['theme'] = theme_name
        print(f"Theme set to {theme_name}!")
        save_vault(vault)
    else:
        print("Invalid theme.")

def cmd_campaign(vault, action=None, name=None):
    if not action or action == 'list':
        print(f"\n{C_BOLD}--- CAMPAIGNS ---{C_RESET}")
        for c in vault['campaigns']:
            active = "*" if c == vault['active_campaign'] else " "
            missions = len(vault['campaigns'][c]['missions'])
            print(f"{active} {c:<15} ({missions} missions)")
    elif action == 'create':
        if name and name not in vault['campaigns']:
            vault['campaigns'][name] = {"missions": [], "bosses": []}
            print(f"Campaign '{name}' created.")
            save_vault(vault)
        else: print("Invalid name.")
    elif action == 'switch':
        if name in vault['campaigns']:
            vault['active_campaign'] = name
            print(f"Switched to Campaign: {name}")
            save_vault(vault)
        else: print("Campaign not found.")

def cmd_roll(vault, bet):
    p = vault['player']
    if p['gold'] < bet:
        print("Not enough Gold!")
        return
    p['gold'] -= bet
    print(f"Rolling the digital dice for {bet} Gold...")
    time.sleep(1)
    roll = random.randint(1, 6)
    print(f"Outcome: {roll}")
    if roll == 6:
        win = bet * 5
        p['gold'] += win
        print(f"JACKPOT! Won {win} Gold!")
    elif roll >= 4:
        win = bet * 2
        p['gold'] += win
        print(f"Win! Gained {win} Gold.")
    else:
        print("Loss. Better luck next time.")
    save_vault(vault)

def cmd_use(vault, item_name):
    p = vault['player']
    if item_name in p['inventory']:
        item_data = next((i for i in vault['shop'] if i['name'] == item_name), None)
        if item_data:
            if item_data['effect'] == 'WISDOM':
                add_xp(vault, 20)
                p['inventory'].remove(item_name)
                print(f"Used {item_name}. Gained 20 XP.")
            elif 'duration' in item_data:
                p['buffs'][item_data['effect']] = item_data['duration']
                p['inventory'].remove(item_name)
                print(f"Activated {item_name}! Buff applied for {item_data['duration']} missions.")
            save_vault(vault)
        else: print("No effect.")
    else: print("Item not found.")

# --- Interactive ---

def interactive_mode(vault):
    print(get_banner(vault['player']['theme']))
    if random.random() < 0.2:
        slow_print(f"\033[35m\033[2m> Encounter: A glitch in the vault whispers your name...\033[0m", 0.03)

    while True:
        try:
            p = vault['player']
            t = THEMES.get(p['theme'], THEMES["Cyberpunk"])
            raw = input(f"{C_BOLD}{t['primary']}forge>{C_RESET} ").strip()
            if not raw: continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()

            if cmd in ['exit', 'quit']: break
            elif cmd == 'vault': cmd_vault(vault)
            elif cmd == 'theme': cmd_theme(vault, parts[1] if len(parts) > 1 else None)
            elif cmd == 'campaign':
                action = parts[1] if len(parts) > 1 else 'list'
                name = parts[2] if len(parts) > 2 else None
                cmd_campaign(vault, action, name)
            elif cmd == 'roll':
                bet = int(parts[1]) if len(parts) > 1 else 10
                cmd_roll(vault, bet)
            elif cmd == 'mission':
                sub = parts[1].lower() if len(parts) > 1 else 'list'
                c = vault['campaigns'][vault['active_campaign']]
                if sub == 'list':
                    for i, m in enumerate(c['missions']):
                        s = "✔" if m['completed'] else "✘"
                        print(f"{i}: {s} {m['title']} ({m['reward']} XP)")
                elif sub == 'add':
                    title = parts[2] if len(parts) > 2 else "Unnamed"
                    reward = int(parts[3]) if len(parts) > 3 else 20
                    c['missions'].append({"title": title, "reward": reward, "completed": False})
                    save_vault(vault)
                    print(f"Mission Forge: {title}")
                elif sub == 'complete':
                    mid = int(parts[2]) if len(parts) > 2 else -1
                    if 0 <= mid < len(c['missions']):
                        m = c['missions'][mid]
                        if not m['completed']:
                            m['completed'] = True
                            xp = m['reward']
                            # Greed/Buffs
                            gold = (xp // 2) + int((xp // 2) * (p['skills']['greed'] * 0.1))
                            if p['buffs'].get('GOLD_BOOST', 0) > 0: gold = int(gold * 1.5)

                            print(f"Mission Clear! +{xp} XP, +{gold} Gold.")
                            p['gold'] += gold
                            add_xp(vault, xp)
                            log_history(vault, f"Mission: {m['title']}")

                            # Tick buffs
                            for b in list(p['buffs'].keys()):
                                if p['buffs'][b] > 0:
                                    p['buffs'][b] -= 1
                                    if p['buffs'][b] == 0: print(f"Buff expired: {b}")

                            animate_victory()
                            save_vault(vault)
            elif cmd == 'boss':
                sub = parts[1].lower() if len(parts) > 1 else 'list'
                c = vault['campaigns'][vault['active_campaign']]
                if sub == 'list':
                    for i, b in enumerate(c['bosses']):
                        s = "[DEAD]" if b['defeated'] else "[ALIVE]"
                        print(f"{i}: {s} {b['name']}")
                elif sub == 'spawn':
                    name = parts[2] if len(parts) > 2 else "Unknown"
                    c['bosses'].append({"name": name, "defeated": False, "reward": 200})
                    print(f"BOSS SPAWN: {name}")
                    if name in BOSS_PORTRAITS: print(BOSS_PORTRAITS[name])
                    save_vault(vault)
                elif sub == 'slay':
                    bid = int(parts[2]) if len(parts) > 2 else -1
                    if 0 <= bid < len(c['bosses']):
                        b = c['bosses'][bid]
                        if not b['defeated']:
                            b['defeated'] = True
                            p['gold'] += 100
                            add_xp(vault, b['reward'])
                            log_history(vault, f"Slew: {b['name']}")
                            print(f"VICTORY. {b['name']} defeated.")
                            save_vault(vault)
            elif cmd == 'shop':
                if len(parts) > 2 and parts[1] == 'buy':
                    idx = int(parts[2])
                    item = vault['shop'][idx]
                    if p['gold'] >= item['price']:
                        p['gold'] -= item['price']
                        p['inventory'].append(item['name'])
                        print(f"Bought {item['name']}!")
                        save_vault(vault)
                    else: print("Gold needed.")
                else:
                    for i, item in enumerate(vault['shop']):
                        print(f"{i}: {item['name']} ({item['price']} Gold) - {item['desc']}")
            elif cmd == 'use':
                if len(parts) > 1: cmd_use(vault, parts[1])
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            elif cmd == 'help':
                print("Vault: vault | theme <name> | campaign <action> <name>")
                print("Gameplay: mission <list|add|complete> | boss <list|spawn|slay> | use <item>")
                print("Minigames: roll <bet>")
                print("Economy: shop [buy <id>]")
                print("System: clear | help | exit")
        except (EOFError, KeyboardInterrupt): break
        except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="GhostForge v4.0 - The Campaign Update")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('subcommand', nargs='*', default=[])
    args = parser.parse_args()

    vault = load_vault()

    if args.command == 'vault': cmd_vault(vault)
    else: interactive_mode(vault)

if __name__ == "__main__":
    main()
