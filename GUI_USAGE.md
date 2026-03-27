# GUI Usage Guide — jshortcuts

`jshortcuts-gui.py` is the popup window companion to the CLI tool.  
Both tools share the same `~/.jshortcuts.json` data file.

---

## Launching the GUI

**Via the CLI companion:**
```bash
jshortcuts gui
```

**Directly:**
```bash
python3 ~/bin/jshortcuts-gui.py
```

**From the app menu:**  
After running `install.sh`, search for **jshortcuts** in the Ubuntu app launcher (Super key → type "jshortcuts").

---

## Window layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ ⌨  jshortcuts     my keyboard shortcuts         [⌕ search...     ] │
├──────────────┬──────────────────────────────────────────────────────┤
│ CATEGORIES   │  12 shortcut(s)          [+ Add]  [✎ Edit] [✕ Delete]│
│              ├──────────────────────────────────────────────────────┤
│  All         │  ▸ NAVIGATION                                        │
│  Navigation  │   [1]  Super + D              Show / Hide Desktop    │
│  Terminal    │   [2]  Super + Left / Right   Snap window to half    │
│  Browser     │   [3]  Super + Up             Maximise window        │
│  System      │                                                      │
│              │  ▸ TERMINAL                                          │
│              │   [4]  Ctrl + Alt + T         Open Terminal          │
│              │         Default Ubuntu terminal shortcut             │
│              │   [5]  Ctrl + Shift + C       Copy in Terminal       │
│              │                                                      │
├──────────────┴──────────────────────────────────────────────────────┤
│  data: /home/yourname/.jshortcuts.json                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Features

### Category sidebar (left panel)

- Lists all unique categories in your data
- Click **All** to show everything
- Click any category name to filter the list
- Currently selected category is highlighted
- Each category has its own colour, matching the list

### Shortcut list (right panel)

Each row shows:
- **ID** (grey chip on the left)
- **Keys** (coloured badge matching the category)
- **Description** (main white text)
- **Notes** (grey subtext, if present)

### Search box (top right)

Type to filter shortcuts in real-time across:
- Keys
- Description
- Notes
- Category

The count updates as you type.

---

## Actions

### Add a shortcut

1. Click **+ Add**
2. Fill in the dialog:
   - **Category** — type a new one or choose from the dropdown
   - **Keys** — e.g. `Ctrl + Shift + P`
   - **Description** — what it does
   - **Notes** — optional extra info
3. Click **Save** (or press Enter)

### Edit a shortcut

**Option 1:** Single-click a row to select it, then click **✎ Edit**  
**Option 2:** Double-click any row directly

The edit dialog shows current values pre-filled. Press Enter on any field to keep it unchanged.

### Delete a shortcut

1. Single-click a row to select it (it highlights)
2. Click **✕ Delete**
3. Confirm in the prompt

### Scroll

- Mouse wheel / trackpad scroll
- Click and drag the scrollbar

---

## Keyboard shortcuts (in the GUI)

| Key | Action |
|---|---|
| `Enter` | Save (in Add/Edit dialog) |
| `Escape` | Cancel / close dialog |

---

## Add/Edit dialog

```
┌─────────────────────────────────────────┐
│ ⌨  Add Shortcut                        │
├─────────────────────────────────────────┤
│  Category                               │
│  [ Terminal               ▼ ]           │
│                                         │
│  Keys (e.g. Ctrl + T)                  │
│  [ Ctrl + Alt + T                    ]  │
│                                         │
│  Description                            │
│  [ Open Terminal                      ] │
│                                         │
│  Notes (optional)                       │
│  [ Default Ubuntu terminal shortcut   ] │
│                                         │
│                    [Cancel]  [  Save  ] │
└─────────────────────────────────────────┘
```

The Category field is a combo box — it lists your existing categories so you can pick one, or type a new name to create a new category.

---

## Tips

- Changes made in the GUI are immediately saved to `~/.jshortcuts.json`
- If you edit the file in a text editor, relaunch the GUI (or the CLI) to see changes
- The GUI and CLI always show the same data — they share one file
- Window size is resizable; minimum size is 600 × 400

---

## Troubleshooting

**GUI won't launch:**
```bash
# Check tkinter is installed
python3 -c "import tkinter; print('OK')"
# Install if missing
sudo apt install python3-tk
```

**Font looks plain / monospaced missing:**
```bash
sudo apt install fonts-jetbrains-mono
```
Then log out and back in for font changes to apply.
