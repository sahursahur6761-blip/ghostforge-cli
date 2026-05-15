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
VERSION = "3.0.0"

# --- ANSI Colors ---
C_RED = "\033[31m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_BLUE = "\033[34m"
C_MAGENTA = "\033[35m"
C_CYAN = "\033[36m"
C_WHITE = "\033[37m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_RESET = "\033[0m"

# --- ASCII Art & Aesthetic ---
BANNER = rf"""{C_CYAN}{C_BOLD}
   ▟████▙      ▟█   ▟█      ▟████▙      ▟███████     ▟████▙
  ▟█    █    ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█          ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█  ▟███   ▟██████     ▟█    █     ▟███████    ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
   ▜████▛    ▜█  ▜█      ▜████▛     ▜███████▛    ▜████▛
{C_RESET}{C_CYAN}{C_DIM}        ⟁  A S C E N S I O N   U P D A T E   v{VERSION}  ⟁
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
                "level": 1,
                "xp": 0,
                "gold": 0,
                "sp": 0, # Skill Points
                "class": "Novice",
                "inventory": [],
                "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0}
            },
            "missions": [],
            "bosses": [],
            "history": [],
            "daily_quest": None,
            "shop": [
                {"name": "Coffee of Focus", "price": 50, "effect": "XP_BOOST", "desc": "Increases XP gain from missions by 20% for 1 mission."},
                {"name": "Energy Drink", "price": 80, "effect": "GOLD_BOOST", "desc": "Increases Gold gain by 50% for 1 mission."},
                {"name": "Rubber Duck", "price": 100, "effect": "WISDOM", "desc": "Instantly grants 20 XP."}
            ]
        }
        save_vault(default_vault)
        return default_vault

    try:
        with open(path, 'r') as f:
            v = json.load(f)
            # Migration/Defaults for v3
            p = v['player']
            if 'sp' not in p: p['sp'] = max(0, p['level'] - 1)
            if 'skills' not in p: p['skills'] = {"efficiency": 0, "greed": 0, "luck": 0}
            if 'shop' not in v: v['shop'] = [
                {"name": "Coffee of Focus", "price": 50, "effect": "XP_BOOST", "desc": "Increases XP gain."},
                {"name": "Rubber Duck", "price": 100, "effect": "WISDOM", "desc": "Gain 20 XP."}
            ]
            return v
    except (json.JSONDecodeError, IOError):
        print(f"{C_RED}Error: Vault corrupted.{C_RESET}")
        sys.exit(1)

def save_vault(data):
    try:
        with open(get_vault_path(), 'w') as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        print(f"{C_RED}Error saving Vault: {e}{C_RESET}")

def get_xp_for_level(level):
    return level * 100

def add_xp(vault, amount):
    p = vault['player']
    # Efficiency Skill: +5% XP per rank
    bonus = int(amount * (p['skills'].get('efficiency', 0) * 0.05))
    total_xp = amount + bonus

    p['xp'] += total_xp
    xp_needed = get_xp_for_level(p['level'])

    while p['xp'] >= xp_needed:
        p['xp'] -= xp_needed
        p['level'] += 1
        p['sp'] += 1 # Gain 1 SP per level
        xp_needed = get_xp_for_level(p['level'])
        slow_print(f"\n{C_YELLOW}{C_BOLD}🌟 LEVEL UP! You are now Level {p['level']}!{C_RESET}", 0.03)
        slow_print(f"{C_CYAN}✨ Gained 1 Skill Point (SP)!{C_RESET}")

        if p['level'] == 5:
            p['class'] = "Apprentice Coder"
            p['titles'].append("Bug Squasher")
        elif p['level'] == 10:
            p['class'] = "Senior Architect"
            p['titles'].append("Ghost of the Machine")

def log_history(vault, message):
    vault['history'].append({
        "timestamp": datetime.now().isoformat(),
        "event": message
    })

# --- Features ---

def cmd_vault(vault):
    p = vault['player']
    print(BANNER)
    print(f"{C_BOLD}--- PLAYER PROFILE ---{C_RESET}")
    print(f"{C_CYAN}Class:{C_RESET}  {p['class']}  {C_DIM}({p['titles'][-1]}){C_RESET}")
    print(f"{C_CYAN}Level:{C_RESET}  {p['level']}  {C_MAGENTA}(SP: {p['sp']}){C_RESET}")

    # Progress Bar
    xp_needed = get_xp_for_level(p['level'])
    percent = int((p['xp'] / xp_needed) * 20) if xp_needed > 0 else 0
    bar = "█" * percent + "░" * (20 - percent)
    print(f"{C_CYAN}XP:{C_RESET}     [{C_GREEN}{bar}{C_RESET}] {p['xp']}/{xp_needed}")

    print(f"{C_CYAN}Gold:{C_RESET}   {C_YELLOW}⟁ {p['gold']}{C_RESET}")

    # Skills
    s = p['skills']
    print(f"{C_CYAN}Skills:{C_RESET} Efficiency {C_BOLD}{s['efficiency']}{C_RESET} | Greed {C_BOLD}{s['greed']}{C_RESET} | Luck {C_BOLD}{s['luck']}{C_RESET}")

    if p.get('inventory'):
        print(f"{C_CYAN}Items:{C_RESET}  {', '.join(p['inventory'])}")
    print(f"{C_BOLD}----------------------{C_RESET}")

    # Activity Pulse
    print(f"{C_BOLD}PROJECT PULSE{C_RESET}")
    now = datetime.now()
    counts = []
    for i in range(29, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = len([h for h in vault['history'] if datetime.fromisoformat(h['timestamp']).date() == day])
        counts.append(count)

    heatmap = ""
    for i, c in enumerate(counts):
        char = "░"
        if c > 0: char = "▒"
        if c > 2: char = "▓"
        if c > 5: char = "█"
        heatmap += char
        if (i + 1) % 7 == 0: heatmap += " "
    print(f" {heatmap} {C_DIM}(30d Activity){C_RESET}")

def cmd_skills(vault, skill_name=None):
    p = vault['player']
    if not skill_name:
        print(f"\n{C_BOLD}--- SKILL TREE ---{C_RESET} (SP: {p['sp']})")
        print(f"1. {C_CYAN}efficiency{C_RESET}: +5% XP per rank. (Rank: {p['skills']['efficiency']})")
        print(f"2. {C_CYAN}greed{C_RESET}:      +10% Gold per rank. (Rank: {p['skills']['greed']})")
        print(f"3. {C_CYAN}luck{C_RESET}:       +5% chance for double rewards. (Rank: {p['skills']['luck']})")
        print("\nUse 'skills upgrade <name>' to spend 1 SP.")
    elif skill_name in p['skills']:
        if p['sp'] > 0:
            p['sp'] -= 1
            p['skills'][skill_name] += 1
            print(f"{C_GREEN}Upgraded {skill_name.capitalize()} to Rank {p['skills'][skill_name]}!{C_RESET}")
            save_vault(vault)
        else:
            print(f"{C_RED}Not enough SP!{C_RESET}")

def cmd_use(vault, item_name):
    p = vault['player']
    if item_name in p['inventory']:
        item_data = next((i for i in vault['shop'] if i['name'] == item_name), None)
        if item_data:
            if item_data['effect'] == 'WISDOM':
                add_xp(vault, 20)
                p['inventory'].remove(item_name)
                print(f"{C_CYAN}The Rubber Duck listens... and you gain 20 XP.{C_RESET}")
                save_vault(vault)
            else:
                print(f"{C_YELLOW}Item effect '{item_data['effect']}' is passive.{C_RESET}")
        else:
            print(f"{C_RED}Item has no effect.{C_RESET}")
    else:
        print(f"{C_RED}Item not in inventory.{C_RESET}")

def cmd_daily(vault):
    now = datetime.now().date().isoformat()
    if vault.get('daily_quest_date') != now:
        quests = [
            "Complete 3 missions today.",
            "Defeat a boss.",
            "Refactor a messy module.",
            "Write 5 unit tests.",
            "Read a technical blog post."
        ]
        vault['daily_quest'] = random.choice(quests)
        vault['daily_quest_date'] = now
        save_vault(vault)

    print(f"\n{C_YELLOW}📅 DAILY QUEST:{C_RESET} {vault['daily_quest']}")

# --- Interactive ---

def interactive_mode(vault):
    print(BANNER)
    if random.random() < 0.3:
        encounters = [
            "The air is thick with the scent of ozone and stale coffee.",
            "A distant sound of mechanical keyboards echoes through the void.",
            "You feel a sudden urge to refactor everything.",
            "The ghosts of old git branches whisper in the dark."
        ]
        slow_print(f"{C_MAGENTA}{C_DIM}> {random.choice(encounters)}{C_RESET}", 0.03)

    cmd_daily(vault)

    while True:
        try:
            raw = input(f"{C_BOLD}{C_BLUE}forge>{C_RESET} ").strip()
            if not raw: continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()

            if cmd in ['exit', 'quit']: break
            elif cmd == 'help':
                print("Commands: vault, skills [upgrade <name>], use <item>, daily, mission [list|add|complete], boss [list|spawn|slay], shop [buy <id>], clear, exit")
            elif cmd == 'vault': cmd_vault(vault)
            elif cmd == 'skills':
                action = parts[1] if len(parts) > 1 else None
                name = parts[2].lower() if len(parts) > 2 else None
                cmd_skills(vault, name if action == 'upgrade' else None)
            elif cmd == 'use':
                if len(parts) > 1: cmd_use(vault, parts[1])
                else: print("Use what?")
            elif cmd == 'daily': cmd_daily(vault)
            elif cmd == 'mission':
                sub = parts[1].lower() if len(parts) > 1 else 'list'
                if sub == 'list':
                    for i, m in enumerate(vault['missions']):
                        s = f"{C_GREEN}✔{C_RESET}" if m['completed'] else f"{C_RED}✘{C_RESET}"
                        print(f"{i}: {s} {m['title']} ({m['reward']} XP)")
                elif sub == 'add':
                    title = parts[2] if len(parts) > 2 else "Unnamed Mission"
                    reward = int(parts[3]) if len(parts) > 3 else 20
                    vault['missions'].append({"title": title, "reward": reward, "completed": False, "created_at": datetime.now().isoformat()})
                    save_vault(vault)
                    print(f"Mission forged: {title}")
                elif sub == 'complete':
                    mid = int(parts[2]) if len(parts) > 2 else -1
                    if 0 <= mid < len(vault['missions']):
                        m = vault['missions'][mid]
                        if not m['completed']:
                            m['completed'] = True
                            xp = m['reward']
                            gold = (xp // 2) + int((xp // 2) * (vault['player']['skills']['greed'] * 0.1))
                            print(f"{C_GREEN}Mission complete! +{xp} XP, +{gold} Gold.{C_RESET}")
                            vault['player']['gold'] += gold
                            add_xp(vault, xp)
                            log_history(vault, f"Mission: {m['title']}")
                            save_vault(vault)
            elif cmd == 'boss':
                sub = parts[1].lower() if len(parts) > 1 else 'list'
                if sub == 'list':
                    for i, b in enumerate(vault['bosses']):
                        s = f"{C_MAGENTA}[DEAD]{C_RESET}" if b['defeated'] else f"{C_RED}[ALIVE]{C_RESET}"
                        print(f"{i}: {s} {b['name']}")
                elif sub == 'spawn':
                    name = parts[2] if len(parts) > 2 else "Unnamed Terror"
                    vault['bosses'].append({"name": name, "defeated": False, "reward": 200})
                    print(f"{C_RED}WARNING: {name} has appeared!{C_RESET}")
                    if name in BOSS_PORTRAITS: print(C_RED + BOSS_PORTRAITS[name] + C_RESET)
                    save_vault(vault)
                elif sub == 'slay':
                    bid = int(parts[2]) if len(parts) > 2 else -1
                    if 0 <= bid < len(vault['bosses']):
                        b = vault['bosses'][bid]
                        if not b['defeated']:
                            b['defeated'] = True
                            vault['player']['gold'] += 100
                            add_xp(vault, b['reward'])
                            log_history(vault, f"Slew: {b['name']}")
                            print(f"{C_MAGENTA}FATALITY. {b['name']} is no more.{C_RESET}")
                            save_vault(vault)
            elif cmd == 'shop':
                if len(parts) > 2 and parts[1] == 'buy':
                    idx = int(parts[2])
                    item = vault['shop'][idx]
                    if vault['player']['gold'] >= item['price']:
                        vault['player']['gold'] -= item['price']
                        vault['player']['inventory'].append(item['name'])
                        print(f"Bought {item['name']}!")
                        save_vault(vault)
                    else: print("Not enough gold.")
                else:
                    for i, item in enumerate(vault['shop']):
                        print(f"{i}: {item['name']} ({item['price']} Gold) - {item['desc']}")
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                print(f"Unknown command: {cmd}")
        except (EOFError, KeyboardInterrupt): break
        except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="GhostForge v3.0 - Ascension")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('subcommand', nargs='*', default=[])
    args = parser.parse_args()

    vault = load_vault()

    if args.command == 'vault': cmd_vault(vault)
    elif args.command == 'forge': interactive_mode(vault)
    elif args.command == 'mission':
        if not args.subcommand or args.subcommand[0] == 'list':
             for i, m in enumerate(vault['missions']):
                s = "[X]" if m['completed'] else "[ ]"
                print(f"{i}: {s} {m['title']} ({m['reward']} XP)")
        elif args.subcommand[0] == 'add':
            title = args.subcommand[1] if len(args.subcommand) > 1 else "Unnamed Mission"
            reward = int(args.subcommand[2]) if len(args.subcommand) > 2 else 20
            vault['missions'].append({"title": title, "reward": reward, "completed": False, "created_at": datetime.now().isoformat()})
            save_vault(vault)
            print(f"Mission forged: {title}")
        elif args.subcommand[0] == 'complete':
             mid = int(args.subcommand[1]) if len(args.subcommand) > 1 else -1
             if 0 <= mid < len(vault['missions']):
                m = vault['missions'][mid]
                if not m['completed']:
                    m['completed'] = True
                    xp = m['reward']
                    gold = (xp // 2) + int((xp // 2) * (vault['player']['skills']['greed'] * 0.1))
                    print(f"Mission complete! +{xp} XP, +{gold} Gold.")
                    vault['player']['gold'] += gold
                    add_xp(vault, xp)
                    log_history(vault, f"Mission: {m['title']}")
                    save_vault(vault)
    else: interactive_mode(vault)

if __name__ == "__main__":
    main()
