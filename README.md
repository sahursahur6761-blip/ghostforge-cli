# GhostForge CLI v9.0: The Nexus Bridge 🌌🛰️

GhostForge is the ultimate offline terminal-based RPG project manager for software engineers. Forge your projects, automate your workflow, and conquer the codebase.

## ⚔️ New in v9.0: The Nexus
- **Drone Companions**: Equippable drones like the *Viper* (+ATK) or *Mender* (+HP regen) provide powerful passive buffs.
- **Manual Stat Allocation**: Use your **Skill Points (SP)** to manually increase ATK, DEF, and HACKING stats.
- **Combat Hacking**: During boss fights, use the `Hack` command to deal high damage based on your Hacking stat.
- **Improved HUD**: A high-density dashboard showing all core stats, active drones, and campaign progress.

## 🚀 How to Download & Install

To install GhostForge globally on your system:

1. **Download the source**:
   Clone this repository or download `ghostforge.py` and `install.sh`.

2. **Run the Installer**:
```bash
chmod +x install.sh
./install.sh
```

3. **Verify**:
   Type `ghostforge s` from anywhere.

## 🕹️ Nexus Field Manual

### 1. The Interactive Shell
Simply run `ghostforge` to enter the **Nexus Bridge**.

- `status` (or `s`): View your core HUD.
- `upgrade <stat>`: Spend 1 SP to increase `atk`, `def`, or `hack`.
- `mission add "Task"`: Create a new project quest.
- `mission complete <id>`: Finish a task and gain XP, Gold, and potential Drone repairs.
- `boss fight <id>`: Enter the Nexus Arena. Use `Hack` for critical logic damage.
- `shop buy <id>`: Purchase advanced weaponry or **Drones**.

### 2. Drone Mechanics
Drones are equippable companions that sit in your `DRONE` slot.
- **Viper Drone**: Increases your base damage in all combat encounters.
- **Mender Drone**: Repairs 5 HP automatically after every successful mission completion.

---
**Strictly Offline. Zero Dependencies. Legendary Productivity.**
