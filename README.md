# ⌨ jshortcuts-jubuntu

> A personal keyboard shortcut manager for Ubuntu — dark GUI popup **and** a colourful CLI tool, both synced to the same file.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Platform: Ubuntu](https://img.shields.io/badge/platform-Ubuntu-orange)](https://ubuntu.com)
[![Made by: Jbtechnix](https://img.shields.io/badge/by-Jbtechnix-purple)](https://github.com/johnboscocjt)

---

**jshortcuts** is a lightweight personal shortcut-reference tool for Ubuntu.  
It is **not** connected to Ubuntu's system configuration — it's your own editable cheatsheet where you record, browse, and update your keyboard shortcuts and workflow notes.

Both the **GUI window** and the **CLI tool** read and write the same `~/.jshortcuts.json` file so they always show identical data.

---

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Usage](#-cli-usage)
- [GUI Usage](#-gui-usage)
- [Data File Format](#-data-file-format)
- [Examples](#-examples)
- [Uninstall](#-uninstall)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

| Feature | CLI | GUI |
|---|---|---|
| View all shortcuts | ✅ | ✅ |
| Filter by category | ✅ | ✅ |
| Search shortcuts | ✅ | ✅ |
| Add shortcut | ✅ | ✅ |
| Edit shortcut | ✅ | ✅ |
| Delete shortcut | ✅ | ✅ |
| Color-coded categories | ✅ | ✅ |
| Notes per shortcut | ✅ | ✅ |
| Shared data file | ✅ | ✅ |
| Desktop app launcher | — | ✅ |

---

## 🛠 Requirements

- Ubuntu 20.04 or later (also works on Debian-based distros)
- Python 3.8+
- `tkinter` (for the GUI only) — usually pre-installed on Ubuntu

Check whether everything is ready:

```bash
python3 --version
python3 -c "import tkinter; print('tkinter OK')"
```

If tkinter is missing, install it:

```bash
sudo apt install python3-tk
```

---

## 📦 Installation

### Option 1 — Automated (recommended)

One script handles everything. Run these three commands:

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu
bash install.sh
```

**The install script automatically:**
- ✅ Verifies Python 3 is installed
- ✅ Checks for tkinter (warns if missing, CLI still works)
- ✅ Copies `jshortcuts` and `jshortcuts-gui.py` to `~/bin/`
- ✅ Makes both scripts executable
- ✅ Creates `~/.jshortcuts.json` with 12 example shortcuts (skipped if it already exists)
- ✅ Adds `~/bin` to `PATH` in your `~/.bashrc` / `~/.zshrc` automatically
- ✅ Activates `~/bin` in the **current terminal** immediately — no restart needed
- ✅ Creates a `.desktop` launcher so jshortcuts appears in your Ubuntu app menu

**After the script finishes, jshortcuts is ready to use immediately** in that terminal:

```bash
jshortcuts        # try it right now
jshortcuts gui    # open the GUI
```

New terminal windows will also have jshortcuts available automatically because the script updated your shell config.

---

### Option 2 — Manual (step by step)

Use this if you prefer to see exactly what happens, or if the automated installer fails.

**Step 1 — Clone the repository**

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu
```

**Step 2 — Create ~/bin and copy the scripts**

```bash
mkdir -p ~/bin
cp jshortcuts          ~/bin/jshortcuts
cp jshortcuts-gui.py   ~/bin/jshortcuts-gui.py
cp jshortcuts_default.json  ~/bin/jshortcuts_default.json
```

**Step 3 — Make both scripts executable**

```bash
chmod +x ~/bin/jshortcuts
chmod +x ~/bin/jshortcuts-gui.py
```

**Step 4 — Add ~/bin to your PATH** (skip if already present)

```bash
# Check if it's already in your PATH:
echo $PATH | grep -q "$HOME/bin" && echo "Already there" || echo "Not yet added"
```

If it says "Not yet added":

```bash
echo '' >> ~/.bashrc
echo '# jshortcuts' >> ~/.bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
```

Then activate it in the current terminal:

```bash
source ~/.bashrc
```

If you use Zsh instead of Bash:

```bash
echo '' >> ~/.zshrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Step 5 — Create your data file**

```bash
# Only do this if ~/.jshortcuts.json doesn't already exist:
cp jshortcuts_default.json ~/.jshortcuts.json
```

**Step 6 — Verify it works**

```bash
jshortcuts
```

You should see a coloured list of example shortcuts. If you get "command not found", re-run `source ~/.bashrc` in the current terminal.

---

## ⚡ Quick Start

```bash
jshortcuts           # view all shortcuts
jshortcuts add       # add your first custom shortcut
jshortcuts gui       # open the GUI window
```

---

## 🖥 CLI Usage

```
jshortcuts [command] [argument]
```

| Command | Description |
|---|---|
| `jshortcuts` | List all shortcuts grouped by category |
| `jshortcuts add` | Add a new shortcut (interactive prompts) |
| `jshortcuts edit <id>` | Edit a shortcut by its ID |
| `jshortcuts del <id>` | Delete a shortcut by its ID |
| `jshortcuts cat <name>` | Filter shortcuts by category |
| `jshortcuts search <query>` | Search across keys, description, notes |
| `jshortcuts gui` | Launch the GUI popup window |
| `jshortcuts help` | Show help message |

### Listing shortcuts

```bash
jshortcuts
```

```
──────────── ⌨  jshortcuts — My Keyboard Shortcuts ────────────────

  ▸ Navigation

    [  1]  Super + D                     Show / Hide Desktop
    [  2]  Super + Left / Right          Snap window to half screen

  ▸ Terminal

    [  4]  Ctrl + Alt + T                Open Terminal
                                          ↳ Default Ubuntu terminal shortcut

  ▸ Browser

    [  7]  Ctrl + T                      New Tab

──────────────────────────────────────────────────────────────────
  7 shortcut(s)  │  data: /home/you/.jshortcuts.json
  jshortcuts add | edit <id> | del <id> | gui
```

### Adding a shortcut

```bash
jshortcuts add
```

```
  ── Add New Shortcut ──────────────────

  Existing categories: Navigation, Terminal, Browser

  Category (e.g. Terminal, Browser): VS Code
  Keys (e.g. Ctrl + T): Ctrl + `
  Description: Toggle integrated terminal
  Notes (optional): Also works in most editors

  ✓ Shortcut #13 added.
```

### Editing a shortcut

```bash
jshortcuts edit 4
```

```
  ── Edit Shortcut #4 ─────────────────
  (Press Enter to keep current value)

  Category [Terminal]:
  Keys [Ctrl + Alt + T]:
  Description [Open Terminal]: Open Gnome Terminal
  Notes [Default Ubuntu terminal shortcut]:

  ✓ Shortcut #4 updated.
```

### Deleting a shortcut

```bash
jshortcuts del 7
```

```
  Delete: [7] Ctrl + T — New Tab
  Are you sure? (y/N): y

  ✓ Shortcut #7 deleted.
```

### Filtering by category

```bash
jshortcuts cat Terminal
jshortcuts cat Browser
jshortcuts cat "VS Code"
```

### Searching

```bash
jshortcuts search ctrl
jshortcuts search terminal
jshortcuts search snap
```

---

## 🪟 GUI Usage

```bash
jshortcuts gui
# or:
python3 ~/bin/jshortcuts-gui.py
# or: search "jshortcuts" in the Ubuntu app menu
```

### Window layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ ⌨  jshortcuts       my keyboard shortcuts         [⌕ search...    ] │
├────────────────┬─────────────────────────────────────────────────────┤
│ CATEGORIES     │  12 shortcut(s)         [+ Add]  [✎ Edit] [✕ Delete]│
│                ├─────────────────────────────────────────────────────┤
│  All           │  ▸ NAVIGATION                                       │
│  Navigation    │   [1]  Super + D              Show / Hide Desktop   │
│  Terminal      │   [2]  Super + Left/Right     Snap to half screen   │
│  Browser       │                                                     │
│  System        │  ▸ TERMINAL                                         │
│                │   [4]  Ctrl + Alt + T         Open Terminal         │
│                │         Default Ubuntu terminal shortcut            │
├────────────────┴─────────────────────────────────────────────────────┤
│  data: /home/yourname/.jshortcuts.json                               │
└──────────────────────────────────────────────────────────────────────┘
```

### GUI actions

| Action | How to do it |
|---|---|
| Select a shortcut | Single click on a row |
| Edit a shortcut | Double-click a row, **or** select then click ✎ Edit |
| Add a shortcut | Click **+ Add**, fill the form, click **Save** |
| Delete a shortcut | Single-click to select, then click **✕ Delete** |
| Filter by category | Click a category name in the left sidebar |
| Search | Type in the search box (top right) |
| Scroll | Mouse wheel or trackpad |

> **Tip:** In the Add/Edit dialog, press **Enter** to save or **Escape** to cancel.

---

## 📄 Data File Format

All shortcuts live in `~/.jshortcuts.json`. You can edit this file directly in any text editor — both the CLI and GUI will pick up your changes on the next run.

```json
{
  "shortcuts": [
    {
      "id": 1,
      "category": "Terminal",
      "keys": "Ctrl + Alt + T",
      "description": "Open Terminal",
      "notes": "Default Ubuntu terminal shortcut"
    },
    {
      "id": 2,
      "category": "Browser",
      "keys": "Ctrl + T",
      "description": "New Tab",
      "notes": ""
    }
  ],
  "next_id": 3
}
```

**Fields:**

| Field | Required | Description |
|---|---|---|
| `id` | auto | Unique integer, assigned automatically, never reused |
| `category` | yes | Group label (Navigation, Terminal, Browser, etc.) |
| `keys` | yes | The key combination, e.g. `Ctrl + Shift + P` |
| `description` | yes | What the shortcut does |
| `notes` | no | Extra info, tip, or context |

---

## 💡 Examples

### Add a full VS Code shortcut set

```bash
jshortcuts add   # Category: VS Code | Keys: Ctrl + P        | Description: Quick file open
jshortcuts add   # Category: VS Code | Keys: Ctrl + Shift + P | Description: Command palette
jshortcuts add   # Category: VS Code | Keys: Ctrl + `         | Description: Toggle terminal
jshortcuts add   # Category: VS Code | Keys: Ctrl + B         | Description: Toggle sidebar
```

Then view them:

```bash
jshortcuts cat "VS Code"
```

### Back up your shortcuts

```bash
cp ~/.jshortcuts.json ~/Desktop/shortcuts_backup_$(date +%Y%m%d).json
```

### Restore from backup

```bash
cp ~/Desktop/shortcuts_backup_20260327.json ~/.jshortcuts.json
```

### Reset to the default examples

```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

---

## 🗑 Uninstall

```bash
bash uninstall.sh
```

**The uninstaller removes:**
- `~/bin/jshortcuts`
- `~/bin/jshortcuts-gui.py`
- `~/bin/jshortcuts_default.json`
- The `.desktop` app launcher

**Your data file `~/.jshortcuts.json` is kept by default.** The uninstaller will ask if you want to delete it too.

To also remove the PATH line added to your shell config:

```bash
# Open ~/.bashrc and remove the two lines that mention jshortcuts
nano ~/.bashrc
```

---

## 🔧 Troubleshooting

### `jshortcuts: command not found` after install

The installer already updated your shell config, but the current terminal may need refreshing:

```bash
source ~/.bashrc
# or, if using zsh:
source ~/.zshrc
```

Then try `jshortcuts` again. New terminal windows will work automatically.

### GUI doesn't open

```bash
# Check tkinter
python3 -c "import tkinter; print('OK')"
# Install if missing
sudo apt install python3-tk
```

### Font looks different / plain

Install JetBrains Mono for the best experience:

```bash
sudo apt install fonts-jetbrains-mono
```

Log out and back in for it to take effect.

### My shortcuts disappeared / data is empty

Check if the data file exists:

```bash
cat ~/.jshortcuts.json
```

If it's missing or empty, restore from the defaults:

```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

### Permission denied when running

```bash
chmod +x ~/bin/jshortcuts
chmod +x ~/bin/jshortcuts-gui.py
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request against `main`

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## 📄 License

MIT © 2026 [Jbtechnix - Mr. Humble Beginnings](https://github.com/johnboscocjt)  
See [LICENSE](LICENSE) for full text.
