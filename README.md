# ⌨ jshortcuts-jubuntu

> A personal keyboard shortcut manager for Ubuntu — with a dark GUI popup **and** a colourful CLI tool, both synced to the same file.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Platform: Ubuntu](https://img.shields.io/badge/platform-Ubuntu-orange)](https://ubuntu.com)
[![Made by: Jbtechnix](https://img.shields.io/badge/by-Jbtechnix-purple)](https://github.com/johnboscocjt)

---

**jshortcuts** is a lightweight personal shortcut-reference tool.  
It is **not** connected to Ubuntu's system configuration — it's your own editable cheatsheet where you record and browse your keyboard shortcuts, launch commands, and workflow notes.

Both the **GUI window** and the **CLI tool** read and write the same `~/.jshortcuts.json` file, so they always show the same data.

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
- `tkinter` (for the GUI) — usually pre-installed on Ubuntu

Check if tkinter is available:

```bash
python3 -c "import tkinter; print('tkinter OK')"
```

If missing, install it:

```bash
sudo apt install python3-tk
```

---

## 📦 Installation

### Option 1 — Automated (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu

# 2. Run the installer
bash install.sh
```

The installer will:
- Copy scripts to `~/bin/`
- Make them executable
- Create `~/.jshortcuts.json` with example shortcuts
- Create a `.desktop` launcher (so jshortcuts appears in your app menu)

Then reload your shell:

```bash
source ~/.bashrc
# or, if you use zsh:
source ~/.zshrc
```

### Option 2 — Manual

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu

mkdir -p ~/bin
cp jshortcuts ~/bin/jshortcuts
cp jshortcuts-gui.py ~/bin/jshortcuts-gui.py
cp jshortcuts_default.json ~/bin/jshortcuts_default.json
chmod +x ~/bin/jshortcuts ~/bin/jshortcuts-gui.py

# Add ~/bin to PATH if not already there
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## ⚡ Quick Start

```bash
# See all your shortcuts
jshortcuts

# Add your first shortcut
jshortcuts add

# Open the GUI window
jshortcuts gui
```

---

## 🖥 CLI Usage

```
jshortcuts [command] [arguments]
```

| Command | Description |
|---|---|
| `jshortcuts` | List all shortcuts |
| `jshortcuts add` | Add a new shortcut (interactive prompts) |
| `jshortcuts edit <id>` | Edit a shortcut by its ID |
| `jshortcuts del <id>` | Delete a shortcut by its ID |
| `jshortcuts cat <name>` | Filter shortcuts by category |
| `jshortcuts search <query>` | Search across keys, description, notes |
| `jshortcuts gui` | Launch the GUI popup window |
| `jshortcuts help` | Show help message |

### List all shortcuts

```bash
jshortcuts
```

Output:

```
──────────────── ⌨  jshortcuts — My Keyboard Shortcuts ────────────────

  ▸ Navigation

    [ 1]  Super + D                     Show/Hide Desktop
    [ 2]  Super + Left/Right            Snap window to half screen

  ▸ Terminal

    [ 3]  Ctrl + Alt + T                Open Terminal
               ↳ Default Ubuntu terminal shortcut
    [ 4]  Ctrl + Shift + C              Copy in Terminal

  ▸ Browser

    [ 5]  Ctrl + T                      New Tab
    [ 6]  Ctrl + Shift + T              Reopen closed Tab

──────────────────────────────────────────────────────────────────────
  6 shortcut(s)  │  data: /home/yourname/.jshortcuts.json
  jshortcuts add | edit <id> | del <id> | gui
```

### Add a shortcut

```bash
jshortcuts add
```

You'll be prompted:

```
  ── Add New Shortcut ──────────────────

  Existing categories: Navigation, Terminal, Browser

  Category (e.g. Terminal, Browser): VS Code
  Keys (e.g. Ctrl + T): Ctrl + `
  Description: Toggle integrated terminal
  Notes (optional): Works in most editors too
```

### Edit a shortcut

```bash
jshortcuts edit 3
```

```
  ── Edit Shortcut #3 ─────────────────
  (Press Enter to keep current value)

  Category [Terminal]:
  Keys [Ctrl + Alt + T]:
  Description [Open Terminal]: Open Terminal (Gnome)
  Notes [Default Ubuntu terminal shortcut]:

  ✓ Shortcut #3 updated.
```

### Delete a shortcut

```bash
jshortcuts del 5
```

```
  Delete: [5] Ctrl + T — New Tab
  Are you sure? (y/N): y

  ✓ Shortcut #5 deleted.
```

### Filter by category

```bash
jshortcuts cat Terminal
jshortcuts cat "VS Code"
```

### Search

```bash
jshortcuts search ctrl
jshortcuts search terminal
jshortcuts search snap
```

---

## 🪟 GUI Usage

Launch the GUI:

```bash
jshortcuts gui
# or directly:
python3 ~/bin/jshortcuts-gui.py
```

Or find it in your **Ubuntu app menu** (after install) as **jshortcuts**.

### GUI Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ ⌨  jshortcuts          my keyboard shortcuts       [⌕ search  ] │
├────────────┬────────────────────────────────────────────────────┤
│ CATEGORIES │  0 shortcut(s)         [+ Add] [✎ Edit] [✕ Delete]│
│            ├────────────────────────────────────────────────────┤
│  All       │  ▸ NAVIGATION                                      │
│  Navigation│    [1]  Super + D          Show/Hide Desktop       │
│  Terminal  │    [2]  Super + Left/Right Snap window to half     │
│  Browser   │                                                    │
│  System    │  ▸ TERMINAL                                        │
│            │    [3]  Ctrl + Alt + T     Open Terminal           │
│            │         Default Ubuntu terminal shortcut           │
│            │    [4]  Ctrl + Shift + C   Copy in Terminal        │
├────────────┴────────────────────────────────────────────────────┤
│  data: /home/yourname/.jshortcuts.json                          │
└─────────────────────────────────────────────────────────────────┘
```

### GUI Actions

| Action | How |
|---|---|
| **Select a row** | Single click |
| **Edit a shortcut** | Double-click a row, or select then click ✎ Edit |
| **Add a shortcut** | Click + Add |
| **Delete a shortcut** | Select row, click ✕ Delete |
| **Filter by category** | Click a category in the sidebar |
| **Search** | Type in the search box (top right) |
| **Scroll** | Mouse wheel / trackpad scroll |

---

## 📄 Data File Format

All shortcuts are stored in `~/.jshortcuts.json`:

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

You can also **edit this file directly** in any text editor. Both the CLI and GUI will pick up your changes immediately on next run.

---

## 💡 Examples

### Add shortcuts for VS Code

```bash
jshortcuts add
# Category: VS Code
# Keys: Ctrl + P
# Description: Quick file open
# Notes: Type filename to jump to it

jshortcuts add
# Category: VS Code
# Keys: Ctrl + Shift + P
# Description: Command palette
# Notes:

jshortcuts add
# Category: VS Code
# Keys: Ctrl + `
# Description: Toggle integrated terminal
# Notes:
```

### Add a custom app launcher note

```bash
jshortcuts add
# Category: Apps
# Keys: Super (hold)
# Description: Show activity overview
# Notes: Also shows search bar
```

### View only Browser shortcuts in CLI

```bash
jshortcuts cat Browser
```

### Search for anything with "terminal"

```bash
jshortcuts search terminal
```

### Edit a shortcut you got wrong

```bash
jshortcuts          # find the ID first
jshortcuts edit 7   # edit it
```

### Export / backup your shortcuts

```bash
cp ~/.jshortcuts.json ~/Desktop/my_shortcuts_backup.json
```

### Restore from backup

```bash
cp ~/Desktop/my_shortcuts_backup.json ~/.jshortcuts.json
```

---

## 🗑 Uninstall

Run the uninstaller:

```bash
bash uninstall.sh
```

The uninstaller will:
- Remove `~/bin/jshortcuts`
- Remove `~/bin/jshortcuts-gui.py`
- Remove `~/bin/jshortcuts_default.json`
- Remove the `.desktop` app launcher

Your data file `~/.jshortcuts.json` is **kept by default** so you don't lose your shortcuts. To delete it too:

```bash
rm ~/.jshortcuts.json
```

---

## 🔧 Troubleshooting

### `jshortcuts: command not found`

`~/bin` is not in your PATH. Add it:

```bash
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### GUI doesn't open

Make sure tkinter is installed:

```bash
sudo apt install python3-tk
python3 -c "import tkinter; print('OK')"
```

### Font looks wrong in GUI

The GUI uses JetBrains Mono. If not installed, it falls back gracefully. To install it:

```bash
sudo apt install fonts-jetbrains-mono
```

### Shortcut data is empty after install

The default data is copied only if `~/.jshortcuts.json` doesn't already exist. To reset to defaults:

```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

### `Permission denied` when running jshortcuts

```bash
chmod +x ~/bin/jshortcuts
chmod +x ~/bin/jshortcuts-gui.py
```

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Short version:
1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

---

## 📜 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

---

## 📄 License

MIT © 2026 [Jbtechnix - Mr. Humble Beginnings](https://github.com/johnboscocjt)

See [LICENSE](LICENSE) for full text.
