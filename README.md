# GhostForge CLI

GhostForge CLI is an offline terminal command center that turns any coding folder into a game-like project forge: missions, boss fights, project maps, health reports, XP, vault notes, and exportable dev logs.

## Why it exists
Coding should feel like an adventure. GhostForge transforms your boring tasks and todo lists into an RPG-style experience. Instead of fixing a bug, you complete a mission. Instead of refactoring a huge chunk of code, you fight a Boss. You gain XP, level up, and maintain a local log of your coding journey—all from the comfort of your terminal.

## Free and Open-Source Promise
GhostForge CLI is built with standard Python 3.
- No external dependencies.
- No internet required.
- No API keys.
- No login.
- No ads.
- No tracking.
- No paywalls.
- Free forever.

## How to run it
Make sure you have Python 3 installed. Run the following command in your terminal from your project directory:

```bash
python3 ghostforge.py
```

## Commands
- `help` : Show the help menu.
- `scan` : Scan the current project folder.
- `map` : Show a readable tree of the project map.
- `status` : Generate a local project health report.
- `mission <description>` : Create a normal mission.
- `boss <description>` : Create a harder boss mission.
- `missions` : List all missions.
- `open <mission_id>` : Open a mission for details.
- `plan <mission_id>` : Generate a simulated offline plan.
- `complete <mission_id>` : Complete a mission and gain XP.
- `fail <mission_id>` : Mark a mission as failed.
- `log <mission_id> <note>` : Add a note to a mission.
- `vault add <title> <text>` : Save useful snippets or notes.
- `vault list` : List all vault entries.
- `vault search <keyword>` : Search your vault.
- `export <mission_id>` : Export mission details to a markdown file.
- `profile` : View your rank, XP, and stats.
- `reset-demo` : Reset GhostForge sample data.
- `quit` : Exit the terminal.

## Example Workflow
1. Run `python3 ghostforge.py` to start the forge.
2. Run `scan` to see what kind of project you're working on.
3. Check `status` to see if your project is missing a README or LICENSE.
4. Run `boss Fix memory leak` to create a boss mission.
5. Generate a plan with `plan 1` (assuming ID is 1).
6. Fix the bug in your code.
7. Run `complete 1` to slay the boss and gain XP!
8. View your progress with `profile`.

## Data Files Created
GhostForge keeps all its data locally inside your project folder:
- `ghostforge_data/missions.json`: Stores your active and completed missions.
- `ghostforge_data/profile.json`: Stores your XP, level, and stats.
- `ghostforge_data/vault.json`: Stores your snippets and notes.
- `exports/`: Contains exported mission logs in Markdown format.

## Safety Notes
- GhostForge NEVER reads files outside the current directory.
- It blocks path traversal (e.g., `../`).
- It refuses to open huge files to prevent crashing.
- It will NOT delete your user files.
- It will NOT overwrite exports without creating a safe unique filename.
- The `reset-demo` command only resets GhostForge data, not your project files.

## Roadmap
A future optional version could use Rich or Textual for a more visual terminal UI, but currently, we keep dependencies at zero.
- Rich visual mode
- Textual TUI mode
- Git diff viewer
- Patch preview
- Plugin system
- Local AI model support
- Web dashboard
- Optional donations later
