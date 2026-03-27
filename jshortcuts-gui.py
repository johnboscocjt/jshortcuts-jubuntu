#!/usr/bin/env python3
"""
jshortcuts-gui -- Dark popup GUI for managing personal keyboard shortcuts.
Reads/writes the same ~/.jshortcuts.json as the CLI tool.

Features:
  - Two tabs: Shortcuts view + CLI Reference
  - Add / Edit / Delete shortcuts
  - Open data file in default editor
  - Push shortcuts to GitHub
  - Ctrl+C from terminal closes the window cleanly
  - Clear row selection highlight

Launch:
  python3 jshortcuts-gui.py
  jshortcuts gui
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# ── Make Ctrl+C from terminal close the window ────────────────────────────────
signal.signal(signal.SIGINT, signal.SIG_DFL)

# ── Colour palette ────────────────────────────────────────────────────────────
BG        = "#0f1117"
BG2       = "#161b27"
BG3       = "#1e2436"
BG_SEL    = "#1a2d50"   # selected row background (distinct blue tint)
ACCENT    = "#5b8af5"
ACCENT2   = "#3d6ae0"
FG        = "#e2e8f0"
FG_DIM    = "#6b7a99"
SUCCESS   = "#48bb78"
DANGER    = "#fc5c65"
WARNING   = "#f6ad55"
SEL_BORDER= "#5b8af5"   # left border of selected row

CAT_COLORS = ["#5b8af5", "#f6ad55", "#48bb78", "#fc5c65", "#b794f4", "#4fd1c5"]

FONT_TITLE = ("JetBrains Mono", 14, "bold")
FONT_BOLD  = ("JetBrains Mono", 10, "bold")
FONT_BODY  = ("JetBrains Mono", 10)
FONT_SMALL = ("JetBrains Mono", 9)
FONT_MONO  = ("JetBrains Mono", 9)

DATA_FILE   = os.path.expanduser("~/.jshortcuts.json")
CONFIG_FILE = os.path.expanduser("~/.jshortcuts_github.json")
DEFAULT_DATA = {"shortcuts": [], "next_id": 1}


# ── Data helpers ──────────────────────────────────────────────────────────────

def load_data():
    if not os.path.exists(DATA_FILE):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        default = os.path.join(script_dir, "jshortcuts_default.json")
        if os.path.exists(default):
            shutil.copy(default, DATA_FILE)
        else:
            save_data(DEFAULT_DATA)
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def load_github_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {}


def save_github_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ── Common widget helpers ─────────────────────────────────────────────────────

def make_button(parent, text, cmd, bg=ACCENT, fg="white", **kwargs):
    return tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, font=FONT_SMALL,
        relief="flat", padx=11, pady=5, cursor="hand2",
        activebackground=BG3, activeforeground=FG,
        **kwargs
    )


# ── Add / Edit dialog ─────────────────────────────────────────────────────────

class ShortcutDialog(tk.Toplevel):
    """
    Modal dialog to add or edit a shortcut.
    Button bar is packed BEFORE the form (side=bottom) so it is always visible
    regardless of how large the form content grows.
    """

    def __init__(self, parent, title, categories, shortcut=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        W, H = 530, 470
        self.geometry(f"{W}x{H}")
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry(f"{W}x{H}+{px}+{py}")

        self._build(categories, shortcut or {})

    def _label(self, parent, text):
        tk.Label(parent, text=text, bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(12, 3))

    def _entry_row(self, parent, value=""):
        var = tk.StringVar(value=value)
        tk.Entry(
            parent, textvariable=var,
            bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
            insertbackground=ACCENT,
            highlightthickness=1,
            highlightbackground=BG3,
            highlightcolor=ACCENT,
        ).pack(fill="x", ipady=7)
        return var

    def _build(self, categories, s):
        # 1. Header (top, fixed height)
        hdr = tk.Frame(self, bg=ACCENT2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  {self.title()}",
                 bg=ACCENT2, fg="white", font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        # 2. Button bar (bottom, fixed height) -- MUST be packed before form
        #    Tkinter allocates space bottom-up for side=bottom widgets first,
        #    so the button bar is guaranteed to be visible even if form is large.
        btn_bar = tk.Frame(self, bg=BG, height=64)
        btn_bar.pack(side="bottom", fill="x")
        btn_bar.pack_propagate(False)

        make_button(btn_bar, "  Cancel  ", self.destroy,
                    bg=BG3, fg=FG_DIM).pack(side="right", padx=(6, 18), pady=14)
        make_button(btn_bar, "  Save  ", self._save,
                    bg=ACCENT, fg="white").pack(side="right", pady=14)

        # 3. Divider line
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # 4. Form (fills remaining space between header and button bar)
        form = tk.Frame(self, bg=BG2, padx=26, pady=6)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        self._label(form, "Category  (pick existing or type a new one)")
        self.cat_var = tk.StringVar(value=s.get("category", ""))
        combo = ttk.Combobox(form, textvariable=self.cat_var,
                             values=categories, font=FONT_BODY)
        combo.pack(fill="x", ipady=5)
        self._style_combo()

        self._label(form, "Keys  (e.g.  Ctrl + T   |   Super + D)")
        self.keys_var = self._entry_row(form, s.get("keys", ""))

        self._label(form, "Description  (what does this shortcut do?)")
        self.desc_var = self._entry_row(form, s.get("description", ""))

        self._label(form, "Notes  (optional extra info)")
        self.notes_var = self._entry_row(form, s.get("notes", ""))

        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _style_combo(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("TCombobox",
                    fieldbackground=BG3, background=BG3,
                    foreground=FG, selectbackground=ACCENT,
                    selectforeground="white",
                    arrowcolor=FG_DIM, bordercolor=BG3,
                    lightcolor=BG3, darkcolor=BG3)

    def _save(self):
        cat   = self.cat_var.get().strip()
        keys  = self.keys_var.get().strip()
        desc  = self.desc_var.get().strip()
        notes = self.notes_var.get().strip()
        if not cat or not keys or not desc:
            messagebox.showwarning(
                "Missing Fields",
                "Category, Keys, and Description are required.",
                parent=self)
            return
        self.result = {"category": cat, "keys": keys,
                       "description": desc, "notes": notes}
        self.destroy()


# ── GitHub dialog ─────────────────────────────────────────────────────────────

class GitHubDialog(tk.Toplevel):
    """Dialog to configure and push shortcuts to a GitHub repo."""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("GitHub Sync")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        W, H = 540, 360
        self.geometry(f"{W}x{H}")
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry(f"{W}x{H}+{px}+{py}")

        self._build()

    def _build(self):
        cfg = load_github_config()

        # Header
        hdr = tk.Frame(self, bg=ACCENT2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  Push Shortcuts to GitHub",
                 bg=ACCENT2, fg="white", font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        # Button bar (bottom, packed before form)
        btn_bar = tk.Frame(self, bg=BG, height=64)
        btn_bar.pack(side="bottom", fill="x")
        btn_bar.pack_propagate(False)
        make_button(btn_bar, "  Cancel  ", self.destroy,
                    bg=BG3, fg=FG_DIM).pack(side="right", padx=(6, 18), pady=14)
        make_button(btn_bar, "  Push  ", self._do_push,
                    bg=SUCCESS, fg="white").pack(side="right", pady=14)

        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # Form
        form = tk.Frame(self, bg=BG2, padx=26, pady=12)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        tk.Label(form, text="GitHub Repository URL (HTTPS or SSH)",
                 bg=BG2, fg=FG_DIM, font=FONT_SMALL, anchor="w"
                 ).pack(fill="x", pady=(4, 3))
        self.url_var = tk.StringVar(value=cfg.get("repo_url", ""))
        tk.Entry(form, textvariable=self.url_var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT
                 ).pack(fill="x", ipady=7)

        tk.Label(form,
                 text="Example: https://github.com/yourname/my-shortcuts.git",
                 bg=BG2, fg=FG_DIM, font=FONT_MONO, anchor="w"
                 ).pack(fill="x", pady=(3, 16))

        tk.Label(form, text="Commit Message",
                 bg=BG2, fg=FG_DIM, font=FONT_SMALL, anchor="w"
                 ).pack(fill="x", pady=(0, 3))
        self.msg_var = tk.StringVar(value="Update shortcuts")
        tk.Entry(form, textvariable=self.msg_var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT
                 ).pack(fill="x", ipady=7)

        # Status area
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(form, textvariable=self.status_var,
                                   bg=BG2, fg=SUCCESS, font=FONT_SMALL,
                                   anchor="w", wraplength=460, justify="left")
        self.status_lbl.pack(fill="x", pady=(14, 0))

        self.bind("<Return>", lambda _: self._do_push())
        self.bind("<Escape>", lambda _: self.destroy())

    def _do_push(self):
        if not shutil.which("git"):
            messagebox.showerror("git not found",
                "git is not installed.\nInstall it with:\n  sudo apt install git",
                parent=self)
            return

        url = self.url_var.get().strip()
        msg = self.msg_var.get().strip() or "Update shortcuts"
        if not url:
            messagebox.showwarning("URL required",
                "Please enter your GitHub repo URL.", parent=self)
            return

        cfg = load_github_config()
        cfg["repo_url"] = url
        save_github_config(cfg)

        self.status_var.set("Working...")
        self.status_lbl.config(fg=WARNING)
        self.update()

        sync_dir = os.path.expanduser("~/.jshortcuts-sync")
        os.makedirs(sync_dir, exist_ok=True)
        shutil.copy(DATA_FILE, os.path.join(sync_dir, "jshortcuts.json"))

        readme_path = os.path.join(sync_dir, "README.md")
        if not os.path.exists(readme_path):
            with open(readme_path, "w") as rf:
                rf.write("# My jshortcuts\n\nPersonal keyboard shortcuts managed by "
                         "[jshortcuts-jubuntu](https://github.com/johnboscocjt/jshortcuts-jubuntu).\n")
        try:
            env = os.environ.copy()
            git_dir = os.path.join(sync_dir, ".git")

            if not os.path.isdir(git_dir):
                subprocess.check_call(["git", "init"], cwd=sync_dir, env=env,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.check_call(["git", "remote", "add", "origin", url],
                                      cwd=sync_dir, env=env,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                try:
                    subprocess.check_call(["git", "remote", "set-url", "origin", url],
                                          cwd=sync_dir, env=env,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except subprocess.CalledProcessError:
                    subprocess.check_call(["git", "remote", "add", "origin", url],
                                          cwd=sync_dir, env=env,
                                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            subprocess.check_call(["git", "add", "."], cwd=sync_dir, env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            diff = subprocess.run(["git", "diff", "--cached", "--quiet"],
                                  cwd=sync_dir, env=env)
            if diff.returncode == 0:
                self.status_var.set("Nothing changed since last push.")
                self.status_lbl.config(fg=FG_DIM)
                return

            subprocess.check_call(["git", "commit", "-m", msg],
                                   cwd=sync_dir, env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                subprocess.check_call(["git", "push", "-u", "origin", "main"],
                                       cwd=sync_dir, env=env)
            except subprocess.CalledProcessError:
                subprocess.check_call(["git", "push", "-u", "origin", "master"],
                                       cwd=sync_dir, env=env)

            self.status_var.set(f"Pushed successfully to:\n{url}")
            self.status_lbl.config(fg=SUCCESS)

        except subprocess.CalledProcessError as e:
            self.status_var.set(
                f"Push failed: {e}\n"
                "Check your repo URL and that you have push access.\n"
                "For HTTPS, you may need a GitHub Personal Access Token.")
            self.status_lbl.config(fg=DANGER)


# ── Main application window ───────────────────────────────────────────────────

class JShortcutsApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("jshortcuts")
        self.configure(bg=BG)
        self.geometry("900x620")
        self.minsize(640, 440)

        self._cat_color_map = {}
        self._selected_id   = None
        self._rows          = {}
        self._search_var    = tk.StringVar()
        self._selected_cat  = tk.StringVar(value="All")
        self._search_var.trace_add("write", lambda *_: self._refresh())

        self._build_ui()
        self._refresh()

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"900x620+{(sw - 900)//2}+{(sh - 620)//2}")

        # Let Ctrl+C from the terminal propagate cleanly (already set globally)
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # ── Top-level layout ──────────────────────────────────────────────────────

    def _build_ui(self):
        self._style_ttk()

        # Status bar (packed first so always visible at bottom)
        status = tk.Frame(self, bg=BG2, height=28)
        status.pack(side="bottom", fill="x")
        status.pack_propagate(False)
        tk.Label(status, text=f"  data: {DATA_FILE}",
                 bg=BG2, fg=FG_DIM, font=("JetBrains Mono", 8), anchor="w"
                 ).pack(side="left", pady=6)

        # Top bar
        topbar = tk.Frame(self, bg=BG2, height=56)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="jshortcuts", bg=BG2, fg=FG,
                 font=FONT_TITLE).pack(side="left", padx=(16, 0), pady=10)
        tk.Label(topbar, text="  my keyboard shortcuts", bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", pady=14)

        # Top-bar action buttons (right side)
        make_button(topbar, " Open File", self._open_file,
                    bg=BG3, fg=FG_DIM).pack(side="right", padx=(4, 12), pady=12)
        make_button(topbar, " GitHub", self._github_dialog,
                    bg=BG3, fg=FG_DIM).pack(side="right", padx=4, pady=12)

        # Search box
        sf = tk.Frame(topbar, bg=BG3, padx=8, pady=4)
        sf.pack(side="right", padx=8, pady=10)
        tk.Label(sf, text="search:", bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left")
        tk.Entry(sf, textvariable=self._search_var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 width=20, insertbackground=ACCENT
                 ).pack(side="left", padx=(4, 0))

        # Notebook (tabs)
        self._notebook = ttk.Notebook(self, style="Dark.TNotebook")
        self._notebook.pack(side="top", fill="both", expand=True)

        # Tab 1: Shortcuts
        self._shortcuts_tab = tk.Frame(self._notebook, bg=BG)
        self._notebook.add(self._shortcuts_tab, text="  Shortcuts  ")
        self._build_shortcuts_tab()

        # Tab 2: CLI Reference
        cli_tab = tk.Frame(self._notebook, bg=BG)
        self._notebook.add(cli_tab, text="  CLI Reference  ")
        self._build_cli_tab(cli_tab)

    def _style_ttk(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dark.TNotebook",
                    background=BG2, borderwidth=0,
                    tabmargins=[0, 0, 0, 0])
        s.configure("Dark.TNotebook.Tab",
                    background=BG2, foreground=FG_DIM,
                    padding=[16, 8], font=FONT_BODY,
                    borderwidth=0)
        s.map("Dark.TNotebook.Tab",
              background=[("selected", BG), ("active", BG3)],
              foreground=[("selected", FG), ("active", FG)])

    # ── Tab 1: Shortcuts ──────────────────────────────────────────────────────

    def _build_shortcuts_tab(self):
        tab = self._shortcuts_tab

        # Sidebar
        sidebar = tk.Frame(tab, bg=BG2, width=170)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="CATEGORIES", bg=BG2, fg=FG_DIM,
                 font=("JetBrains Mono", 8), anchor="w"
                 ).pack(fill="x", padx=12, pady=(16, 8))
        self._cat_frame = tk.Frame(sidebar, bg=BG2)
        self._cat_frame.pack(fill="x")

        # Right pane
        right = tk.Frame(tab, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Toolbar
        toolbar = tk.Frame(right, bg=BG, pady=8, padx=16)
        toolbar.pack(side="top", fill="x")
        self._count_label = tk.Label(toolbar, text="", bg=BG,
                                     fg=FG_DIM, font=FONT_SMALL)
        self._count_label.pack(side="left")
        for text, cmd, color in [
            ("+ Add",    self._add,    SUCCESS),
            ("Edit",     self._edit,   ACCENT),
            ("Delete",   self._delete, DANGER),
        ]:
            make_button(toolbar, text, cmd, bg=color).pack(side="right", padx=4)

        # Hint label
        tk.Label(toolbar, text="click to select  |  double-click to edit",
                 bg=BG, fg=FG_DIM, font=FONT_MONO
                 ).pack(side="right", padx=8)

        # Scrollable list
        canvas_frame = tk.Frame(right, bg=BG)
        canvas_frame.pack(side="top", fill="both", expand=True)
        self._canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(canvas_frame, orient="vertical",
                          command=self._canvas.yview, bg=BG2)
        self._canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._list_frame = tk.Frame(self._canvas, bg=BG)
        self._cw = self._canvas.create_window(
            (0, 0), window=self._list_frame, anchor="nw")
        self._list_frame.bind("<Configure>",
            lambda _: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
            lambda e: self._canvas.itemconfig(self._cw, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self._canvas.bind_all("<Button-4>",
            lambda _: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>",
            lambda _: self._canvas.yview_scroll(1, "units"))

    # ── Tab 2: CLI Reference ──────────────────────────────────────────────────

    def _build_cli_tab(self, tab):
        # Header
        hdr = tk.Frame(tab, bg=BG2, height=44)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  jshortcuts -- CLI Command Reference",
                 bg=BG2, fg=FG, font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=16, pady=12)

        # Scrollable content
        canvas = tk.Canvas(tab, bg=BG, highlightthickness=0)
        sb2 = tk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=BG)
        cw2 = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>",
            lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(cw2, width=e.width))

        # Command data
        COMMANDS = [
            ("jshortcuts",
             "List all shortcuts",
             "Displays all shortcuts grouped by category with colour coding."),
            ("jshortcuts add",
             "Add a new shortcut",
             "Interactive prompts guide you through creating a new entry.\n"
             "You can type a new category or pick from existing ones."),
            ("jshortcuts edit <id>",
             "Edit a shortcut by ID",
             "Shows current values in brackets. Press Enter to keep them.\n"
             "Find IDs by running: jshortcuts"),
            ("jshortcuts del <id>",
             "Delete a shortcut by ID",
             "Asks for confirmation before deleting.\n"
             "Aliases: del  delete  rm"),
            ("jshortcuts cat <name>",
             "Filter by category",
             "Shows only shortcuts in that category (case-insensitive).\n"
             'Use quotes for multi-word categories: jshortcuts cat "VS Code"'),
            ("jshortcuts search <query>",
             "Search shortcuts",
             "Searches keys, description, notes, and category.\n"
             "Example: jshortcuts search terminal"),
            ("jshortcuts open",
             "Open data file in editor",
             f"Opens {DATA_FILE} in your default editor (gedit, nano, etc).\n"
             "Both CLI and GUI pick up changes automatically on next run."),
            ("jshortcuts github",
             "Push shortcuts to GitHub",
             "Asks for your GitHub repo URL and commit message,\n"
             "then pushes your shortcuts file to that repo.\n"
             "Requires: git  (sudo apt install git)"),
            ("jshortcuts gui",
             "Open the GUI window",
             "Launches this graphical interface.\n"
             "Can also be launched from the Ubuntu app menu."),
            ("jshortcuts help",
             "Show help in terminal",
             "Prints a compact command reference to the terminal.\n"
             "Aliases: help  --help  -h"),
        ]

        pad = 28
        for i, (cmd, summary, detail) in enumerate(COMMANDS):
            row = tk.Frame(inner, bg=BG2 if i % 2 == 0 else BG, pady=0)
            row.pack(fill="x", padx=16, pady=(12, 0))

            # Command chip
            chip = tk.Frame(row, bg=BG3)
            chip.pack(side="left", anchor="nw", padx=(0, 16), pady=4)
            tk.Label(chip, text=f"  {cmd}  ", bg=BG3, fg=ACCENT,
                     font=FONT_BOLD, anchor="w").pack(padx=2, pady=4)

            # Text column
            txt = tk.Frame(row, bg=row["bg"])
            txt.pack(side="left", fill="both", expand=True, anchor="nw")
            tk.Label(txt, text=summary, bg=row["bg"], fg=FG,
                     font=FONT_BOLD, anchor="w").pack(fill="x")
            tk.Label(txt, text=detail, bg=row["bg"], fg=FG_DIM,
                     font=FONT_SMALL, anchor="w", justify="left",
                     wraplength=520).pack(fill="x", pady=(2, 0))

        # Data file note
        tk.Frame(inner, bg=BG3, height=1).pack(fill="x", padx=16, pady=20)
        note = tk.Frame(inner, bg=BG)
        note.pack(fill="x", padx=16, pady=(0, 20))
        tk.Label(note, text="Data file:", bg=BG, fg=FG_DIM,
                 font=FONT_BOLD).pack(side="left")
        tk.Label(note, text=f"  {DATA_FILE}", bg=BG, fg=ACCENT,
                 font=FONT_MONO).pack(side="left")
        tk.Label(note,
                 text="  (shared between CLI and GUI -- edit either, both stay in sync)",
                 bg=BG, fg=FG_DIM, font=FONT_SMALL).pack(side="left")

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, categories):
        for w in self._cat_frame.winfo_children():
            w.destroy()
        for cat in ["All"] + categories:
            selected = (self._selected_cat.get() == cat)
            color = self._cat_color_map.get(cat, ACCENT) if cat != "All" else ACCENT
            bg = BG3 if selected else BG2
            fg = color if selected else FG_DIM
            btn = tk.Button(
                self._cat_frame, text=f"  {cat}",
                command=lambda c=cat: self._select_cat(c),
                bg=bg, fg=fg, font=FONT_SMALL,
                relief="flat", anchor="w", padx=8, pady=6,
                cursor="hand2",
                activebackground=BG3, activeforeground=FG)
            btn.pack(fill="x")
            if selected:
                # Left accent bar for selected category
                tk.Frame(self._cat_frame, bg=color, height=2
                         ).pack(fill="x", padx=12)

    def _select_cat(self, cat):
        self._selected_cat.set(cat)
        self._refresh()

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh(self):
        data = load_data()
        shortcuts = data["shortcuts"]
        cats = []
        for s in shortcuts:
            if s["category"] not in cats:
                cats.append(s["category"])
        for i, cat in enumerate(cats):
            self._cat_color_map[cat] = CAT_COLORS[i % len(CAT_COLORS)]

        self._build_sidebar(cats)

        sel_cat = self._selected_cat.get()
        query   = self._search_var.get().strip().lower()
        filtered = shortcuts
        if sel_cat != "All":
            filtered = [s for s in filtered if s["category"] == sel_cat]
        if query:
            filtered = [s for s in filtered if
                        query in s["keys"].lower()
                        or query in s["description"].lower()
                        or query in s.get("notes", "").lower()
                        or query in s["category"].lower()]

        self._count_label.config(text=f"{len(filtered)} shortcut(s)")
        self._render_list(filtered)

    # ── Render list ───────────────────────────────────────────────────────────

    def _render_list(self, shortcuts):
        for w in self._list_frame.winfo_children():
            w.destroy()
        self._selected_id = None
        self._rows = {}

        if not shortcuts:
            tk.Label(self._list_frame,
                     text="\n  No shortcuts found.\n  Click '+ Add' to create one.",
                     bg=BG, fg=FG_DIM, font=FONT_BODY,
                     justify="left").pack(padx=24, pady=40)
            return

        grouped = {}
        for s in shortcuts:
            grouped.setdefault(s["category"], []).append(s)

        for cat, items in grouped.items():
            color = self._cat_color_map.get(cat, ACCENT)
            hdr = tk.Frame(self._list_frame, bg=BG)
            hdr.pack(fill="x", padx=16, pady=(16, 6))
            tk.Frame(hdr, bg=color, width=4, height=18).pack(side="left")
            tk.Label(hdr, text=f"  {cat.upper()}", bg=BG, fg=color,
                     font=("JetBrains Mono", 9, "bold")).pack(side="left")
            for s in items:
                self._make_row(s, color)

    def _make_row(self, s, cat_color):
        sid = s["id"]
        is_selected = (self._selected_id == sid)

        # Outer container — changes BG on select/hover
        row = tk.Frame(self._list_frame,
                       bg=BG_SEL if is_selected else BG2,
                       cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)

        # Left accent bar: bright accent when selected, dim otherwise
        left_bar_color = SEL_BORDER if is_selected else BG3
        left_bar = tk.Frame(row, bg=left_bar_color, width=4)
        left_bar.pack(side="left", fill="y")

        # ID chip
        tk.Label(row, text=f" {sid} ", bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(6, 0), pady=10)

        # Keys badge
        keys_lbl = tk.Label(row, text=f"  {s['keys']}  ",
                            bg=BG3, fg=cat_color, font=FONT_BOLD, padx=4)
        keys_lbl.pack(side="left", padx=8, pady=10)

        # Description + notes
        text_frame = tk.Frame(row, bg=row["bg"])
        text_frame.pack(side="left", fill="both", expand=True, pady=8)
        tk.Label(text_frame, text=s["description"],
                 bg=row["bg"], fg=FG, font=FONT_BODY, anchor="w").pack(fill="x")
        if s.get("notes"):
            tk.Label(text_frame, text=s["notes"],
                     bg=row["bg"], fg=FG_DIM, font=FONT_SMALL, anchor="w").pack(fill="x")

        def on_click(_, i=sid):
            self._select_row(i)

        def on_double(_, i=sid):
            self._edit_id(i)

        def on_enter(_, r=row, lb=left_bar, tf=text_frame, i=sid):
            if self._selected_id != i:
                r.config(bg=BG3)
                tf.config(bg=BG3)

        def on_leave(_, r=row, lb=left_bar, tf=text_frame, i=sid):
            if self._selected_id == i:
                r.config(bg=BG_SEL)
                lb.config(bg=SEL_BORDER)
                tf.config(bg=BG_SEL)
            else:
                r.config(bg=BG2)
                lb.config(bg=BG3)
                tf.config(bg=BG2)

        for widget in (row, keys_lbl, text_frame):
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-1>", on_double)
            widget.bind("<Enter>",    on_enter)
            widget.bind("<Leave>",    on_leave)

        self._rows[sid] = (row, left_bar, text_frame)

    def _select_row(self, sid):
        # Deselect previously selected row
        if self._selected_id and self._selected_id in self._rows:
            old_row, old_bar, old_tf = self._rows[self._selected_id]
            old_row.config(bg=BG2)
            old_bar.config(bg=BG3)
            old_tf.config(bg=BG2)

        self._selected_id = sid

        if sid in self._rows:
            row, bar, tf = self._rows[sid]
            row.config(bg=BG_SEL)
            bar.config(bg=SEL_BORDER)
            tf.config(bg=BG_SEL)

    # ── Action: Open file ─────────────────────────────────────────────────────

    def _open_file(self):
        editors = ["xdg-open", "gedit", "mousepad", "kate", "nano"]
        for ed in editors:
            if shutil.which(ed):
                try:
                    subprocess.Popen([ed, DATA_FILE])
                    return
                except Exception:
                    pass
        messagebox.showinfo("Open File",
            f"No editor found.\nOpen this file manually:\n{DATA_FILE}",
            parent=self)

    # ── Action: GitHub ────────────────────────────────────────────────────────

    def _github_dialog(self):
        dlg = GitHubDialog(self)
        self.wait_window(dlg)

    # ── CRUD ──────────────────────────────────────────────────────────────────

    def _categories(self):
        data = load_data()
        seen = []
        for s in data["shortcuts"]:
            if s["category"] not in seen:
                seen.append(s["category"])
        return seen

    def _add(self):
        dlg = ShortcutDialog(self, "Add Shortcut", self._categories())
        self.wait_window(dlg)
        if dlg.result:
            data = load_data()
            data["shortcuts"].append({"id": data["next_id"], **dlg.result})
            data["next_id"] += 1
            save_data(data)
            self._refresh()

    def _edit(self):
        if not self._selected_id:
            messagebox.showinfo("No selection",
                "Click a shortcut row to select it, then click Edit.",
                parent=self)
            return
        self._edit_id(self._selected_id)

    def _edit_id(self, sid):
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == sid), None)
        if not match:
            return
        dlg = ShortcutDialog(self, "Edit Shortcut", self._categories(), match)
        self.wait_window(dlg)
        if dlg.result:
            match.update(dlg.result)
            save_data(data)
            self._refresh()

    def _delete(self):
        if not self._selected_id:
            messagebox.showinfo("No selection",
                "Click a shortcut row to select it, then click Delete.",
                parent=self)
            return
        sid   = self._selected_id
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == sid), None)
        if not match:
            return
        if messagebox.askyesno(
                "Delete Shortcut",
                f"Delete shortcut #{sid}?\n\n{match['keys']}  --  {match['description']}",
                parent=self):
            data["shortcuts"] = [s for s in data["shortcuts"] if s["id"] != sid]
            save_data(data)
            self._selected_id = None
            self._refresh()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = JShortcutsApp()
    app.mainloop()
