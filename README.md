# GhostForge CLI 🛠️🥷

GhostForge is an offline, RPG-styled project manager and terminal command center. It helps you track your progress, slay milestones (bosses), and complete tasks (missions) to level up your engineering skills.

## Features
- **RPG-Style Progression**: Earn XP, level up, and build your character as you work.
- **Offline & Private**: All data is stored locally in `vault.json`. No internet, no trackers, no BS.
- **Lightweight**: Zero external dependencies. Requires only Python 3.
- **Safety First**: Designed to stay within its own directory and respect your system.

## Quick Start

### 1. "Installation"
Simply download `ghostforge.py` to your project folder. No `pip install` required.

```bash
# Optional: make it executable
chmod +x ghostforge.py
```

### 2. Check your stats
```bash
python3 ghostforge.py vault
```

### 3. Add a Mission (Task)
```bash
python3 ghostforge.py mission add "Fix the login bug" --reward 20
```

### 4. Complete a Mission
```bash
python3 ghostforge.py mission list
python3 ghostforge.py mission complete 0
```

### 5. Spawn and Slay a Boss (Milestone)
```bash
python3 ghostforge.py boss spawn "Release Version 1.0" --reward 200
python3 ghostforge.py boss slay 0
```

## Commands

| Command | Action | Description |
|---------|--------|-------------|
| `vault` | | View your current Level, XP, and stats. |
| `mission` | `list` | See all active and completed missions. |
| `mission` | `add <title>` | Create a new task. |
| `mission` | `complete <id>`| Finish a task and earn XP. |
| `boss` | `list` | See your milestones. |
| `boss` | `spawn <name>` | Create a major project milestone. |
| `boss` | `slay <id>` | Defeat the boss and earn massive XP. |

## Why GhostForge?
Traditional project managers are bloated and boring. GhostForge turns your git commits and bug fixes into a quest.

Stay offline. Stay productive. Keep forging.
