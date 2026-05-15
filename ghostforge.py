#!/usr/bin/env python3
import json
import os
import sys
import argparse
import time
import shlex
import random
import shutil
import subprocess
from datetime import datetime, timedelta

# Optional: readline for better interactive experience
try:
    import readline
except ImportError:
    readline = None

# --- Constants & Configuration ---
VAULT_FILE = os.path.expanduser('~/.ghostforge_vault.json')
BACKUP_DIR = os.path.expanduser('~/.ghostforge_backups')
VERSION = "7.0.2"

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

# --- Theming ---
THEMES = {
    "Cyberpunk": {"primary": C_CYAN, "secondary": C_MAGENTA, "accent": C_YELLOW, "b_char": "▟"},
    "Frost": {"primary": C_BLUE, "secondary": C_WHITE, "accent": C_CYAN, "b_char": "❄"},
    "Hellfire": {"primary": C_RED, "secondary": C_YELLOW, "accent": C_MAGENTA, "b_char": "🔥"},
    "Void": {"primary": "\033[30;1m", "secondary": C_WHITE, "accent": C_MAGENTA, "b_char": "░"}
}

# --- Core Engine ---

class Forge:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or VAULT_FILE
        self.vault = self.load_vault()
        self.p = self.vault['player']
        self.theme = THEMES.get(self.p.get('theme', 'Cyberpunk'), THEMES["Cyberpunk"])

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return self.get_default_vault()
        try:
            with open(self.vault_path, 'r') as f:
                return self.migrate_vault(json.load(f))
        except (json.JSONDecodeError, IOError):
            print(f"{C_RED}Error: Vault data singularity detected. File corrupted.{C_RESET}")
            sys.exit(1)

    def get_default_vault(self):
        return {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0, "shards": 0,
                "hp": 100, "max_hp": 100, "atk": 10, "def": 5,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "research": {"automation": 0, "optics": 0, "logic": 0},
                "buffs": {}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "journal": [],
            "shop": [
                {"name": "Cyberdeck", "price": 200, "type": "WEAPON", "atk": 15, "desc": "A standard hacking tool. +15 ATK."},
                {"name": "Icepick Shield", "price": 150, "type": "ARMOR", "def": 10, "desc": "Counter-intrusion software. +10 DEF."},
                {"name": "Coffee", "price": 50, "type": "BUFF", "effect": "XP_BOOST", "duration": 3, "desc": "+20% XP (3 missions)."},
                {"name": "Rubber Duck", "price": 100, "type": "USE", "effect": "WISDOM", "desc": "Instantly grants 20 XP."}
            ]
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('hp', 100)
        p.setdefault('max_hp', 100)
        p.setdefault('atk', 10)
        p.setdefault('def', 5)
        p.setdefault('shards', 0)
        v.setdefault('campaigns', {"Default": {"missions": [], "bosses": []}})
        v.setdefault('shop', self.get_default_vault()['shop'])
        return v

    def save(self):
        temp_path = self.vault_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.vault, f, indent=4)
            os.replace(temp_path, self.vault_path)
        except IOError as e: print(f"{C_RED}Save Error: {e}{C_RESET}")

    def slow_print(self, text, delay=0.01):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def get_banner(self):
        t = self.theme
        p, s, b = t["primary"], t["secondary"], t["b_char"]
        return rf"""{p}{C_BOLD}
   {b*5}      ▟█   ▟█      {b*5}      ▟███████     {b*5}
  ▟█    █    ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█          ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█  ▟███   ▟██████     ▟█    █     ▟███████    ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
   ▜████▛    ▜█  ▜█      ▜████▛     ▜███████▛    ▜████▛
{C_RESET}{s}{C_DIM}        🌌  T H E   G A L A C T I C   F O R G E   v{VERSION}  🌌
{C_RESET}"""

    # --- Gameplay ---

    def add_xp(self, amount):
        bonus_pct = self.p['skills'].get('efficiency', 0) * 0.05 + self.p['shards'] * 1.0
        total_xp = int(amount * (1 + bonus_pct))
        self.p['xp'] += total_xp
        while self.p['xp'] >= self.p['level'] * 100:
            self.p['xp'] -= self.p['level'] * 100
            self.p['level'] += 1
            self.p['sp'] += 1
            self.p['max_hp'] += 20
            self.p['hp'] = self.p['max_hp']
            self.slow_print(f"\n{C_YELLOW}{C_BOLD}🌟 GALACTIC LEVEL UP! Reached Level {self.p['level']}!{C_RESET}")

    def cmd_status(self):
        p, t = self.p, self.theme
        prim, sec, acc = t["primary"], t["secondary"], t["accent"]
        xp_n = p['level'] * 100
        pct = int((p['xp'] / xp_n) * 20) if xp_n > 0 else 0
        bar = f"{sec}" + "█" * pct + f"{C_RESET}{C_DIM}" + "░" * (20 - pct) + f"{C_RESET}"

        print(f"\n{C_BOLD}--- GALACTIC CORE STATUS ---{C_RESET}")
        print(f"{prim}LVL {p['level']}{C_RESET} | {bar} | {acc}⟁ {p['gold']}{C_RESET}")
        print(f"{prim}HP:{C_RESET} {C_GREEN}{p['hp']}/{p['max_hp']}{C_RESET} | {prim}ATK:{C_RESET} {p['atk']} | {prim}DEF:{C_RESET} {p['def']}")
        print(f"{C_DIM}Campaign:{C_RESET} {acc}{self.vault['active_campaign']}{C_RESET}")

    def matrix_effect(self):
        # A quick visual flourish
        cols = shutil.get_terminal_size().columns
        for _ in range(10):
            line = "".join([random.choice("01") if random.random() > 0.9 else " " for _ in range(cols)])
            print(f"{C_GREEN}{line}{C_RESET}")
            time.sleep(0.05)

    def cmd_combat(self, boss_idx):
        c = self.vault['campaigns'][self.vault['active_campaign']]
        try:
            boss = c['bosses'][int(boss_idx)]
        except: print("Invalid Boss ID."); return

        if boss['defeated']: print("Boss already defeated."); return

        self.matrix_effect()
        b_hp = 100 + (self.p['level'] * 10)
        print(f"\n{C_RED}{C_BOLD}ENCOUNTER: {boss['name']} ({b_hp} HP){C_RESET}")

        while b_hp > 0 and self.p['hp'] > 0:
            print(f"\n{C_CYAN}YOU: {self.p['hp']} HP | {C_RED}BOSS: {b_hp} HP{C_RESET}")
            move = input(f"{C_BOLD}(S)trike or (D)efend? {C_RESET}").lower()
            if move == 's':
                dmg = random.randint(self.p['atk']-5, self.p['atk']+5)
                b_hp -= dmg
                print(f"You strike for {C_RED}{dmg} dmg!{C_RESET}")
            elif move == 'd':
                print("You brace for impact...")
            else:
                print("Stunned by indecision!")

            if b_hp > 0:
                b_dmg = max(0, random.randint(10, 20) - (self.p['def'] if move == 'd' else 0))
                self.p['hp'] -= b_dmg
                print(f"Boss counters for {C_RED}{b_dmg} dmg!{C_RESET}")

        if self.p['hp'] > 0:
            boss['defeated'] = True
            self.p['gold'] += 200
            self.add_xp(500)
            print(f"\n{C_GREEN}{C_BOLD}VICTORY! Slew {boss['name']}. +200 ⟁, +500 XP.{C_RESET}")
        else:
            print(f"\n{C_RED}{C_BOLD}CRITICAL SYSTEM FAILURE. You retreated.{C_RESET}")
            self.p['hp'] = self.p['max_hp'] // 2
        self.save()

    def cmd_shop(self, action='list', idx=None):
        if action == 'buy' and idx is not None:
            try:
                item = self.vault['shop'][int(idx)]
                if self.p['gold'] >= item['price']:
                    self.p['gold'] -= item['price']
                    if item['type'] == 'WEAPON': self.p['atk'] += item['atk']
                    elif item['type'] == 'ARMOR': self.p['def'] += item['def']
                    else: self.p['inventory'].append(item['name'])
                    print(f"Purchased {item['name']}.")
                    self.save()
                else: print("Insufficient gold.")
            except: print("Invalid Item ID.")
        else:
            print(f"\n{C_BOLD}--- GALACTIC MARKET ---{C_RESET}")
            for i, item in enumerate(self.vault['shop']):
                print(f"{i}: {C_CYAN}{item['name']:<15}{C_RESET} ({item['price']:>3} ⟁) - {C_DIM}{item['desc']}{C_RESET}")

    def boot_sequence(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        seq = [
            f"{C_CYAN}GHOSTFORGE BIOS v{VERSION}{C_RESET}",
            "CHECKING MEMORY BANKS... [ OK ]",
            "INITIALIZING NEURAL GRID... [ OK ]",
            "CONNECTING TO GALACTIC FORGE... [ OK ]",
            "SCANNING VAULT SIGNATURE... [ OK ]",
            f"{C_YELLOW}WARNING: UNAUTHORIZED POWER LEVELS DETECTED.{C_RESET}",
            f"{C_BOLD}{C_GREEN}WELCOME TO THE SINGULARITY.{C_RESET}"
        ]
        for line in seq:
            print(line)
            time.sleep(0.05)
        time.sleep(0.3)

    def interactive(self):
        self.boot_sequence()
        print(self.get_banner())
        self.cmd_status()

        while True:
            try:
                raw = input(f"{C_BOLD}{self.theme['primary']}forge>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()
                if cmd in ['exit', 'quit']: break
                elif cmd == 'status': self.cmd_status()
                elif cmd == 'shop': self.cmd_shop(parts[1] if len(parts)>1 else 'list', parts[2] if len(parts)>2 else None)
                elif cmd == 'boss':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts)>1 else 'list'
                    if sub == 'list':
                        for i, b in enumerate(c['bosses']):
                            print(f"{i}: {'[X]' if b['defeated'] else '[ ]'} {b['name']}")
                    elif sub == 'spawn':
                        c['bosses'].append({"name": " ".join(parts[2:]), "defeated": False})
                        self.save()
                        print(f"Boss spawned: {' '.join(parts[2:])}")
                    elif sub == 'fight': self.cmd_combat(parts[2])
                elif cmd == 'mission':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts)>1 else 'list'
                    if sub == 'list':
                        for i, m in enumerate(c['missions']):
                            print(f"{i}: {'[X]' if m['completed'] else '[ ]'} {m['title']}")
                    elif sub == 'add':
                        title = parts[2]
                        script = parts[3] if len(parts) > 3 else None
                        c['missions'].append({"title": title, "reward": 50, "completed": False, "script": script})
                        self.save()
                        print(f"Mission added: {title}")
                    elif sub == 'complete':
                        m = c['missions'][int(parts[2])]
                        if not m['completed']:
                            m['completed'] = True
                            self.add_xp(m['reward'])
                            self.p['gold'] += 25
                            if m.get('script'):
                                print(f"Executing payload: {m['script']}")
                                subprocess.run(m['script'], shell=True)
                            self.save()
                            print("Mission synchronization complete.")
                elif cmd == 'clear': os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd == 'help':
                    print("Commands: status, mission <list|add|complete>, boss <list|spawn|fight>, shop, clear, exit")
            except Exception as e: print(f"Error: {e}")

# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description=f"GhostForge v{VERSION} - Galactic Forge")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    forge = Forge()
    cmd = args.command.lower()
    if cmd == 'forge': forge.interactive()
    elif cmd == 'status': forge.cmd_status()
    elif cmd == 'mission':
        c = forge.vault['campaigns'][forge.vault['active_campaign']]
        if not args.params or args.params[0] == 'list':
            for i, m in enumerate(c['missions']): print(f"{i}: {'[X]' if m['completed'] else '[ ]'} {m['title']}")
        elif args.params[0] == 'add':
            c['missions'].append({"title": args.params[1], "reward": 50, "completed": False})
            forge.save()
            print(f"Mission added: {args.params[1]}")
        elif args.params[0] == 'complete':
            m = c['missions'][int(args.params[1])]
            m['completed'] = True
            forge.add_xp(m['reward'])
            forge.p['gold'] += 25
            forge.save()
            print("Mission complete.")
    else: forge.interactive()

if __name__ == "__main__":
    main()
