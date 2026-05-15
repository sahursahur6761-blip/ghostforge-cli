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
VERSION = "8.0.1"

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
                "hp": 100, "max_hp": 100, "atk": 10, "def": 5, "spec": None,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "research": {"automation": 0, "optics": 0, "logic": 0},
                "buffs": {}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "journal": [], "last_backup": None,
            "shop": [
                {"name": "Cyberdeck", "price": 200, "type": "WEAPON", "atk": 15, "desc": "Hacking tool. +15 ATK."},
                {"name": "Shield", "price": 150, "type": "ARMOR", "def": 10, "desc": "Protection. +10 DEF."},
                {"name": "Stimpack", "price": 50, "type": "USE", "effect": "HEAL", "desc": "Restore 50 HP."},
                {"name": "Energy Cell", "price": 75, "type": "USE", "effect": "ENERGY", "desc": "Restore 50 Energy."}
            ]
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('energy', 50)
        p.setdefault('max_energy', 50)
        p.setdefault('spec', None)
        v.setdefault('last_backup', None)
        if 'campaigns' not in v: v['campaigns'] = {"Default": {"missions": [], "bosses": []}}
        if 'active_campaign' not in v: v['active_campaign'] = "Default"
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
            ts = now.strftime("%Y%m%d")
            bp = os.path.join(BACKUP_DIR, f"vault_daily_{ts}.json")
            self.vault['last_backup'] = now.isoformat()
            if os.path.exists(self.vault_path):
                shutil.copy2(self.vault_path, bp)
            self.save()

    def get_banner(self):
        t = self.theme
        b = t["b_char"]
        return rf"""{t['primary']}{C_BOLD}
   ┌────────────────────────────────────────────────────────┐
   │ {b*3}  G H O S T F O R G E   O V E R S E E R   v{VERSION}  {b*3} │
   └────────────────────────────────────────────────────────┘{C_RESET}"""

    # --- Gameplay ---

    def add_xp(self, amount):
        bonus = 1.0 + (self.p['skills'].get('efficiency', 0) * 0.05)
        if self.p['spec'] == 'Netrunner': bonus += 0.20
        total = int(amount * bonus)
        self.p['xp'] += total
        while self.p['xp'] >= self.p['level'] * 100:
            self.p['xp'] -= self.p['level'] * 100
            self.p['level'] += 1
            self.p['max_hp'] += 20
            self.p['hp'] = self.p['max_hp']
            print(f"{C_YELLOW}LEVEL UP! Reached {self.p['level']}.{C_RESET}")
            if self.p['level'] == 10 and not self.p['spec']:
                print(f"{C_MAGENTA}SPECIALIZATION AVAILABLE: Choose Netrunner, Enforcer, or Architect!{C_RESET}")

    def cmd_status(self):
        p, t = self.p, self.theme
        prim, sec, acc = t["primary"], t["secondary"], t["accent"]
        print(f"\n{C_BOLD}┌── CORE PROFILE {'─'*32}┐{C_RESET}")
        print(f"│ {prim}LVL {p['level']:<2}{C_RESET} | {prim}HP:{C_RESET} {p['hp']}/{p['max_hp']} | {prim}ENG:{C_RESET} {p['energy']}/{p['max_energy']} │")
        print(f"│ {prim}SPEC:{C_RESET} {str(p['spec']):<10} | {prim}GOLD:{C_RESET} {acc}⟁ {p['gold']:<5} │")
        print(f"{C_BOLD}└{'─'*49}┘{C_RESET}")

    def hack_minigame(self):
        target = "".join([random.choice("01") for _ in range(8)])
        print(f"{C_CYAN}DECRYPTION PROTOCOL: Match the sequence {C_WHITE}{target}{C_RESET}")
        start = time.time()
        attempt = input("KEY: ").strip()
        if attempt == target and (time.time() - start) < 15:
            print(f"{C_GREEN}SUCCESS. Encryption bypassed.{C_RESET}")
            return True
        print(f"{C_RED}FAILURE. IDS triggered.{C_RESET}")
        return False

    def cmd_combat(self, boss_idx):
        c = self.vault['campaigns'][self.vault['active_campaign']]
        try:
            boss = c['bosses'][int(boss_idx)]
        except: print("Invalid Boss ID."); return

        b_hp = 100 + (self.p['level'] * 15)
        print(f"\n{C_RED}BATTLE: {boss['name']} ({b_hp} HP){C_RESET}")

        while b_hp > 0 and self.p['hp'] > 0:
            print(f"YOU: {self.p['hp']} HP | {self.p['energy']} ENG")
            move = input("(S)trike [0E] | (B)last [20E] | (D)efend [0E]: ").lower()
            if move == 'b' and self.p['energy'] >= 20:
                dmg = self.p['atk'] * 2
                self.p['energy'] -= 20
                b_hp -= dmg
                print(f"Power blast for {C_RED}{dmg} dmg!{C_RESET}")
            elif move == 's':
                dmg = self.p['atk']
                b_hp -= dmg
                print(f"Strike for {dmg} dmg.")
            elif move == 'd':
                print("Bracing...")
            else:
                print("Indecision costs you!")

            if b_hp > 0:
                b_dmg = max(0, 15 - (self.p['def'] if move == 'd' else 0))
                self.p['hp'] -= b_dmg
                print(f"Boss deals {b_dmg} dmg.")

        if self.p['hp'] > 0:
            boss['defeated'] = True
            self.p['gold'] += 200
            self.add_xp(500)
            print(f"{C_GREEN}VICTORY! Slew {boss['name']}.{C_RESET}")
        else:
            print(f"{C_RED}FAILURE. Reprogramming required.{C_RESET}")
            self.p['hp'] = self.p['max_hp'] // 2
        self.save()

    def interactive(self):
        print(self.get_banner())
        self.cmd_status()

        while True:
            try:
                raw = input(f"{C_BOLD}{self.theme['primary']}overseer>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()

                # Aliases
                if cmd == 's': cmd = 'status'
                elif cmd == 'm': cmd = 'mission'
                elif cmd == 'b': cmd = 'boss'

                if cmd in ['exit', 'quit']: break
                elif cmd == 'status': self.cmd_status()
                elif cmd == 'mission':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts) > 1 else 'list'
                    if sub == 'list':
                        for i, m in enumerate(c['missions']):
                            print(f"{i}: [{'X' if m['completed'] else ' '}] {m['title']}")
                    elif sub == 'add':
                        if len(parts) > 2:
                            c['missions'].append({"title": parts[2], "reward": 50, "completed": False})
                            self.save()
                            print("Mission uploaded.")
                        else: print("Missing title.")
                    elif sub == 'complete':
                        if len(parts) > 2:
                            if self.hack_minigame():
                                m = c['missions'][int(parts[2])]
                                if not m['completed']:
                                    m['completed'] = True
                                    self.add_xp(m['reward'])
                                    self.p['gold'] += 50
                                    self.p['energy'] = min(self.p['max_energy'], self.p['energy'] + 10)
                                    self.save()
                        else: print("Missing ID.")
                elif cmd == 'boss':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    sub = parts[1].lower() if len(parts) > 1 else 'list'
                    if sub == 'list':
                        for i, b in enumerate(c['bosses']):
                            print(f"{i}: [{'X' if b['defeated'] else ' '}] {b['name']}")
                    elif sub == 'spawn':
                        if len(parts) > 2:
                            c['bosses'].append({"name": " ".join(parts[2:]), "defeated": False})
                            self.save()
                            print("Boss detected.")
                        else: print("Missing name.")
                    elif sub == 'fight':
                        if len(parts) > 2: self.cmd_combat(parts[2])
                        else: print("Missing ID.")
                elif cmd == 'spec':
                    if len(parts) > 1:
                        if self.p['level'] >= 10 and not self.p['spec']:
                            self.p['spec'] = parts[1]
                            print(f"Path chosen: {parts[1]}")
                            self.save()
                        else: print("Level 10 required or path already chosen.")
                    else: print("Specify: Netrunner, Enforcer, Architect.")
                elif cmd == 'clear': os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd == 'help': print("Commands: status (s), mission (m) <list|add|complete>, boss (b) <list|spawn|fight>, spec <name>, clear, exit")
                else: print(f"Unknown: {cmd}")
            except Exception as e: print(f"System Error: {e}")

# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description=f"GhostForge Overseer v{VERSION}")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    forge = Forge()
    cmd = args.command.lower()

    if cmd in ['status', 's']: forge.cmd_status()
    elif cmd == 'forge': forge.interactive()
    else: forge.interactive()

if __name__ == "__main__":
    main()
