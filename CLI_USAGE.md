# CLI Usage Guide — jshortcuts

The `jshortcuts` command-line tool lets you view, add, edit, delete, and search your personal keyboard shortcuts from any terminal.

---

## Installation

Follow the steps in the [main README](../README.md#installation).  
After install, verify it works:

```bash
jshortcuts help
```

---

## Command reference

### `jshortcuts` — List all shortcuts

```bash
jshortcuts
```

Displays all shortcuts grouped by category with colour coding:

```
──────────── ⌨  jshortcuts — My Keyboard Shortcuts ────────────────

  ▸ Navigation

    [  1]  Super + D                     Show / Hide Desktop
    [  2]  Super + Left / Right          Snap window to half screen

  ▸ Terminal

    [  3]  Ctrl + Alt + T                Open Terminal
                                          ↳ Default Ubuntu terminal shortcut
    [  4]  Ctrl + Shift + C              Copy in Terminal

  ▸ Browser

    [  7]  Ctrl + T                      New Tab
    [  8]  Ctrl + Shift + T              Reopen closed Tab

────────────────────────────────────────────────────────────────────
  4 shortcut(s)  │  data: /home/user/.jshortcuts.json
  jshortcuts add | edit <id> | del <id> | open | github | gui
```

---

### `jshortcuts add` — Add a new shortcut

```bash
jshortcuts add
```

Interactive prompts guide you through creating a new entry:

```
  ── Add New Shortcut ──────────────────

  Existing categories: Navigation, Terminal, Browser

  Category (e.g. Terminal, Browser): VS Code
  Keys (e.g. Ctrl + T): Ctrl + `
  Description: Toggle integrated terminal
  Notes (optional): Also works in most editors

  ✓ Shortcut #13 added.
```

**Tips:**
- Type an existing category name to add to it, or type a new one to create it.
- Notes are optional — press Enter to skip.
- The ID is assigned automatically and never reused.

---

### `jshortcuts edit <id>` — Edit a shortcut

```bash
jshortcuts edit 3
```

Shows current values in brackets. Press Enter to keep them:

```
  ── Edit Shortcut #3 ─────────────────
  (Press Enter to keep current value)

  Category [Terminal]:
  Keys [Ctrl + Alt + T]: Ctrl + Alt + T
  Description [Open Terminal]: Open Gnome Terminal
  Notes [Default Ubuntu terminal shortcut]:

  ✓ Shortcut #3 updated.
```

---

### `jshortcuts del <id>` — Delete a shortcut

```bash
jshortcuts del 7
```

Asks for confirmation before deleting:

```
  Delete: [7] Ctrl + T — New Tab
  Are you sure? (y/N): y

  ✓ Shortcut #7 deleted.
```

Aliases: `del`, `delete`, `rm` — all work the same.

---

### `jshortcuts cat <category>` — Filter by category

```bash
jshortcuts cat Terminal
jshortcuts cat Browser
jshortcuts cat "VS Code"
```

Shows only shortcuts in the specified category (case-insensitive):

```
──────────── ⌨  jshortcuts — My Keyboard Shortcuts ────────────────

  ▸ Terminal

    [  3]  Ctrl + Alt + T                Open Terminal
    [  4]  Ctrl + Shift + C              Copy in Terminal
    [  5]  Ctrl + Shift + V              Paste in Terminal

────────────────────────────────────────────────────────────────────
  3 shortcut(s)
```

---

### `jshortcuts search <query>` — Search shortcuts

```bash
jshortcuts search ctrl
jshortcuts search terminal
jshortcuts search snap
jshortcuts search "new tab"
```

Searches across keys, description, notes, and category (case-insensitive):

```bash
jshortcuts search tab
```

```
  ▸ Browser

    [  7]  Ctrl + T                      New Tab
    [  8]  Ctrl + Shift + T              Reopen closed Tab
```

---

### `jshortcuts open` — Open data file

```bash
jshortcuts open
```

Opens `~/.jshortcuts.json` in your default terminal or graphical editor (e.g. VS Code, gedit, nano).

---

### `jshortcuts github <push/pull>` — Sync with GitHub

```bash
jshortcuts github push
jshortcuts github pull
```

- **`push`**: Commits your `~/.jshortcuts.json` and pushes it to your remote GitHub repository.
- **`pull`**: Performs a `fetch` and a forced `reset --hard` to instantly update your local shortcuts to perfectly match whatever is on GitHub, resolving any conflicts automatically.

---

### `jshortcuts gui` — Open the GUI window

```bash
jshortcuts gui
```

Launches `jshortcuts-gui.py` from the same directory as the CLI.  
Requires Python `tkinter` to be installed.

---

### `jshortcuts help` — Show help

```bash
jshortcuts help
jshortcuts --help
jshortcuts -h
```

---

## Data file

All shortcuts are stored in `~/.jshortcuts.json`.  
Both the CLI and GUI read and write the same file.  
You can edit it directly in any text editor.

**Schema:**

```json
{
  "shortcuts": [
    {
      "id": 1,
      "category": "Terminal",
      "keys": "Ctrl + Alt + T",
      "description": "Open Terminal",
      "notes": "Default Ubuntu shortcut"
    }
  ],
  "next_id": 2
}
```

---

## Tips and tricks

**Backup your shortcuts:**
```bash
cp ~/.jshortcuts.json ~/Desktop/shortcuts_backup.json
```

**Restore from backup:**
```bash
cp ~/Desktop/shortcuts_backup.json ~/.jshortcuts.json
```

**Reset to defaults:**
```bash
cp ~/bin/jshortcuts_default.json ~/.jshortcuts.json
```

**Pipe output (no colour):**
```bash
jshortcuts > shortcuts.txt
```

**Use in a script:**
```bash
# Count your shortcuts
python3 -c "import json; d=json.load(open('$HOME/.jshortcuts.json')); print(len(d['shortcuts']))"
```
