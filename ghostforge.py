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
VERSION = "10.0.0"

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

# --- UI Engine ---

def draw_box(title, lines, width=60):
    print(f"{C_CYAN}┌── {C_BOLD}{title}{C_RESET}{C_CYAN} {'─' * (width - len(title) - 5)}┐{C_RESET}")
    for line in lines:
        content = line.ljust(width - 2)
        print(f"{C_CYAN}│{C_RESET} {content} {C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└{'─' * (width - 2)}┘{C_RESET}")

# --- Core Engine ---

class Forge:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or VAULT_FILE
        self.vault = self.load_vault()
        self.p = self.vault['player']
        self.theme = self.p.get('theme', 'Cyberpunk')
        self.save() # Ensure vault exists
        self.auto_backup()

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return self.get_default_vault()
        try:
            with open(self.vault_path, 'r') as f:
                return self.migrate_vault(json.load(f))
        except (json.JSONDecodeError, IOError):
            print(f"{C_RED}ERROR: Vault collapse. Re-initializing...{C_RESET}")
            return self.get_default_vault()

    def get_default_vault(self):
        return {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0, "scrap": 0,
                "hp": 100, "max_hp": 100, "atk": 10, "def": 5, "hack": 10,
                "class": "Novice", "inventory": [], "drone": None,
                "skills": {"speed": 0, "power": 0}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "last_backup": None,
            "drones": {
                "Scout": {"cost": 100, "description": "+5 Hacking"},
                "Striker": {"cost": 250, "description": "+10 Attack"}
            }
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('scrap', 0)
        p.setdefault('hack', 10)
        v.setdefault('drones', self.get_default_vault()['drones'])
        return v

    def save(self):
        temp_path = self.vault_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.vault, f, indent=4)
            os.replace(temp_path, self.vault_path)
        except IOError as e: print(f"Write error: {e}")

    def auto_backup(self):
        now = datetime.now()
        last = self.vault.get('last_backup')
        if not last or (now - datetime.fromisoformat(last)).days >= 1:
            if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
            bp = os.path.join(BACKUP_DIR, f"vault_{now.strftime('%Y%m%d')}.json")
            if os.path.exists(self.vault_path):
                shutil.copy2(self.vault_path, bp)
                self.vault['last_backup'] = now.isoformat()
                self.save()

    # --- Gameplay ---

    def add_xp(self, amount):
        self.p['xp'] += amount
        while self.p['xp'] >= self.p['level'] * 100:
            self.p['xp'] -= self.p['level'] * 100
            self.p['level'] += 1
            self.p['sp'] += 2
            self.p['max_hp'] += 20
            self.p['hp'] = self.p['max_hp']
            print(f"{C_YELLOW}{C_BOLD}>>> SINGULARITY ASCENSION: LEVEL {self.p['level']} <<<{C_RESET}")

    def cmd_status(self):
        p = self.p
        stats = [
            f"{C_CYAN}LVL {p['level']}{C_RESET} | {C_GREEN}HP {p['hp']}/{p['max_hp']}{C_RESET} | {C_YELLOW}⟁ {p['gold']}{C_RESET} | {C_MAGENTA}⚙ {p['scrap']}{C_RESET}",
            f"{C_DIM}ATK:{p['atk']} DEF:{p['def']} HACK:{p['hack']}{C_RESET} | {C_BLUE}DRONE:{str(p['drone']):<10}{C_RESET}",
            f"{C_DIM}Campaign: {self.vault['active_campaign']}{C_RESET}"
        ]
        draw_box(f"SYSTEM HUD v{VERSION}", stats)

    def cmd_auto_forge(self):
        print(f"{C_BLUE}Scanning git logs...{C_RESET}")
        try:
            output = subprocess.check_output(["git", "log", "-n", "3", "--oneline"], stderr=subprocess.STDOUT).decode()
            lines = output.strip().split("\n")
            if lines:
                print(f"{C_YELLOW}Git activity detected. Suggestions for missions:{C_RESET}")
                for line in lines:
                    print(f" - Suggestion: {line.split(' ', 1)[1]}")
            else: print("No recent commits found.")
        except: print("Not a git repository or git not found.")

    def cmd_combat(self, boss_idx):
        c = self.vault['campaigns'][self.vault['active_campaign']]
        try: boss = c['bosses'][int(boss_idx)]
        except: print("Boss ID invalid."); return

        b_hp = 200 + (self.p['level'] * 20)
        print(f"\n{C_RED}!!! COMBAT ENGAGED: {boss['name']} !!!{C_RESET}")

        while b_hp > 0 and self.p['hp'] > 0:
            print(f"{C_CYAN}YOU: {self.p['hp']} HP{C_RESET} | {C_RED}BOSS: {b_hp} HP{C_RESET}")
            move = input(f"{C_BOLD}(S)trike | (H)ack | (D)efend: {C_RESET}").lower()

            if move == 'h' and random.randint(1, 100) < (self.p['hack'] * 5):
                dmg = self.p['hack'] * 3
                b_hp -= dmg
                print(f"{C_CYAN}SYSTEM BYPASS! {dmg} logical damage.{C_RESET}")
                continue

            dmg = self.p['atk'] + (10 if move == 's' else 0)
            b_hp -= dmg
            print(f"You deal {dmg} damage.")

            if b_hp > 0:
                boss_dmg = max(0, 20 - (self.p['def'] if move == 'd' else 0))
                self.p['hp'] -= boss_dmg
                print(f"Boss counters for {boss_dmg} damage.")

        if self.p['hp'] > 0:
            boss['defeated'] = True
            self.p['scrap'] += 50
            self.add_xp(500)
            print(f"{C_GREEN}BOSS DEFEATED. +50 Scrap, +500 XP.{C_RESET}")
        else:
            self.p['hp'] = self.p['max_hp'] // 2
            print(f"{C_RED}SYSTEM SHUTDOWN. Re-initializing at 50% HP.{C_RESET}")
        self.save()

    def cmd_fabricate(self, drone_type=None):
        if not drone_type:
            print(f"\n{C_BOLD}--- FABRICATION LAB ---{C_RESET} (Scrap: {self.p['scrap']})")
            for name, data in self.vault['drones'].items():
                print(f" - {C_CYAN}{name}{C_RESET}: {data['cost']} Scrap | {data['description']}")
            return

        if drone_type in self.vault['drones']:
            cost = self.vault['drones'][drone_type]['cost']
            if self.p['scrap'] >= cost:
                self.p['scrap'] -= cost
                self.p['drone'] = drone_type
                if drone_type == 'Scout': self.p['hack'] += 5
                elif drone_type == 'Striker': self.p['atk'] += 10
                print(f"{C_GREEN}Drone {drone_type} fabricated and deployed.{C_RESET}")
                self.save()
            else: print("Insufficient scrap.")

    def interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"{C_CYAN}{C_BOLD}--- GHOSTFORGE SINGULARITY ENGINE v{VERSION} ---{C_RESET}")
        self.cmd_status()

        while True:
            try:
                raw = input(f"{C_BOLD}{C_GREEN}engine>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()

                if cmd in ['exit', 'quit']: break
                elif cmd in ['status', 's']: self.cmd_status()
                elif cmd == 'autoforge': self.cmd_auto_forge()
                elif cmd == 'mission':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts) > 1 else 'list'
                    if sub == 'list':
                        lines = [f"{i}: [{'X' if m['completed'] else ' '}] {m['title']}" for i, m in enumerate(c['missions'])]
                        draw_box("MISSION LOG", lines)
                    elif sub == 'add':
                        c['missions'].append({"title": parts[2], "completed": False})
                        self.save()
                        print("Mission logged.")
                    elif sub == 'complete':
                        m = c['missions'][int(parts[2])]
                        m['completed'] = True
                        self.add_xp(50)
                        self.p['gold'] += 50
                        self.save()
                elif cmd == 'boss':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts) > 1 else 'list'
                    if sub == 'list':
                        for i, b in enumerate(c['bosses']): print(f"{i}: {'[X]' if b['defeated'] else '[ ]'} {b['name']}")
                    elif sub == 'spawn':
                        c['bosses'].append({"name": parts[2], "defeated": False})
                        self.save()
                    elif sub == 'fight': self.cmd_combat(parts[2])
                elif cmd == 'fabricate':
                    self.cmd_fabricate(parts[1] if len(parts) > 1 else None)
                elif cmd == 'clear': os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd == 'help': print("status, autoforge, mission, boss, fabricate, clear, exit")
            except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description=f"GhostForge Singularity Engine v{VERSION}")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    f = Forge()
    if args.command == 'status' or args.command == 's': f.cmd_status()
    else: f.interactive()

if __name__ == "__main__":
    main()
