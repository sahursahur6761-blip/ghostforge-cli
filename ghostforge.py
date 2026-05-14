import os
import sys
import json
import uuid
import datetime
import shutil

# Configuration
DATA_DIR = "ghostforge_data"
EXPORTS_DIR = "exports"
MISSIONS_FILE = os.path.join(DATA_DIR, "missions.json")
PROFILE_FILE = os.path.join(DATA_DIR, "profile.json")
VAULT_FILE = os.path.join(DATA_DIR, "vault.json")

IGNORE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "env",
    "dist", "build", "exports", "ghostforge_data", "target"
}
IGNORE_FILES = {
    ".DS_Store", "Thumbs.db"
}

BANNER = """
   _____ _               _  ______
  / ____| |             | | |  ____|
 | |  __| |__   ___  ___| |_| |__ ___  _ __ __ _  ___
 | | |_ | '_ \\ / _ \\/ __| __|  __/ _ \\| '__/ _` |/ _ \\
 | |__| | | | | (_) \\__ \\ |_| | | (_) | | | (_| |  __/
  \\_____|_| |_|\\___/|___/\\__|_|  \\___/|_|  \\__, |\\___|
                                            __/ |
                                           |___/
      --- The Offline Terminal Command Center ---
"""

def print_colored(text, color_code=""):
    # Fallback to normal text if not supported or just stick to plain text for compatibility
    # But since it should be fun/hacker style, let's use standard ANSI codes.
    # To keep it standard python without dependencies, we print directly.
    reset = "\033[0m"
    if color_code:
        print(f"{color_code}{text}{reset}")
    else:
        print(text)

def success(text): print_colored(f"[+] {text}", "\033[92m")  # Green
def info(text): print_colored(f"[*] {text}", "\033[96m")    # Cyan
def warning(text): print_colored(f"[!] {text}", "\033[93m") # Yellow
def error(text): print_colored(f"[-] {text}", "\033[91m")   # Red

# --- Initialization ---

def init_env():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(EXPORTS_DIR, exist_ok=True)

    if not os.path.exists(PROFILE_FILE):
        save_json(PROFILE_FILE, {
            "username": "Ghost",
            "level": 1,
            "xp": 0,
            "missions_completed": 0,
            "boss_missions_completed": 0,
            "failed_missions": 0,
            "streak": 0,
            "favorite_project_type": "Unknown"
        })
    if not os.path.exists(MISSIONS_FILE):
        save_json(MISSIONS_FILE, {})
    if not os.path.exists(VAULT_FILE):
        save_json(VAULT_FILE, {})

def load_json(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def safe_path(base, target):
    # Prevent path traversal
    abs_base = os.path.abspath(base)
    abs_target = os.path.abspath(os.path.join(base, target))
    return abs_target.startswith(abs_base)

# --- Profile System ---

def get_rank(level):
    if level >= 20: return "Ghost Architect"
    if level >= 10: return "Terminal Knight"
    if level >= 5: return "Forge Runner"
    if level >= 3: return "Code Squire"
    return "Spark"

def add_xp(amount):
    profile = load_json(PROFILE_FILE)
    profile['xp'] += amount

    # Level up logic (100 XP per level)
    while profile['xp'] >= 100:
        profile['xp'] -= 100
        profile['level'] += 1
        success(f"LEVEL UP! You are now Level {profile['level']} ({get_rank(profile['level'])}).")

    save_json(PROFILE_FILE, profile)

def draw_progress_bar(xp, total=100, length=20):
    filled = int(length * xp // total)
    bar = '█' * filled + '-' * (length - filled)
    return f"[{bar}] {xp}/{total} XP"

# --- Project Scanner ---

def detect_project_type():
    has_py = has_html = has_js = has_luau = has_md = False

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        for f in files:
            if f.endswith('.py'): has_py = True
            elif f.endswith('.html') or f.endswith('.css'): has_html = True
            elif f.endswith('.js') or f.endswith('.ts'): has_js = True
            elif f.endswith('.lua') or f.endswith('.luau'): has_luau = True
            elif f.endswith('.md'): has_md = True

    if has_py and not (has_html or has_js or has_luau): return "Python"
    if has_html or has_js: return "Web"
    if has_luau: return "Roblox/Luau"
    if has_js: return "Node"
    if has_py and (has_html or has_js): return "Mixed"
    if has_md and not (has_py or has_html or has_js or has_luau): return "Markdown/docs"
    return "Unknown"

def scan_project():
    info("Scanning project...")
    total_files = 0
    total_dirs = 0
    ext_counts = {}
    largest_files = []

    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        total_dirs += len(dirs)

        for file in files:
            if file in IGNORE_FILES: continue
            total_files += 1
            ext = os.path.splitext(file)[1].lower()
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

            filepath = os.path.join(root, file)
            try:
                size = os.path.getsize(filepath)
                largest_files.append((size, filepath))
            except OSError:
                pass

    largest_files.sort(reverse=True)
    largest_files = largest_files[:5]

    proj_type = detect_project_type()

    print("\n--- SYSTEM SCAN COMPLETE ---")
    print(f"Project Type: {proj_type}")
    print(f"Total Folders: {total_dirs}")
    print(f"Total Files: {total_files}")

    print("\nFile Types:")
    for ext, count in sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        ext_name = ext if ext else "no extension"
        print(f"  {ext_name}: {count}")

    print("\nLargest Files:")
    for size, path in largest_files:
        print(f"  {path} ({size / 1024:.1f} KB)")

    return proj_type

def build_map(startpath=".", max_depth=3):
    print("\n--- PROJECT MAP ---")

    def print_tree(dir_path, prefix="", depth=0):
        if depth > max_depth:
            print(f"{prefix}└── ... (truncated)")
            return

        try:
            entries = os.listdir(dir_path)
        except PermissionError:
            print(f"{prefix}└── [Access Denied]")
            return

        # Filter and sort
        dirs = []
        files = []
        for e in entries:
            path = os.path.join(dir_path, e)
            if e in IGNORE_DIRS or e in IGNORE_FILES or e.startswith('.'):
                continue
            if os.path.isdir(path):
                dirs.append(e)
            else:
                files.append(e)

        dirs.sort()
        files.sort()

        all_entries = dirs + files
        for i, entry in enumerate(all_entries):
            path = os.path.join(dir_path, entry)
            is_last = (i == len(all_entries) - 1)
            connector = "└── " if is_last else "├── "

            if os.path.isdir(path):
                print(f"{prefix}{connector}{entry}/")
                extension = "    " if is_last else "│   "
                print_tree(path, prefix + extension, depth + 1)
            else:
                print(f"{prefix}{connector}{entry}")

    print(".")
    print_tree(startpath)
    print("-------------------\n")

def check_status():
    proj_type = detect_project_type()
    has_readme = os.path.exists("README.md")
    has_license = os.path.exists("LICENSE")
    has_gitignore = os.path.exists(".gitignore")

    todo_count = 0
    # Quick scan for TODO/FIXME
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith('.')]
        for file in files:
            if file in IGNORE_FILES or not file.endswith(('.py', '.js', '.html', '.css', '.md', '.txt')):
                continue
            filepath = os.path.join(root, file)
            try:
                # Basic check, don't read huge files
                if os.path.getsize(filepath) < 1024 * 1024:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        todo_count += content.count("TODO") + content.count("FIXME")
            except:
                pass

    print("\n--- HEALTH REPORT ---")
    print(f"Project Type: {proj_type}")
    print(f"README.md: {'[OK]' if has_readme else '[MISSING]'}")
    print(f"LICENSE:   {'[OK]' if has_license else '[MISSING]'}")
    print(f".gitignore:{'[OK]' if has_gitignore else '[MISSING]'}")
    print(f"TODO/FIXME count: {todo_count}")

    print("\nSuggested Next Steps:")
    if not has_readme: print("- Create a README.md to document your project.")
    if not has_license: print("- Add a LICENSE if you plan to open-source this.")
    if todo_count > 0: print(f"- Knock out some of those {todo_count} TODOs/FIXMEs.")
    if has_readme and has_license and todo_count == 0: print("- Project looks healthy! Start a new mission.")

# --- Mission System ---

def generate_offline_plan(desc, proj_type):
    desc_lower = desc.lower()

    plan = {
        "disclaimer": "Offline simulated plan — no AI/API used.",
        "goals": [f"Successfully complete: {desc}"],
        "suggested_files": [],
        "steps": [],
        "testing": [],
        "risks": ["Unexpected side effects in existing logic.", "Breaking core functionality."]
    }

    if "bug" in desc_lower or "fix" in desc_lower or "error" in desc_lower or "debug" in desc_lower:
        plan["type"] = "debugging plan"
        plan["steps"] = [
            "Reproduce the bug locally.",
            "Locate the file and line number causing the issue.",
            "Write a fix and verify it doesn't break other things.",
            "Clean up debug print statements."
        ]
        plan["testing"] = ["Run existing tests.", "Manually test the edge case that caused the bug."]
    elif "feature" in desc_lower or "add" in desc_lower or "build" in desc_lower:
        plan["type"] = "feature plan"
        plan["steps"] = [
            "Outline the data structures or functions needed.",
            "Implement the core logic.",
            "Integrate the new feature into the existing UI/loop.",
            "Review code for cleanliness."
        ]
        plan["testing"] = ["Test positive path (feature works as expected).", "Test negative path (invalid inputs handled safely)."]
    elif "web" in desc_lower or "html" in desc_lower or "css" in desc_lower:
        plan["type"] = "web plan"
        plan["steps"] = [
            "Locate target HTML/CSS files.",
            "Apply layout or style changes.",
            "Check responsiveness."
        ]
        plan["testing"] = ["Test in browser.", "Resize window to check mobile view."]
    elif "roblox" in desc_lower or "luau" in desc_lower or "studio" in desc_lower:
        plan["type"] = "Roblox testing plan"
        plan["steps"] = [
            "Open Roblox Studio.",
            "Locate target Script or LocalScript.",
            "Implement logic, checking for Client/Server boundaries."
        ]
        plan["testing"] = ["Playtest in Studio.", "Check Output window for errors."]
    elif "doc" in desc_lower or "readme" in desc_lower or "license" in desc_lower:
        plan["type"] = "documentation plan"
        plan["steps"] = [
            "Open the relevant markdown file.",
            "Write clear, concise explanations.",
            "Check formatting."
        ]
        plan["testing"] = ["Preview markdown locally or on GitHub."]
    elif "refactor" in desc_lower or "clean" in desc_lower:
        plan["type"] = "refactor plan"
        plan["steps"] = [
            "Identify duplicated or messy code.",
            "Extract logic into functions/classes.",
            "Ensure old behavior is preserved."
        ]
        plan["testing"] = ["Run all tests to ensure no regressions."]
    else:
        plan["type"] = "general project plan"
        plan["steps"] = [
            "Analyze the request.",
            "Draft a solution.",
            "Implement and verify."
        ]
        plan["testing"] = ["Verify changes manually."]

    return plan

def create_mission(description, is_boss=False):
    missions = load_json(MISSIONS_FILE)
    mission_id = uuid.uuid4().hex[:6]

    proj_type = detect_project_type()

    missions[mission_id] = {
        "id": mission_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "description": description,
        "type": "boss" if is_boss else "normal",
        "xp_reward": 150 if is_boss else 50,
        "project_type": proj_type,
        "status": "active",
        "notes": [],
        "plan": generate_offline_plan(description, proj_type)
    }

    save_json(MISSIONS_FILE, missions)

    mission_type_str = "BOSS MISSION" if is_boss else "MISSION"
    success(f"{mission_type_str} CREATED: {mission_id} - {description}")
    info(f"Reward: {missions[mission_id]['xp_reward']} XP")

def list_missions():
    missions = load_json(MISSIONS_FILE)
    if not missions:
        info("No missions found in the forge.")
        return

    print("\n--- MISSION BOARD ---")
    for mid, m in missions.items():
        status_color = ""
        if m['status'] == 'completed': status_color = "\033[92m" # Green
        elif m['status'] == 'failed': status_color = "\033[91m" # Red
        else: status_color = "\033[93m" # Yellow (Active)

        mtype = "BOSS" if m['type'] == 'boss' else "Norm"
        print_colored(f"[{m['status'].upper()}] {mid} | {mtype} | {m['description']} ({m['xp_reward']} XP)", status_color)

def open_mission(mission_id):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    m = missions[mission_id]
    print(f"\n=== MISSION: {m['id']} ===")
    print(f"Desc:   {m['description']}")
    print(f"Status: {m['status'].upper()}")
    print(f"Type:   {m['type'].upper()}")
    print(f"Reward: {m['xp_reward']} XP")
    print(f"Date:   {m['timestamp']}")
    print("\nNotes:")
    if not m['notes']: print("  (No notes yet. Use 'log <id> <note>' to add one)")
    for note in m['notes']:
        print(f"  - {note}")
    print("======================\n")

def show_plan(mission_id):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    plan = missions[mission_id].get('plan')
    if not plan:
        error("No plan generated for this mission.")
        return

    print(f"\n--- MISSION PLAN ({plan.get('type', 'plan')}) ---")
    warning(plan.get('disclaimer', 'Offline plan'))
    print("\nGoals:")
    for g in plan['goals']: print(f"  - {g}")
    print("\nSteps:")
    for i, s in enumerate(plan['steps'], 1): print(f"  {i}. {s}")
    print("\nTesting Checklist:")
    for t in plan['testing']: print(f"  [ ] {t}")
    print("\nRisks:")
    for r in plan['risks']: print(f"  ! {r}")
    print("------------------------\n")

def complete_mission(mission_id):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    if missions[mission_id]['status'] == 'completed':
        warning("Mission already completed!")
        return

    missions[mission_id]['status'] = 'completed'
    save_json(MISSIONS_FILE, missions)

    xp = missions[mission_id]['xp_reward']
    success(f"Mission '{mission_id}' complete! Gained {xp} XP.")

    profile = load_json(PROFILE_FILE)
    profile['missions_completed'] += 1
    if missions[mission_id]['type'] == 'boss':
        profile['boss_missions_completed'] += 1
    save_json(PROFILE_FILE, profile)

    add_xp(xp)

def fail_mission(mission_id):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    if missions[mission_id]['status'] != 'active':
        warning(f"Cannot fail a mission that is {missions[mission_id]['status']}.")
        return

    missions[mission_id]['status'] = 'failed'
    save_json(MISSIONS_FILE, missions)

    error(f"Mission '{mission_id}' failed. Don't give up, Ghost!")

    profile = load_json(PROFILE_FILE)
    profile['failed_missions'] += 1
    save_json(PROFILE_FILE, profile)

def log_note(mission_id, note):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    missions[mission_id]['notes'].append(note)
    save_json(MISSIONS_FILE, missions)
    success("Note added to mission vault.")

# --- Vault System ---

def vault_add(title, text):
    vault = load_json(VAULT_FILE)
    vid = uuid.uuid4().hex[:6]
    vault[vid] = {
        "title": title,
        "text": text,
        "timestamp": datetime.datetime.now().isoformat()
    }
    save_json(VAULT_FILE, vault)
    success(f"Added '{title}' to Vault [{vid}].")

def vault_list():
    vault = load_json(VAULT_FILE)
    if not vault:
        info("Vault is empty.")
        return
    print("\n--- VAULT ---")
    for vid, v in vault.items():
        print(f"[{vid}] {v['title']}")

def vault_search(keyword):
    vault = load_json(VAULT_FILE)
    keyword = keyword.lower()
    found = False
    print(f"\n--- VAULT SEARCH: '{keyword}' ---")
    for vid, v in vault.items():
        if keyword in v['title'].lower() or keyword in v['text'].lower():
            print(f"\n[{vid}] {v['title']}")
            print(f"  {v['text']}")
            found = True
    if not found:
        info("No matching entries found.")

# --- Export System ---

def export_mission(mission_id):
    missions = load_json(MISSIONS_FILE)
    if mission_id not in missions:
        error("Mission not found.")
        return

    m = missions[mission_id]

    # Safe filename creation
    base_filename = f"mission_{mission_id}.md"
    export_path = os.path.join(EXPORTS_DIR, base_filename)

    counter = 1
    while os.path.exists(export_path):
        export_path = os.path.join(EXPORTS_DIR, f"mission_{mission_id}_{counter}.md")
        counter += 1

    profile = load_json(PROFILE_FILE)
    rank = get_rank(profile['level'])

    content = f"""# GhostForge Mission Export

## Mission Details
- **ID:** {m['id']}
- **Description:** {m['description']}
- **Type:** {m['type']}
- **XP Reward:** {m['xp_reward']}
- **Status:** {m['status']}
- **Timestamp:** {m['timestamp']}

## Project Summary
- Project Type: {m.get('project_type', 'Unknown')}

## Offline Plan
_{m['plan'].get('disclaimer', '')}_

**Goals:**
"""
    for g in m['plan'].get('goals', []): content += f"- {g}\n"
    content += "\n**Steps:**\n"
    for i, s in enumerate(m['plan'].get('steps', []), 1): content += f"{i}. {s}\n"
    content += "\n**Testing:**\n"
    for t in m['plan'].get('testing', []): content += f"- [ ] {t}\n"

    content += "\n## Notes\n"
    if m['notes']:
        for note in m['notes']: content += f"- {note}\n"
    else:
        content += "(No notes)\n"

    content += f"\n## XP/Profile Summary\n"
    content += f"- Level {profile['level']}: {rank} ({profile['xp']} XP)\n"

    try:
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write(content)
        success(f"Mission exported to {export_path}")
    except Exception as e:
        error(f"Failed to export mission: {e}")

# --- Core Loop ---

def show_profile():
    profile = load_json(PROFILE_FILE)
    print("\n--- GHOSTFORGE PROFILE ---")
    print(f"Name:  {profile['username']}")
    print(f"Rank:  {get_rank(profile['level'])} (Level {profile['level']})")
    print(draw_progress_bar(profile['xp']))
    print(f"Total XP: {profile['level']*100 - 100 + profile['xp']}")
    print("\nStats:")
    print(f"  Missions Completed: {profile['missions_completed']}")
    print(f"  Bosses Defeated:    {profile['boss_missions_completed']}")
    print(f"  Missions Failed:    {profile['failed_missions']}")
    print("--------------------------\n")

def reset_demo():
    warning("This will delete all GhostForge data (missions, profile, vault) in this project.")
    confirm = input("Are you sure? (y/N): ")
    if confirm.lower() == 'y':
        try:
            if os.path.exists(DATA_DIR):
                shutil.rmtree(DATA_DIR)
            init_env()
            success("GhostForge data reset.")
        except Exception as e:
            error(f"Failed to reset data: {e}")
    else:
        info("Reset cancelled.")

def print_help():
    print("""
Available Commands:
  help                    - Show this menu
  scan                    - Scan current project folder
  map                     - Show a readable tree of the project
  status                  - Generate local health report
  mission <desc>          - Create a normal mission
  boss <desc>             - Create a boss mission
  missions                - List all missions
  open <id>               - Open mission details
  plan <id>               - Generate offline plan
  complete <id>           - Complete mission and gain XP
  fail <id>               - Mark mission as failed
  log <id> <note>         - Add a note to a mission
  vault add <title> <txt> - Save a note to the vault
  vault list              - List vault entries
  vault search <keyword>  - Search the vault
  export <id>             - Export mission to markdown
  profile                 - View your stats and rank
  reset-demo              - Reset GhostForge sample data
  quit / exit             - Close the forge
""")

def main():
    init_env()
    print_colored(BANNER, "\033[96m")
    info("GhostForge CLI initialized. Type 'help' for commands.")

    while True:
        try:
            cmd_input = input("\033[92mghostforge>\033[0m ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting Forge. Goodbye.")
            break

        if not cmd_input:
            continue

        parts = cmd_input.split()
        cmd = parts[0].lower()
        args = parts[1:]

        if cmd in ['quit', 'exit']:
            print("Exiting Forge. Goodbye.")
            break
        elif cmd == 'help':
            print_help()
        elif cmd == 'scan':
            scan_project()
        elif cmd == 'map':
            build_map()
        elif cmd == 'status':
            check_status()
        elif cmd == 'mission':
            if not args:
                error("Please provide a description: mission <description>")
            else:
                create_mission(" ".join(args), is_boss=False)
        elif cmd == 'boss':
            if not args:
                error("Please provide a description: boss <description>")
            else:
                create_mission(" ".join(args), is_boss=True)
        elif cmd == 'missions':
            list_missions()
        elif cmd == 'open':
            if len(args) != 1: error("Usage: open <mission_id>")
            else: open_mission(args[0])
        elif cmd == 'plan':
            if len(args) != 1: error("Usage: plan <mission_id>")
            else: show_plan(args[0])
        elif cmd == 'complete':
            if len(args) != 1: error("Usage: complete <mission_id>")
            else: complete_mission(args[0])
        elif cmd == 'fail':
            if len(args) != 1: error("Usage: fail <mission_id>")
            else: fail_mission(args[0])
        elif cmd == 'log':
            if len(args) < 2: error("Usage: log <mission_id> <note>")
            else: log_note(args[0], " ".join(args[1:]))
        elif cmd == 'vault':
            if not args:
                error("Usage: vault add|list|search")
            elif args[0] == 'add':
                if len(args) < 3: error("Usage: vault add <title> <text>")
                else: vault_add(args[1], " ".join(args[2:]))
            elif args[0] == 'list':
                vault_list()
            elif args[0] == 'search':
                if len(args) < 2: error("Usage: vault search <keyword>")
                else: vault_search(args[1])
            else:
                error("Unknown vault command.")
        elif cmd == 'export':
            if len(args) != 1: error("Usage: export <mission_id>")
            else: export_mission(args[0])
        elif cmd == 'profile':
            show_profile()
        elif cmd == 'reset-demo':
            reset_demo()
        else:
            error(f"Unknown command: '{cmd}'. Type 'help' for a list of commands.")

if __name__ == "__main__":
    main()
