#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
import shlex
from datetime import datetime, timedelta

# Try to import readline for better interactive experience
try:
    import readline
except ImportError:
    readline = None

# --- Constants ---
VAULT_FILE = 'vault.json'
VERSION = "2.0.0"

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
   ▄██████▄   ▄█    █▄   ▄██████▄     ▄████████  ▄██████▄
  ███    ███ ███    ███ ███    ███   ███    ███ ███    ███
  ███    █▀  ███    ███ ███    ███   ███    █▀  ███    ███
 ▄███        ███    ███ ███    ███   ███        ███    ███
▀▀███ ████▄  ███    ███ ███    ███ ▀███████████ ███    ███
  ███    ███ ███    ███ ███    ███          ███ ███    ███
  ███    ███ ███    ███ ███    ███    ▄█    ███ ███    ███
  ████████▀   ▀██████▀   ▀██████▀   ▄████████▀   ▀██████▀
{C_RESET}{C_MAGENTA}{C_BOLD}   Forge your legacy. Master your craft. v{VERSION}
{C_RESET}"""

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
                "class": "Novice",
                "inventory": [],
                "titles": ["The Unforged"]
            },
            "missions": [],
            "bosses": [],
            "history": [],
            "shop": [
                {"name": "Coffee of Focus", "price": 50, "effect": "XP Boost (Minor)"},
                {"name": "Mechanical Keyboard", "price": 500, "effect": "Title: Click-Clack Knight"},
                {"name": "Rubber Duck", "price": 100, "effect": "Wisdom"}
            ]
        }
        save_vault(default_vault)
        return default_vault

    try:
        with open(path, 'r') as f:
            return json.load(f)
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
    vault['player']['xp'] += amount
    xp_needed = get_xp_for_level(vault['player']['level'])

    while vault['player']['xp'] >= xp_needed:
        vault['player']['xp'] -= xp_needed
        vault['player']['level'] += 1
        xp_needed = get_xp_for_level(vault['player']['level'])
        slow_print(f"\n{C_YELLOW}{C_BOLD}[!] LEVEL UP! Reached Level {vault['player']['level']}!{C_RESET}", 0.03)

        if vault['player']['level'] == 5:
            vault['player']['class'] = "Apprentice Coder"
            vault['player']['titles'].append("Bug Squasher")
        elif vault['player']['level'] == 10:
            vault['player']['class'] = "Senior Architect"
            vault['player']['titles'].append("Ghost of the Machine")

def log_history(vault, message):
    vault['history'].append({
        "timestamp": datetime.now().isoformat(),
        "event": message
    })

# --- Features ---

def cmd_vault(vault):
    p = vault['player']
    print(BANNER)
    print(f"{C_BOLD}PLAYER PROFILE{C_RESET}")
    print(f"{C_CYAN}Class:{C_RESET}  {p['class']}  {C_DIM}({p['titles'][-1]}){C_RESET}")
    print(f"{C_CYAN}Level:{C_RESET}  {p['level']}")

    # Progress Bar
    xp_needed = get_xp_for_level(p['level'])
    percent = int((p['xp'] / xp_needed) * 20)
    bar = "█" * percent + "░" * (20 - percent)
    print(f"{C_CYAN}XP:{C_RESET}     [{C_GREEN}{bar}{C_RESET}] {p['xp']}/{xp_needed}")

    print(f"{C_CYAN}Gold:{C_RESET}   {C_YELLOW}⟁ {p['gold']}{C_RESET}")
    if p.get('inventory'):
        print(f"{C_CYAN}Items:{C_RESET}  {', '.join(p['inventory'])}")
    print(f"{C_BOLD}---------------------{C_RESET}")

    # Activity Pulse (last 7 days)
    print(f"{C_BOLD}PROJECT PULSE (Recent Deeds){C_RESET}")
    now = datetime.now()
    counts = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).date()
        count = len([h for h in vault['history'] if datetime.fromisoformat(h['timestamp']).date() == day])
        counts.append(count)

    max_count = max(counts) if counts and max(counts) > 0 else 1
    graph = ""
    for c in counts:
        height = int((c / max_count) * 4)
        chars = [" ", "▃", "▅", "▆", "█"]
        graph += chars[min(height, 4)] + " "
    print(f" {graph}  (Total Actions: {sum(counts)})")

def cmd_shop(vault, action=None, item_idx=None):
    if not action:
        print(f"\n{C_BOLD}--- THE BLACK MARKET SHOP ---{C_RESET}")
        for i, item in enumerate(vault['shop']):
            print(f"{i}: {C_CYAN}{item['name']:<20}{C_RESET} | {C_YELLOW}{item['price']:>4} Gold{C_RESET} | {C_DIM}{item['effect']}{C_RESET}")
        print(f"\nYour Gold: {C_YELLOW}{vault['player']['gold']}{C_RESET}")
        print("Use 'shop buy <id>' to purchase.")
    elif action == 'buy':
        try:
            idx = int(item_idx)
            item = vault['shop'][idx]
            if vault['player']['gold'] >= item['price']:
                vault['player']['gold'] -= item['price']
                vault['player']['inventory'].append(item['name'])
                print(f"{C_GREEN}Purchased {item['name']}!{C_RESET}")
                if "Title:" in item['effect']:
                    new_title = item['effect'].split(": ")[1]
                    vault['player']['titles'].append(new_title)
                    print(f"New title unlocked: {C_BOLD}{new_title}{C_RESET}")
                save_vault(vault)
            else:
                print(f"{C_RED}Insufficient gold!{C_RESET}")
        except:
            print(f"{C_RED}Invalid item ID.{C_RESET}")

def cmd_mission_complete(vault, mid):
    try:
        idx = int(mid)
        if 0 <= idx < len(vault['missions']):
            m = vault['missions'][idx]
            if not m['completed']:
                m['completed'] = True
                xp = m['reward']
                gold = xp // 2
                print(f"{C_GREEN}Mission complete! +{xp} XP, +{gold} Gold.{C_RESET}")
                vault['player']['gold'] += gold
                add_xp(vault, xp)
                log_history(vault, f"Mission: {m['title']}")
                save_vault(vault)
            else:
                print(f"{C_YELLOW}Mission already done.{C_RESET}")
        else:
            print(f"{C_RED}Mission ID not found.{C_RESET}")
    except:
        print(f"{C_RED}ID must be numeric.{C_RESET}")

# --- Interactive ---

def interactive_mode(vault):
    print(BANNER)
    slow_print(f"{C_GREEN}The Forge is hot. Ready for work?{C_RESET}", 0.02)

    # Simple tab completion
    if readline:
        commands = ['vault', 'mission list', 'mission add', 'mission complete', 'boss list', 'boss spawn', 'boss slay', 'shop', 'clear', 'exit']
        def completer(text, state):
            options = [i for i in commands if i.startswith(text)]
            return options[state] if state < len(options) else None
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")

    while True:
        try:
            raw = input(f"{C_BOLD}{C_BLUE}forge>{C_RESET} ").strip()
            if not raw: continue
            parts = shlex.split(raw)
            cmd = parts[0].lower()

            if cmd in ['exit', 'quit']: break
            elif cmd == 'help':
                print("Vault: vault")
                print("Missions: mission list | add <title> [reward] | complete <id>")
                print("Bosses: boss list | spawn <name> | slay <id>")
                print("Economy: shop | shop buy <id>")
                print("System: clear | help | exit")
            elif cmd == 'vault': cmd_vault(vault)
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
                    cmd_mission_complete(vault, parts[2] if len(parts) > 2 else -1)
            elif cmd == 'boss':
                sub = parts[1].lower() if len(parts) > 1 else 'list'
                if sub == 'list':
                    for i, b in enumerate(vault['bosses']):
                        s = f"{C_MAGENTA}[DEAD]{C_RESET}" if b['defeated'] else f"{C_RED}[ALIVE]{C_RESET}"
                        print(f"{i}: {s} {b['name']} - {b['description']}")
                elif sub == 'spawn':
                    name = parts[2] if len(parts) > 2 else "Unknown Terror"
                    vault['bosses'].append({"name": name, "description": "Manual spawn", "reward": 100, "defeated": False})
                    save_vault(vault)
                    slow_print(f"{C_RED}{C_BOLD}⚠️  BOSS SPAWNED: {name}{C_RESET}", 0.05)
                elif sub == 'slay':
                    bid = int(parts[2]) if len(parts) > 2 else -1
                    if 0 <= bid < len(vault['bosses']):
                        b = vault['bosses'][bid]
                        if not b['defeated']:
                            b['defeated'] = True
                            vault['player']['gold'] += 100
                            add_xp(vault, b['reward'])
                            log_history(vault, f"Slew: {b['name']}")
                            loot = f"Relic of {b['name']}"
                            vault['player']['inventory'].append(loot)
                            slow_print(f"{C_MAGENTA}FATALITY. {b['name']} is no more.{C_RESET}", 0.04)
                            save_vault(vault)
            elif cmd == 'shop':
                action = parts[1] if len(parts) > 1 else None
                item = parts[2] if len(parts) > 2 else None
                cmd_shop(vault, action, item)
            elif cmd == 'clear':
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                print(f"Unknown command: {cmd}")
        except (EOFError, KeyboardInterrupt): break
        except Exception as e: print(f"Error: {e}")

# --- CLI Entry ---

def main():
    parser = argparse.ArgumentParser(description="GhostForge v2.0 - The Ultimate Forge")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('subcommand', nargs='*', default=[])
    args = parser.parse_args()

    vault = load_vault()

    if args.command == 'forge':
        interactive_mode(vault)
    elif args.command == 'vault':
        cmd_vault(vault)
    elif args.command == 'mission':
        # Legacy CLI support
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
            cmd_mission_complete(vault, args.subcommand[1])
    else:
        # Just run interactive for anything else
        interactive_mode(vault)

if __name__ == "__main__":
    main()
