# GhostForge CLI 🛠️🥷

GhostForge is an offline, RPG-styled project manager and terminal command center. It turns your engineering tasks into a quest for glory.

## Features
- **RPG-Style Progression**: Earn XP, level up, and find Artifacts (loot) as you work.
- **Interactive Forge Mode**: Run `ghostforge.py` without arguments to enter a persistent shell.
- **Colorized UI**: High-contrast ANSI colors for a hacker/RPG aesthetic.
- **Offline & Private**: All data is stored locally in `vault.json`. No internet required.
- **Zero Dependencies**: Requires only Python 3 standard library.

## Quick Start

### 1. "Installation"
Simply download `ghostforge.py` to your project folder.

```bash
chmod +x ghostforge.py
./install.sh
```

### 2. Enter the Forge (Interactive Mode)
```bash
python3 ghostforge.py
```
From here you can run commands like `mission add "Fix bug"`, `boss list`, etc.

### 3. CLI Mode
You can also run commands directly:
```bash
python3 ghostforge.py vault
python3 ghostforge.py mission add "Refactor code" --reward 50
```

## Commands (Interactive & CLI)

| Command | Sub-command | Description |
|---------|-------------|-------------|
| `vault` | | View your Level, XP, Class, and Items. |
| `forge` | | Enter the interactive shell. |
| `mission` | `list` | See all active and completed tasks. |
| `mission` | `add <title>` | Create a new task. |
| `mission` | `complete <id>`| Finish a task and earn XP. |
| `boss` | `list` | See your milestones. |
| `boss` | `spawn <name>` | Create a major project milestone. |
| `boss` | `slay <id>` | Defeat the boss and earn XP + Loot! |

## RPG Mechanics
- **Levels**: Each level requires more XP than the last.
- **Promotions**: Reaching certain levels changes your character class.
- **Artifacts**: Defeating bosses grants unique artifacts that appear in your Vault.

Stay offline. Stay productive. Keep forging.
