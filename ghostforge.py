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
VERSION = "9.0.0"

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
}

# --- Core Engine ---

class Forge:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or VAULT_FILE
        self.vault = self.load_vault()
        self.p = self.vault['player']
        self.theme = THEMES.get(self.p.get('theme', 'Cyberpunk'), THEMES["Cyberpunk"])
        self.auto_backup()

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return self.get_default_vault()
        try:
            with open(self.vault_path, 'r') as f:
                return self.migrate_vault(json.load(f))
        except (json.JSONDecodeError, IOError):
            print(f"{C_RED}Error: Vault corrupted.{C_RESET}")
            sys.exit(1)

    def get_default_vault(self):
        return {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0, "energy": 50, "max_energy": 50,
                "hp": 100, "max_hp": 100, "atk": 10, "def": 5, "hack": 10,
                "class": "Novice", "inventory": [], "drone": None,
                "titles": ["The Unforged"], "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "research": {"automation": 0, "optics": 0, "logic": 0},
                "buffs": {}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "journal": [], "last_backup": None,
            "shop": [
                {"name": "Viper Drone", "price": 500, "type": "DRONE", "desc": "Combat drone. +10 ATK passive."},
                {"name": "Mender Drone", "price": 400, "type": "DRONE", "desc": "Repair drone. Restore 5 HP/mission."},
                {"name": "Cyberdeck+", "price": 300, "type": "WEAPON", "atk": 25, "desc": "Advanced hacking. +25 ATK."},
                {"name": "Stimpack", "price": 50, "type": "USE", "effect": "HEAL", "desc": "Restore 50 HP."}
            ]
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('hack', 10)
        p.setdefault('drone', None)
        v.setdefault('shop', self.get_default_vault()['shop'])
        return v

    def save(self):
        temp_path = self.vault_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.vault, f, indent=4)
            os.replace(temp_path, self.vault_path)
        except IOError as e: print(f"{C_RED}Save Error: {e}{C_RESET}")

    def auto_backup(self):
        now = datetime.now()
        last = self.vault.get('last_backup')
        if not last or (now - datetime.fromisoformat(last)).days >= 1:
            if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
            bp = os.path.join(BACKUP_DIR, f"vault_nexus_{now.strftime('%Y%m%d')}.json")
            if os.path.exists(self.vault_path):
                shutil.copy2(self.vault_path, bp)
                self.vault['last_backup'] = now.isoformat()
                self.save()

    def get_banner(self):
        t = self.theme
        return f"{t['primary']}{C_BOLD}--- GHOSTFORGE NEXUS v{VERSION} ---{C_RESET}"

    # --- Gameplay ---

    def add_xp(self, amount):
        self.p['xp'] += amount
        while self.p['xp'] >= self.p['level'] * 100:
            self.p['xp'] -= self.p['level'] * 100
            self.p['level'] += 1
            self.p['sp'] += 2 # Nexux Upgrade: 2 SP per level
            self.p['max_hp'] += 20
            self.p['hp'] = self.p['max_hp']
            print(f"{C_YELLOW}LEVEL UP! Reached {self.p['level']}. SP +2.{C_RESET}")

    def cmd_status(self):
        p, t = self.p, self.theme
        acc = t["accent"]
        print(f"\n{C_BOLD}┌{'─'*58}┐{C_RESET}")
        print(f"│ {C_CYAN}LVL {p['level']:<2}{C_RESET} | {C_GREEN}HP:{p['hp']}/{p['max_hp']}{C_RESET} | {C_YELLOW}ENG:{p['energy']}{C_RESET} | {C_MAGENTA}⟁ {p['gold']}{C_RESET} | {C_BLUE}DRONE:{str(p['drone']):<10}{C_RESET} │")
        print(f"│ {C_DIM}ATK:{p['atk']:<2} DEF:{p['def']:<2} HACK:{p['hack']:<2}{C_RESET} | {C_DIM}SP:{p['sp']:<2}{C_RESET} | {C_DIM}Campaign:{self.vault['active_campaign']:<15}{C_RESET} │")
        print(f"{C_BOLD}└{'─'*58}┘{C_RESET}")

    def cmd_stat_up(self, stat):
        if self.p['sp'] > 0:
            if stat in ['atk', 'def', 'hack']:
                self.p[stat] += 1
                self.p['sp'] -= 1
                print(f"{C_GREEN}{stat.upper()} upgraded!{C_RESET}")
                self.save()
            else: print("Valid stats: atk, def, hack")
        else: print("No SP available.")

    def cmd_combat(self, boss_idx):
        c = self.vault['campaigns'][self.vault['active_campaign']]
        try: boss = c['bosses'][int(boss_idx)]
        except: print("Boss not found."); return

        b_hp = 150 + (self.p['level'] * 10)
        print(f"\n{C_RED}NEXUS COMBAT: {boss['name']} ({b_hp} HP){C_RESET}")

        while b_hp > 0 and self.p['hp'] > 0:
            move = input(f"{C_BOLD}(S)trike | (H)ack | (D)efend: {C_RESET}").lower()
            if move == 's':
                dmg = self.p['atk'] + (10 if self.p['drone'] == 'Viper Drone' else 0)
                b_hp -= dmg
                print(f"You deal {dmg} damage.")
            elif move == 'h':
                if random.randint(1, 100) < self.p['hack'] * 5:
                    b_hp -= self.p['hack'] * 2
                    print(f"{C_CYAN}SYSTEM GLITCH! Boss stunned & damaged.{C_RESET}")
                    continue
                else: print("Hack failed.")

            # Boss turn
            dmg = max(0, 15 - (self.p['def'] if move == 'd' else 0))
            self.p['hp'] -= dmg
            print(f"Boss deals {dmg} damage. HP: {self.p['hp']}")

        if self.p['hp'] > 0:
            boss['defeated'] = True
            self.add_xp(500)
            self.p['gold'] += 300
            print(f"{C_GREEN}TARGET ELIMINATED.{C_RESET}")
        self.save()

    def cmd_shop(self, action='list', idx=None):
        if action == 'buy' and idx is not None:
            try:
                item = self.vault['shop'][int(idx)]
                if self.p['gold'] >= item['price']:
                    self.p['gold'] -= item['price']
                    if item['type'] == 'DRONE': self.p['drone'] = item['name']
                    elif item['type'] == 'WEAPON': self.p['atk'] += item['atk']
                    else: self.p['inventory'].append(item['name'])
                    print(f"Acquired {item['name']}.")
                    self.save()
                else: print("Gold required.")
            except: print("Error.")
        else:
            for i, item in enumerate(self.vault['shop']):
                print(f"{i}: {item['name']} ({item['price']} ⟁) - {item['desc']}")

    def interactive(self):
        print(self.get_banner())
        self.cmd_status()
        while True:
            try:
                raw = input(f"{C_BOLD}{self.theme['primary']}nexus>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()

                if cmd in ['exit', 'quit']: break
                elif cmd in ['status', 's']: self.cmd_status()
                elif cmd == 'upgrade':
                    if len(parts) > 1: self.cmd_stat_up(parts[1].lower())
                elif cmd == 'mission':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    if parts[1] == 'list':
                        for i, m in enumerate(c['missions']): print(f"{i}: [{'X' if m['completed'] else ' '}] {m['title']}")
                    elif parts[1] == 'add':
                        c['missions'].append({"title": parts[2], "reward": 50, "completed": False})
                        self.save()
                    elif parts[1] == 'complete':
                        m = c['missions'][int(parts[2])]
                        m['completed'] = True
                        self.add_xp(m['reward'])
                        self.p['gold'] += 50
                        if self.p['drone'] == 'Mender Drone': self.p['hp'] = min(self.p['max_hp'], self.p['hp'] + 5)
                        self.save()
                        print("Mission Complete.")
                elif cmd == 'boss':
                    if parts[1] == 'list':
                        for i, b in enumerate(self.vault['campaigns'][self.vault['active_campaign']]['bosses']):
                            print(f"{i}: [{'X' if b['defeated'] else ' '}] {b['name']}")
                    elif parts[1] == 'spawn':
                        self.vault['campaigns'][self.vault['active_campaign']]['bosses'].append({"name": parts[2], "defeated": False})
                        self.save()
                    elif parts[1] == 'fight': self.cmd_combat(parts[2])
                elif cmd == 'shop': self.cmd_shop(parts[1] if len(parts)>1 else 'list', parts[2] if len(parts)>2 else None)
                elif cmd == 'clear': os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd == 'help': print("status, upgrade <atk|def|hack>, mission <list|add|complete>, boss <list|spawn|fight>, shop, exit")
            except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"GhostForge Nexus v{VERSION}")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    f = Forge()
    if args.command == 'status' or args.command == 's': f.cmd_status()
    else: f.interactive()

if __name__ == "__main__":
    main()
