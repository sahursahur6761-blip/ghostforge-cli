# GhostForge CLI v7.0: Galactic Forge 🌌⚔️

GhostForge is an insane, offline terminal-based RPG project manager for software engineers who want to conquer their codebase like a galaxy.

## ⚔️ New in v7.0: Galactic Forge
- **Boss Combat System**: Bosses are no longer just milestones—they are encounters. Use `Strike` and `Defend` to defeat them using your gear and stats (HP, ATK, DEF).
- **Equipment System**: Visit the Market to buy **Cyberdecks** and **Icepick Shields** to boost your combat effectiveness.
- **Global Installation**: Install GhostForge once and run it from any directory in your system.
- **Scriptable Missions**: Attach shell commands to your missions; they execute automatically upon completion (e.g., auto-commit, auto-deploy).
- **Galactic Boot Sequence**: High-immersion terminal startup sequence.

## 🚀 Global Installation

To install GhostForge globally on your system:

```bash
chmod +x install.sh
./install.sh
```

Now you can simply type `ghostforge` from any terminal window.

## 🕹️ Master Manual

### 1. The Interactive Forge
Simply run `ghostforge` (or `python3 ghostforge.py`) to enter the persistent command shell.

- `status`: Check your HP, XP, Gold, and active stats.
- `mission add "Task" "Command"`: Create a quest. The optional command runs on completion!
- `mission complete <id>`: Finish the task and trigger the payload.
- `boss spawn "Name"`: Summon a legendary adversary.
- `boss fight <id>`: Enter the turn-based combat arena.
- `shop buy <id>`: Upgrade your hardware.

### 2. Character Progression
- **Leveling**: Increases Max HP and grants Skill Points.
- **Combat Stats**: ATK (Attack) and DEF (Defense) are modified by your equipment.
- **HP Management**: HP is restored upon level up or by certain items.

### 3. Technical Mastery
- **Vault Location**: Your data is now securely stored at `~/.ghostforge_vault.json`.
- **Backups**: Automatically tracked in `~/.ghostforge_backups`.

---
**Zero Dependencies. Maximum Immersion. Forge your Galaxy.**
