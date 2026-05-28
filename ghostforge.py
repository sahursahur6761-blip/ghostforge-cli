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
# Shared board for "Friends" on the same machine (simulated social)
SHARED_LINK = os.path.join('/tmp', '.ghostforge_neural_link.json')
VERSION = "11.0.0"

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

def draw_box(title, lines, width=60, color=C_CYAN):
    print(f"{color}┌── {C_BOLD}{title}{C_RESET}{color} {'─' * (width - len(title) - 5)}┐{C_RESET}")
    for line in lines:
        content = line.ljust(width - 2)
        print(f"{color}│{C_RESET} {content} {color}│{C_RESET}")
    print(f"{color}└{'─' * (width - 2)}┘{C_RESET}")

# --- Core Engine ---

class Forge:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or VAULT_FILE
        self.vault = self.load_vault()
        self.p = self.vault['player']
        self.persona = self.vault.get('persona', random.choice(['Aggressive', 'Cynical', 'Helpful']))
        self.vault['persona'] = self.persona
        self.save()
        self.auto_backup()

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return self.get_default_vault()
        try:
            with open(self.vault_path, 'r') as f:
                return self.migrate_vault(json.load(f))
        except:
            return self.get_default_vault()

    def get_user_name(self):
        try: return os.getlogin()
        except: return os.environ.get('USER', 'Pilot')

    def get_default_vault(self):
        return {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0, "scrap": 0,
                "hp": 100, "max_hp": 100, "atk": 10, "def": 5, "hack": 10,
                "class": "Novice", "inventory": [], "drone": None,
                "name": self.get_user_name()
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "last_backup": None
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('name', self.get_user_name())
        v.setdefault('history', [])
        return v

    def save(self):
        temp_path = self.vault_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.vault, f, indent=4)
            os.replace(temp_path, self.vault_path)
            self.update_neural_link()
        except: pass

    def update_neural_link(self):
        # Update shared machine board
        try:
            data = {}
            if os.path.exists(SHARED_LINK):
                with open(SHARED_LINK, 'r') as f: data = json.load(f)
            data[self.p['name']] = {
                "level": self.p['level'],
                "deed": self.vault['history'][-1]['event'] if self.vault['history'] else "Initializing...",
                "last_seen": datetime.now().strftime("%H:%M")
            }
            with open(SHARED_LINK, 'w') as f: json.dump(data, f)
        except: pass

    def auto_backup(self):
        if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
        shutil.copy2(self.vault_path, os.path.join(BACKUP_DIR, "latest.json"))

    # --- Gameplay ---

    def speak(self, text):
        colors = {'Aggressive': C_RED, 'Cynical': C_MAGENTA, 'Helpful': C_GREEN}
        prefix = f"[{self.persona}]"
        print(f"{colors.get(self.persona, C_WHITE)}{prefix} {text}{C_RESET}")

    def add_xp(self, amount):
        self.p['xp'] += amount
        if self.p['xp'] >= self.p['level'] * 100:
            self.p['level'] += 1
            self.p['max_hp'] += 20
            self.p['hp'] = self.p['max_hp']
            self.speak(f"POWER OVERWHELMING. Level {self.p['level']} reached.")

    def cmd_status(self):
        p = self.p
        hud = [
            f"USER: {p['name']} | LVL {p['level']} | HP {p['hp']}/{p['max_hp']} | ⟁ {p['gold']}",
            f"STATS: ATK {p['atk']} DEF {p['def']} HACK {p['hack']} | SP {p['sp']}",
            f"ACTIVE: {self.vault['active_campaign']} | DRONE: {p['drone']}"
        ]
        draw_box("NEURAL HUD v11.0", hud, color=C_BLUE)

    def cmd_link(self):
        if not os.path.exists(SHARED_LINK):
            print("Neural Link offline. No other users detected.")
            return
        with open(SHARED_LINK, 'r') as f: data = json.load(f)
        lines = [f"{u:<12} | LVL {d['level']:<2} | {d['deed']}" for u, d in data.items()]
        draw_box("NEURAL LINK (LOCAL USERS)", lines, color=C_MAGENTA)

    def interactive(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        self.speak("Neural connection established. Welcome to the Galactic Nexus.")
        self.cmd_status()

        while True:
            try:
                raw = input(f"{C_BOLD}{C_BLUE}nexus>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()

                if cmd in ['exit', 'quit']: break
                elif cmd == 's' or cmd == 'status': self.cmd_status()
                elif cmd == 'link': self.cmd_link()
                elif cmd == 'mission':
                    c = self.vault['campaigns'][self.vault['active_campaign']]
                    if parts[1] == 'list':
                        lines = [f"{i}: [{'X' if m['completed'] else ' '}] {m['title']}" for i, m in enumerate(c['missions'])]
                        draw_box("MISSION LOG", lines)
                    elif parts[1] == 'add':
                        c['missions'].append({"title": parts[2], "completed": False})
                        self.save()
                        self.speak("Mission logged. Don't fail me.")
                    elif parts[1] == 'complete':
                        m = c['missions'][int(parts[2])]
                        m['completed'] = True
                        self.add_xp(50)
                        self.p['gold'] += 50
                        self.vault['history'].append({"event": f"Completed {m['title']}"})
                        self.save()
                        self.speak("Task verified. Currency allocated.")
                elif cmd == 'help': print("status (s), link, mission <list|add|complete>, exit")
                else: self.speak(f"Unknown command '{cmd}'. Try harder.")
            except Exception as e: print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="GhostForge Nexus v11")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()

    f = Forge()
    if args.command == 'status' or args.command == 's': f.cmd_status()
    elif args.command == 'link': f.cmd_link()
    else: f.interactive()

if __name__ == "__main__":
    main()
