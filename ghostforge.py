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

# Optional: readline for better interactive experience
try:
    import readline
except ImportError:
    readline = None

# --- Constants & Configuration ---
VAULT_FILE = 'vault.json'
BACKUP_DIR = '.forge_backups'
VERSION = "6.0.1"

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

# --- Theming Engine ---
THEMES = {
    "Cyberpunk": {"primary": "\033[36m", "secondary": "\033[35m", "accent": "\033[33m", "banner_char": "▟"},
    "Frost": {"primary": "\033[34m", "secondary": "\033[37m", "accent": "\033[36m", "banner_char": "❄"},
    "Hellfire": {"primary": "\033[31m", "secondary": "\033[33m", "accent": "\033[35m", "banner_char": "🔥"},
    "Void": {"primary": "\033[30;1m", "secondary": "\033[37m", "accent": "\033[35m", "banner_char": "░"}
}

# --- Core Engine ---

class Forge:
    def __init__(self, vault_path=None):
        self.vault_path = vault_path or os.path.join(os.getcwd(), VAULT_FILE)
        self.vault = self.load_vault()
        self.p = self.vault['player']
        self.theme = THEMES.get(self.p.get('theme', 'Cyberpunk'), THEMES["Cyberpunk"])

    def load_vault(self):
        if not os.path.exists(self.vault_path):
            return self.get_default_vault()
        try:
            with open(self.vault_path, 'r') as f:
                v = json.load(f)
                return self.migrate_vault(v)
        except (json.JSONDecodeError, IOError):
            print(f"\033[31mError: Vault data singularity detected. File corrupted.\033[0m")
            sys.exit(1)

    def get_default_vault(self):
        return {
            "player": {
                "level": 1, "xp": 0, "gold": 0, "sp": 0, "shards": 0,
                "class": "Novice", "inventory": [], "titles": ["The Unforged"],
                "skills": {"efficiency": 0, "greed": 0, "luck": 0},
                "research": {"automation": 0, "optics": 0, "logic": 0},
                "buffs": {}, "theme": "Cyberpunk"
            },
            "campaigns": {"Default": {"missions": [], "bosses": []}},
            "active_campaign": "Default",
            "history": [], "journal": [],
            "shop": [
                {"name": "Coffee of Focus", "price": 50, "effect": "XP_BOOST", "duration": 3, "desc": "+20% XP for 3 missions."},
                {"name": "Energy Drink", "price": 80, "effect": "GOLD_BOOST", "duration": 3, "desc": "+50% Gold for 3 missions."},
                {"name": "Rubber Duck", "price": 100, "effect": "WISDOM", "desc": "Instantly grants 20 XP."}
            ]
        }

    def migrate_vault(self, v):
        p = v.setdefault('player', {})
        p.setdefault('shards', 0)
        p.setdefault('research', {"automation": 0, "optics": 0, "logic": 0})
        p.setdefault('buffs', {})
        p.setdefault('sp', 0)
        v.setdefault('journal', [])
        v.setdefault('campaigns', {"Default": {"missions": [], "bosses": []}})
        v.setdefault('active_campaign', "Default")
        v.setdefault('history', [])
        if 'shop' not in v: v['shop'] = self.get_default_vault()['shop']
        return v

    def save(self):
        temp_path = self.vault_path + ".tmp"
        try:
            with open(temp_path, 'w') as f:
                json.dump(self.vault, f, indent=4)
            os.replace(temp_path, self.vault_path)
        except IOError as e:
            print(f"\033[31mError during atomic write: {e}\033[0m")

    # --- Utilities ---

    def slow_print(self, text, delay=0.01):
        for char in text:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        print()

    def get_xp_needed(self, level):
        return level * 100

    def get_banner(self):
        p = self.theme["primary"]
        s = self.theme["secondary"]
        b = self.theme["banner_char"]
        return rf"""{p}{C_BOLD}
   {b*5}      ▟█   ▟█      {b*5}      ▟███████     {b*5}
  ▟█    █    ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█          ▟█  ▟█     ▟█    █     ▟█          ▟█    █
  ▟█  ▟███   ▟██████     ▟█    █     ▟███████    ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
  ▟█    █    ▟█  ▟█     ▟█    █               ▟█ ▟█    █
   ▜████▛    ▜█  ▜█      ▜████▛     ▜███████▛    ▜████▛
{C_RESET}{s}{C_DIM}        🌌  T H E   S I N G U L A R I T Y   U P D A T E   v{VERSION}  🌌
{C_RESET}"""

    # --- Logic ---

    def add_xp(self, amount):
        bonus_pct = self.p['skills'].get('efficiency', 0) * 0.05
        bonus_pct += self.p['research'].get('logic', 0) * 0.10
        if self.p['buffs'].get('XP_BOOST', 0) > 0: bonus_pct += 0.20
        bonus_pct += self.p['shards'] * 1.0

        total_xp = int(amount * (1 + bonus_pct))
        self.p['xp'] += total_xp

        while self.p['xp'] >= self.get_xp_needed(self.p['level']):
            self.p['xp'] -= self.get_xp_needed(self.p['level'])
            self.p['level'] += 1
            self.p['sp'] += 1
            self.slow_print(f"\n\033[33m\033[1m✨ SINGULARITY DETECTED: Level {self.p['level']} reached. SP +1\033[0m")

    def log_event(self, event):
        self.vault['history'].append({"timestamp": datetime.now().isoformat(), "event": event})

    # --- Commands ---

    def cmd_status(self):
        p, t = self.p, self.theme
        prim, sec, acc = t["primary"], t["secondary"], t["accent"]

        xp_n = self.get_xp_needed(p['level'])
        pct = int((p['xp'] / xp_n) * 20) if xp_n > 0 else 0
        bar = f"{sec}" + "█" * pct + f"{C_RESET}{C_DIM}" + "░" * (20 - percent) if 'percent' in locals() else "░" * (20 - pct)
        bar = f"{sec}" + "█" * pct + f"{C_RESET}{C_DIM}" + "░" * (20 - pct) + f"{C_RESET}"

        print(f"\n{C_BOLD}--- FORGE CORE STATUS ---{C_RESET}")
        print(f"{prim}LVL {p['level']}{C_RESET} | {bar} | {acc}⟁ {p['gold']}{C_RESET} | {prim}{p['class']}{C_RESET}")
        print(f"{C_DIM}Shards:{C_RESET} {acc}{p['shards']}{C_RESET} | {C_DIM}SP:{C_RESET} {sec}{p['sp']}{C_RESET} | {C_DIM}Theme:{C_RESET} {p['theme']}")

        active_c = self.vault['active_campaign']
        missions = self.vault['campaigns'][active_c]['missions']
        active_m = [m for m in missions if not m['completed']]
        print(f"{C_DIM}Campaign:{C_RESET} {acc}{active_c}{C_RESET} ({len(active_m)} active missions)")

        now = datetime.now()
        spark = ""
        for i in range(6, -1, -1):
            day = (now - timedelta(days=i)).date()
            c = len([h for h in self.vault['history'] if datetime.fromisoformat(h['timestamp']).date() == day])
            spark += " " if c == 0 else "▂" if c < 2 else "▅" if c < 5 else "█"
        print(f"{C_DIM}Pulse (7d):{C_RESET} {spark}")

    def cmd_mission(self, action='list', params=None):
        params = params or []
        c = self.vault['campaigns'][self.vault['active_campaign']]
        if action == 'list':
            print(f"\n{C_BOLD}--- MISSIONS [{self.vault['active_campaign']}] ---{C_RESET}")
            print(f"{'ID':<3} | {'Status':<6} | {'Prio':<4} | {'Title':<30} | {'Reward'}")
            print("-" * 60)
            for i, m in enumerate(c['missions']):
                s = f"{C_GREEN}✔{C_RESET}" if m['completed'] else f"{C_RED}✘{C_RESET}"
                prio = m.get('priority', 'Med')
                print(f"{i:<3} | {s:<15} | {prio:<4} | {m['title']:<30} | {m['reward']} XP")
        elif action == 'add':
            title = params[0] if len(params) > 0 else "New Quest"
            reward = int(params[1]) if len(params) > 1 else 50
            prio = params[2] if len(params) > 2 else "Med"
            c['missions'].append({"title": title, "reward": reward, "completed": False, "priority": prio})
            self.save()
            print(f"Mission uploaded to the grid: {title}")
        elif action == 'complete':
            idx = int(params[0]) if len(params) > 0 else -1
            if 0 <= idx < len(c['missions']):
                m = c['missions'][idx]
                if not m['completed']:
                    m['completed'] = True
                    xp = m['reward']
                    gold_bonus = int((xp // 2) * (self.p['skills'].get('greed', 0) * 0.1))
                    gold_bonus += int((xp // 2) * (self.p['research'].get('automation', 0) * 0.2))
                    gold = (xp // 2) + gold_bonus
                    if self.p['buffs'].get('GOLD_BOOST', 0) > 0: gold = int(gold * 1.5)
                    self.p['gold'] += gold
                    self.add_xp(xp)
                    self.log_event(f"Completed: {m['title']}")
                    for b in list(self.p['buffs'].keys()):
                        if self.p['buffs'][b] > 0:
                            self.p['buffs'][b] -= 1
                    self.save()
                    print(f"\033[32m✔ DEED COMPLETE. +{xp} XP, +{gold} Gold.\033[0m")
                else: print("Already synchronized.")

    def cmd_research(self, action='list', target=None):
        res = self.p['research']
        costs = {"automation": (res['automation']+1)*200, "optics": (res['optics']+1)*300, "logic": (res['logic']+1)*500}
        if action == 'list' or not action:
            print(f"\n{C_BOLD}--- RESEARCH LAB ---{C_RESET}")
            print(f"1. Automation [Rank {res['automation']}]: +20% Gold per rank. Cost: {costs['automation']} Gold")
            print(f"2. Optics     [Rank {res['optics']}]: +Daily Quest rewards. Cost: {costs['optics']} Gold")
            print(f"3. Logic      [Rank {res['logic']}]: +10% XP per rank. Cost: {costs['logic']} Gold")
            print(f"\nGold: {self.p['gold']} | Use 'research buy <name>'")
        elif action == 'buy' and target in res:
            cost = costs[target]
            if self.p['gold'] >= cost:
                self.p['gold'] -= cost
                res[target] += 1
                self.save()
                print(f"\033[32mResearch Complete: {target.capitalize()} is now Rank {res[target]}.\033[0m")
            else: print("Insufficient currency.")

    def cmd_ascend(self):
        if self.p['level'] < 50:
            print(f"You must reach Level 50 to perceive the Singularity. (Current: {self.p['level']})")
            return
        confirm = input(f"\033[31mWARNING: Ascension will reset your Level, Gold, and Progress for 1 Singularity Shard. Proceed? (y/n): \033[0m").lower()
        if confirm == 'y':
            self.p['shards'] += 1
            self.p['level'] = 1
            self.p['xp'] = 0
            self.p['gold'] = 0
            self.p['sp'] = 0
            self.p['skills'] = {"efficiency": 0, "greed": 0, "luck": 0}
            self.p['research'] = {"automation": 0, "optics": 0, "logic": 0}
            self.vault['campaigns'] = {"Default": {"missions": [], "bosses": []}}
            self.vault['active_campaign'] = "Default"
            self.save()
            self.slow_print("\033[35m\033[1mYOU HAVE ASCENDED. THE GRID IS REBORN.\033[0m", 0.05)

    def cmd_vault(self):
        print(f"\n{C_BOLD}--- THE ARCHIVE ---{C_RESET}")
        print(f"Level: {self.p['level']} | Gold: {self.p['gold']} | Shards: {self.p['shards']}")
        print(f"Research: {self.p['research']}")
        print(f"Inventory: {', '.join(self.p['inventory'])}")

    def cmd_journal(self, action='list', entry=None):
        if not action or action == 'list':
            print(f"\n{C_BOLD}--- DEV JOURNAL ---{C_RESET}")
            for i, e in enumerate(self.vault['journal']):
                print(f"{i}: {C_DIM}[{e['date']}]{C_RESET} {e['text']}")
        elif action == 'add':
            self.vault['journal'].append({"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": entry})
            print("Log recorded.")
            self.save()

    def cmd_theme(self, name=None):
        if name in THEMES:
            self.p['theme'] = name
            self.theme = THEMES[name]
            print(f"Theme set to {name}.")
            self.save()
        else: print(f"Available themes: {', '.join(THEMES.keys())}")

    def cmd_campaign(self, action='list', name=None):
        if action == 'list':
            for c in self.vault['campaigns']: print(f"{'*' if c == self.vault['active_campaign'] else ' '} {c}")
        elif action == 'create' and name:
            self.vault['campaigns'][name] = {"missions": [], "bosses": []}
            self.save()
            print(f"Campaign {name} created.")
        elif action == 'switch' and name in self.vault['campaigns']:
            self.vault['active_campaign'] = name
            self.save()
            print(f"Switched to {name}.")

    def cmd_shop(self, action='list', idx=None):
        if action == 'buy' and idx is not None:
            item = self.vault['shop'][int(idx)]
            if self.p['gold'] >= item['price']:
                self.p['gold'] -= item['price']
                self.p['inventory'].append(item['name'])
                print(f"Obtained {item['name']}.")
                self.save()
            else: print("Insufficient gold.")
        else:
            print(f"\n{C_BOLD}--- BLACK MARKET ---{C_RESET}")
            for i, item in enumerate(self.vault['shop']):
                print(f"{i}: {item['name']} ({item['price']} Gold) - {item['desc']}")

    def cmd_roll(self, bet=10):
        if self.p['gold'] < bet: print("Gold needed."); return
        self.p['gold'] -= bet
        roll = random.randint(1, 10)
        print(f"Roll: {roll}")
        if roll == 10:
            self.p['gold'] += bet*10
            print("JACKPOT!")
        elif roll > 5:
            self.p['gold'] += bet*2
            print("Win!")
        self.save()

    def cmd_backup(self):
        if not os.path.exists(BACKUP_DIR): os.makedirs(BACKUP_DIR)
        backup_path = os.path.join(BACKUP_DIR, f"vault_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        shutil.copy2(self.vault_path, backup_path)
        print(f"Vault archived to {backup_path}")

    def interactive(self):
        print(self.get_banner())
        self.cmd_status()
        if readline:
            commands = ['status', 'mission', 'research', 'ascend', 'vault', 'journal', 'theme', 'campaign', 'shop', 'roll', 'backup', 'clear', 'exit']
            def completer(text, state):
                options = [i for i in commands if i.startswith(text)]
                return options[state] if state < len(options) else None
            readline.set_completer(completer)
            readline.parse_and_bind("tab: complete")
        while True:
            try:
                raw = input(f"{C_BOLD}{self.theme['primary']}forge>{C_RESET} ").strip()
                if not raw: continue
                parts = shlex.split(raw)
                cmd = parts[0].lower()
                if cmd in ['exit', 'quit']: break
                elif cmd == 'status': self.cmd_status()
                elif cmd == 'mission': self.cmd_mission(parts[1] if len(parts)>1 else 'list', parts[2:])
                elif cmd == 'research': self.cmd_research(parts[1] if len(parts)>1 else 'list', parts[2] if len(parts)>2 else None)
                elif cmd == 'ascend': self.cmd_ascend()
                elif cmd == 'vault': self.cmd_vault()
                elif cmd == 'journal': self.cmd_journal(parts[1] if len(parts)>1 else 'list', " ".join(parts[2:]) if len(parts)>2 else None)
                elif cmd == 'theme': self.cmd_theme(parts[1] if len(parts)>1 else None)
                elif cmd == 'campaign': self.cmd_campaign(parts[1] if len(parts)>1 else 'list', parts[2] if len(parts)>2 else None)
                elif cmd == 'shop': self.cmd_shop(parts[1] if len(parts)>1 else 'list', parts[2] if len(parts)>2 else None)
                elif cmd == 'roll': self.cmd_roll(int(parts[1]) if len(parts)>1 else 10)
                elif cmd == 'backup': self.cmd_backup()
                elif cmd == 'clear': os.system('clear' if os.name == 'posix' else 'cls')
                elif cmd == 'help': print(f"Commands: {', '.join(['status', 'mission', 'research', 'ascend', 'vault', 'journal', 'theme', 'campaign', 'shop', 'roll', 'backup', 'clear', 'exit'])}")
                else: print(f"Unrecognized input: {cmd}")
            except (EOFError, KeyboardInterrupt): break
            except Exception as e: print(f"Runtime Error: {e}")

# --- Main Entry ---

def main():
    parser = argparse.ArgumentParser(description=f"GhostForge v{VERSION} - The Singularity")
    parser.add_argument('command', nargs='?', default='forge')
    parser.add_argument('params', nargs='*', default=[])
    args = parser.parse_args()
    forge = Forge()
    cmd = args.command.lower()
    if cmd == 'forge': forge.interactive()
    elif hasattr(forge, f"cmd_{cmd}"):
        method = getattr(forge, f"cmd_{cmd}")
        # Simplistic mapping for CLI
        if cmd == 'mission': method(args.params[0] if args.params else 'list', args.params[1:])
        elif cmd == 'research': method(args.params[0] if args.params else 'list', args.params[1] if len(args.params)>1 else None)
        elif cmd == 'journal': method(args.params[0] if args.params else 'list', " ".join(args.params[1:]) if len(args.params)>1 else None)
        else: method()
    else: forge.interactive()

if __name__ == "__main__":
    main()
