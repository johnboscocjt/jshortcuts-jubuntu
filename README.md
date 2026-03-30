# jshortcuts-jubuntu

> A personal keyboard shortcut manager for Ubuntu — dark GUI popup **and** a colourful CLI tool, both synced to the same file.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue)](https://python.org)
[![Platform: Ubuntu](https://img.shields.io/badge/platform-Ubuntu-orange)](https://ubuntu.com)
[![Made by: Jbtechnix](https://img.shields.io/badge/by-Jbtechnix-purple)](https://github.com/johnboscocjt)

---

**jshortcuts** is a lightweight personal shortcut-reference tool.
It is **not** connected to Ubuntu's system configuration — it is your own editable cheatsheet where you record, browse, and update keyboard shortcuts and workflow notes.

Both the **GUI window** and the **CLI tool** share the same `~/.jshortcuts.json` file and always show identical data.

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [GUI Usage](#gui-usage)
- [GitHub Sync](#github-sync)
- [Launch via Ubuntu Custom Shortcut](#launch-via-ubuntu-custom-shortcut)
- [Data File Format](#data-file-format)
- [Examples](#examples)
- [Uninstall](#uninstall)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Feature | CLI | GUI |
|---|---|---|
| View all shortcuts | Yes | Yes |
| Filter by category | Yes | Yes |
| Search shortcuts | Yes | Yes |
| Add shortcut | Yes | Yes |
| Edit shortcut | Yes | Yes |
| Delete shortcut | Yes | Yes |
| Color-coded categories | Yes | Yes |
| Notes per shortcut | Yes | Yes |
| Open data file in editor | Yes | Yes |
| Push shortcuts to GitHub | Yes | Yes |
| CLI commands reference page | -- | Yes |
| Desktop app launcher | -- | Yes |
| Ctrl+C closes GUI from terminal | -- | Yes |

---

## Requirements

- Ubuntu 20.04 or later (also works on Debian-based distros)
- Python 3.8+
- `tkinter` — for the GUI only, usually pre-installed on Ubuntu

Check whether everything is ready:

```bash
python3 --version
python3 -c "import tkinter; print('tkinter OK')"
```

If tkinter is missing:

```bash
sudo apt install python3-tk
```

---

## Installation

### Option 1 -- Automated (recommended)

Run these three commands and the installer handles everything:

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu
bash install.sh
```

**The installer does all of this automatically -- no extra steps needed:**

| Step | What happens |
|---|---|
| 1/6 | Checks that Python 3 is installed |
| 2/6 | Checks that tkinter is available (warns if missing, CLI still works) |
| 3/6 | Creates `~/bin/` directory, copies `jshortcuts` and `jshortcuts-gui.py` to `~/bin/`, and makes them executable |
| 4/6 | Creates `~/.jshortcuts.json` with 12 example shortcuts (skipped if it already exists) |
| 5/6 | Writes `export PATH="$HOME/bin:$PATH"` into `~/.bashrc`, `~/.zshrc`, and `~/.profile` (whichever exist) -- also activates it immediately in the current terminal |
| 6/6 | Creates a `.desktop` launcher so jshortcuts appears in your Ubuntu app menu |

**After the script finishes, jshortcuts is ready immediately in that same terminal:**

```bash
jshortcuts        # try it now
jshortcuts gui    # open the GUI window
```

New terminal windows will also have jshortcuts available -- no restart needed.

---

### Option 2 -- Manual (step by step)

Use this if you prefer to understand exactly what happens, or if the installer fails.

**Step 1 -- Clone the repository**

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu
```

**Step 2 -- Create the ~/bin directory and copy scripts**

```bash
mkdir -p ~/bin
cp jshortcuts               ~/bin/jshortcuts
cp jshortcuts-gui.py        ~/bin/jshortcuts-gui.py
cp jshortcuts_default.json  ~/bin/jshortcuts_default.json
```

**Step 3 -- Make both scripts executable**

```bash
chmod +x ~/bin/jshortcuts
chmod +x ~/bin/jshortcuts-gui.py
```

**Step 4 -- Add ~/bin to your PATH**

First check whether it is already there:

```bash
echo $PATH | grep "$HOME/bin" && echo "Already in PATH" || echo "Not in PATH yet"
```

If it says "Not in PATH yet", add it:

```bash
# For Bash users:
echo '' >> ~/.bashrc
echo '# jshortcuts' >> ~/.bashrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc

# For Zsh users (if you use zsh instead of bash):
echo '' >> ~/.zshrc
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
```

Activate it in the current terminal (only needed once -- new terminals pick it up automatically):

```bash
source ~/.bashrc
# or: source ~/.zshrc
```

**Step 5 -- Create your data file**

Only needed if `~/.jshortcuts.json` does not exist yet:

```bash
[ -f ~/.jshortcuts.json ] || cp jshortcuts_default.json ~/.jshortcuts.json
```

**Step 6 -- Create the desktop launcher (optional)**

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/jshortcuts.desktop << 'EOF'
[Desktop Entry]
Name=jshortcuts
Comment=Personal keyboard shortcuts manager
Exec=python3 /home/YOUR_USERNAME/bin/jshortcuts-gui.py
Icon=input-keyboard
Type=Application
Categories=Utility;
Terminal=false
EOF
```

Replace `YOUR_USERNAME` with your actual username (run `whoami` to see it).

**Step 7 -- Verify it works**

```bash
jshortcuts
```

You should see a coloured list of example shortcuts. If you get "command not found", run `source ~/.bashrc` and try again.

---

## Quick Start

```bash
jshortcuts           # see all shortcuts
jshortcuts add       # add your first one
jshortcuts gui       # open the GUI
```

---

## CLI Usage

```
jshortcuts [command] [argument]
```

| Command | Description |
|---|---|
| `jshortcuts` | List all shortcuts grouped by category |
| `jshortcuts add` | Add a new shortcut (interactive prompts) |
| `jshortcuts edit <id>` | Edit a shortcut by its ID |
| `jshortcuts del <id>` | Delete a shortcut by its ID |
| `jshortcuts cat <n>` | Filter shortcuts by category |
| `jshortcuts search <query>` | Search across keys, description, notes |
| `jshortcuts open` | Open the data file in your default editor |
| `jshortcuts github push/pull` | Push your shortcuts to a GitHub repository or pull to force-override local state |
| `jshortcuts gui` | Launch the GUI popup window |
| `jshortcuts help` | Show help message |

### List all shortcuts

```bash
jshortcuts
```

```
-------- jshortcuts -- My Keyboard Shortcuts --------

  > Navigation

    [  1]  Super + D                     Show / Hide Desktop
    [  2]  Super + Left / Right          Snap window to half screen

  > Terminal

    [  4]  Ctrl + Alt + T                Open Terminal
                                          -> Default Ubuntu terminal shortcut

-----------------------------------------------------
  12 shortcut(s)  |  data: /home/you/.jshortcuts.json
  jshortcuts add | edit <id> | del <id> | open | github | gui
```

### Add a shortcut

```bash
jshortcuts add
```

```
  -- Add New Shortcut -------------------

  Existing categories: Navigation, Terminal, Browser, System

  Category (e.g. Terminal, Browser): VS Code
  Keys (e.g. Ctrl + T): Ctrl + P
  Description: Quick file open
  Notes (optional): Type filename to jump to it

  OK  Shortcut #13 added.
```

### Edit a shortcut

```bash
jshortcuts edit 4
```

```
  -- Edit Shortcut #4 ------------------
  (Press Enter to keep the current value)

  Category [Terminal]:
  Keys [Ctrl + Alt + T]:
  Description [Open Terminal]: Open Gnome Terminal
  Notes [Default Ubuntu terminal shortcut]:

  OK  Shortcut #4 updated.
```

### Delete a shortcut

```bash
jshortcuts del 4
```

```
  Delete: [4] Ctrl + Alt + T -- Open Gnome Terminal
  Are you sure? (y/N): y

  OK  Shortcut #4 deleted.
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
jshortcuts search "new tab"
```

### Open data file

```bash
jshortcuts open
```

Opens `~/.jshortcuts.json` in your default editor (gedit, nano, etc).

---

## GUI Usage

```bash
jshortcuts gui
# or:
python3 ~/bin/jshortcuts-gui.py
# or: search "jshortcuts" in the Ubuntu app menu (Super key)
```

### Four tabs

**Shortcuts tab** -- your main view with:
- Category sidebar on the left (click to filter)
- Colour-coded shortcut list with category grouping
- + Add / Edit / Delete buttons in the toolbar
- Real-time search box in the top bar
- "Open File" button -- opens the JSON in your editor
- "GitHub" button -- push/pull your shortcuts to/from GitHub

**Apps tab** -- application-specific shortcuts:
- Sidebar with your configured applications
- Custom lists of shortcuts scoped specifically to those apps

**All My Apps tab** -- your personal app directory:
- Keep track of apps you use, their purpose, repo links, and YouTube tutorials
- Add dynamic custom tags for metadata

**CLI Reference tab** -- a built-in reference showing every jshortcuts command with description and usage notes. No need to open the terminal to look up commands.

### Row selection

- **Single click** -- selects a row (highlighted blue with a bright left border)
- **Double click** -- opens the Edit dialog immediately
- **Edit button** -- edits the currently selected row
- **Delete button** -- deletes the currently selected row

### Ctrl+C from terminal

If you launched the GUI from a terminal with `jshortcuts gui`, pressing Ctrl+C in that terminal will close the GUI window cleanly.

---

## GitHub Sync

You can push your `~/.jshortcuts.json` to a personal GitHub repository so it is backed up and accessible from other machines.

### In the CLI

```bash
jshortcuts github push
jshortcuts github pull
```

You will be prompted for your repo URL and a commit message if pushing. The tool will:
1. Copy your shortcuts file to `~/.jshortcuts-sync/`
2. Run `git init` and set the remote (first time only)
3. Commit and push to GitHub, OR fetch and forcefully `git reset --hard` to overwrite local conflicts when pulling.

### In the GUI

Click the **GitHub** button in the top-right corner of the window. Enter your repo URL and commit message, then click Push.

### Requirements

```bash
# Install git if not already installed:
sudo apt install git

# For HTTPS repos you need a GitHub Personal Access Token (PAT):
# 1. Go to https://github.com/settings/tokens
# 2. Generate a new token with repo scope
# 3. Use it as your password when git prompts for credentials

# Or use SSH (no password prompts after setup):
# https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

### Sync directory

All git operations happen in `~/.jshortcuts-sync/`. Your original data file `~/.jshortcuts.json` is never moved.

---

## Launch via Ubuntu Custom Shortcut

You can assign a keyboard shortcut (for example `Ctrl+Alt+J`) to open the jshortcuts GUI from anywhere on your desktop — just like how `Ctrl+Alt+T` opens the terminal.

**Step-by-step:**

**Step 1 -- Open Settings**

Press the Super key, type "Settings", and open the Settings app.

**Step 2 -- Go to Keyboard Shortcuts**

In Settings, click **Keyboard** in the left panel.
Then click **View and Customize Shortcuts** (or just **Keyboard Shortcuts** depending on your Ubuntu version).

**Step 3 -- Scroll to the bottom and click Custom Shortcuts**

Scroll all the way down to find **Custom Shortcuts**, then click the **+** button to add a new one.

**Step 4 -- Fill in the details**

A dialog will appear asking for three things:

| Field | What to enter |
|---|---|
| Name | `jshortcuts` |
| Command | `/home/YOUR_USERNAME/bin/jshortcuts-gui.py` |
| Shortcut | (leave blank for now, set in next step) |

Replace `YOUR_USERNAME` with your actual Ubuntu username. To find it, open a terminal and run:

```bash
whoami
```

So if your username is `jbtechnix`, the command would be:

```
/home/jbtechnix/bin/jshortcuts-gui.py
```

Click **Add** to save the entry.

**Step 5 -- Assign the keyboard shortcut**

The new entry will appear in the list. Click on it to expand it, then click the shortcut field (it will say "Disabled").

Press the key combination you want -- for example hold `Ctrl`, hold `Alt`, then press `J`. Ubuntu will capture it and show `Ctrl+Alt+J`.

Click **Set** to confirm.

**Step 6 -- Test it**

Close Settings. Press your chosen shortcut (`Ctrl+Alt+J` or whatever you picked).

The jshortcuts GUI window should open immediately.

**Alternative command using the CLI wrapper:**

If the direct path does not work, use the full python3 call:

```
python3 /home/YOUR_USERNAME/bin/jshortcuts-gui.py
```

Or using the CLI tool:

```
/home/YOUR_USERNAME/bin/jshortcuts gui
```

**Note:** If you get a "command not found" or nothing happens, make sure the script is executable:

```bash
chmod +x ~/bin/jshortcuts-gui.py
```

---

## Data File Format

All shortcuts live in `~/.jshortcuts.json`. Edit this file directly in any text editor -- both CLI and GUI pick up changes on the next run.

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

| Field | Required | Description |
|---|---|---|
| `id` | auto | Unique integer, never reused |
| `category` | yes | Group label (Navigation, Terminal, Browser, etc.) |
| `keys` | yes | Key combination, e.g. `Ctrl + Shift + P` |
| `description` | yes | What the shortcut does |
| `notes` | no | Extra info or context |

---

## Examples

### Build a VS Code shortcut set

```bash
jshortcuts add   # Category: VS Code | Keys: Ctrl + P        | Description: Quick file open
jshortcuts add   # Category: VS Code | Keys: Ctrl + Shift + P | Description: Command palette
jshortcuts add   # Category: VS Code | Keys: Ctrl + `         | Description: Toggle terminal
jshortcuts add   # Category: VS Code | Keys: Ctrl + B         | Description: Toggle sidebar
```

Then view just VS Code shortcuts:

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

### Reset to the bundled defaults

```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

---

## Uninstall

```bash
bash uninstall.sh
```

The uninstaller removes the scripts and desktop launcher. Your `~/.jshortcuts.json` data file is **kept by default** and the script will ask whether you want to delete it too.

To also remove the PATH line added to your shell config:

```bash
nano ~/.bashrc
# Remove the two lines that contain "jshortcuts"
```

---

## Troubleshooting

### `jshortcuts: command not found`

The current terminal needs refreshing after install:

```bash
source ~/.bashrc
```

New terminal windows work automatically without this step.

### GUI does not open

```bash
python3 -c "import tkinter; print('OK')"
# If that fails:
sudo apt install python3-tk
```

### Font looks different or plain

Install JetBrains Mono for the intended look:

```bash
sudo apt install fonts-jetbrains-mono
```

Log out and back in for fonts to take effect.

### Data file is empty or missing

```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

### GitHub push fails

- Check that `git` is installed: `git --version`
- Verify your repo URL is correct (copy it from GitHub)
- For HTTPS repos: use a Personal Access Token as your password
- For SSH repos: make sure your SSH key is added to GitHub

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "feat: add my feature"`
4. Push and open a Pull Request against `main`

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## License

MIT (c) 2026 [Jbtechnix - Mr. Humble Beginnings](https://github.com/johnboscocjt)
See [LICENSE](LICENSE) for full text.
