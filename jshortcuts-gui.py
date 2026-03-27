#!/usr/bin/env python3
"""
jshortcuts-gui v1.2.0 -- Dark GUI for managing personal keyboard shortcuts.
Braintel Technologies | github.com/johnboscocjt/jshortcuts-jubuntu

Tabs:
  Shortcuts  -- view / add / edit / delete shortcuts, filtered by category
  Apps       -- per-app shortcut groups, add/edit/delete apps and their shortcuts
  CLI Ref    -- built-in command reference so you never need to open a terminal

Features:
  - Single shared Add/Edit dialog (double-click and Edit button open same popup)
  - Row selection with clear blue highlight + accent border
  - Scroll works anywhere in each tab (mouse wheel, no sidebar click needed)
  - Sidebar only scrolls when it actually overflows
  - GitHub push + pull buttons
  - Open file launches detached (won't block the terminal that started the GUI)
  - Ctrl+C from terminal closes the GUI cleanly
  - Version shown in title bar and status bar
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# -- Ctrl+C from terminal closes the window cleanly ---------------------------
signal.signal(signal.SIGINT, signal.SIG_DFL)

# -- Version -------------------------------------------------------------------
VERSION = "1.2.0"
APP_NAME = "jshortcuts"
COMPANY  = "Braintel Technologies"
GITHUB   = "https://github.com/johnboscocjt/jshortcuts-jubuntu"

# -- Paths ---------------------------------------------------------------------
DATA_FILE   = os.path.expanduser("~/.jshortcuts.json")
CONFIG_FILE = os.path.expanduser("~/.jshortcuts_github.json")
DEFAULT_DATA = {"shortcuts": [], "next_id": 1}

# -- Colour palette ------------------------------------------------------------
BG        = "#0f1117"
BG2       = "#161b27"
BG3       = "#1e2436"
BG_SEL    = "#1a2d50"
ACCENT    = "#5b8af5"
ACCENT2   = "#3d6ae0"
ACCENT3   = "#2a4db0"
FG        = "#e2e8f0"
FG_DIM    = "#6b7a99"
SUCCESS   = "#48bb78"
DANGER    = "#fc5c65"
WARNING   = "#f6ad55"

CAT_COLORS = ["#5b8af5", "#f6ad55", "#48bb78", "#fc5c65", "#b794f4", "#4fd1c5",
              "#f97316", "#06b6d4", "#a3e635", "#e879f9"]

FONT_TITLE  = ("JetBrains Mono", 13, "bold")
FONT_BOLD   = ("JetBrains Mono", 10, "bold")
FONT_BODY   = ("JetBrains Mono", 10)
FONT_SMALL  = ("JetBrains Mono", 9)
FONT_TINY   = ("JetBrains Mono", 8)


# =============================================================================
# Data helpers
# =============================================================================

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


# =============================================================================
# Reusable scroll canvas
# =============================================================================

def make_scrollable(parent, bg=BG):
    """
    Return (outer_frame, inner_frame, canvas).
    Bind mouse wheel to the canvas so scrolling works anywhere inside it,
    not just on the scrollbar. The canvas will NOT show a scrollbar when
    content fits -- only when content overflows.
    """
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0)
    sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview, bg=BG2,
                      troughcolor=BG2, activebackground=BG3)
    canvas.configure(yscrollcommand=sb.set)

    inner = tk.Frame(canvas, bg=bg)
    cw = canvas.create_window((0, 0), window=inner, anchor="nw")

    def on_frame_configure(_event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Only show scrollbar when content is taller than canvas
        canvas_h = canvas.winfo_height()
        content_h = inner.winfo_reqheight()
        if content_h > canvas_h:
            sb.pack(side="right", fill="y")
        else:
            sb.pack_forget()

    def on_canvas_configure(event):
        canvas.itemconfig(cw, width=event.width)
        # Re-evaluate scrollbar visibility
        canvas_h = event.height
        content_h = inner.winfo_reqheight()
        if content_h > canvas_h:
            sb.pack(side="right", fill="y")
        else:
            sb.pack_forget()

    inner.bind("<Configure>", on_frame_configure)
    canvas.bind("<Configure>", on_canvas_configure)

    def scroll(event):
        # Scroll only if there's actually overflow
        if inner.winfo_reqheight() > canvas.winfo_height():
            if event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-1, "units")
            else:
                canvas.yview_scroll(1, "units")

    canvas.bind_all("<MouseWheel>", scroll)
    canvas.bind_all("<Button-4>",   scroll)
    canvas.bind_all("<Button-5>",   scroll)

    canvas.pack(side="left", fill="both", expand=True)
    return outer, inner, canvas


# =============================================================================
# Shared Add / Edit dialog
# =============================================================================

class ShortcutDialog(tk.Toplevel):
    """
    Single dialog used for both Add and Edit.
    Button bar packed BEFORE form (side=bottom) so Save is always visible.
    """

    def __init__(self, parent, title, categories, shortcut=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        W, H = 530, 460
        self.geometry("{}x{}".format(W, H))
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry("{}x{}+{}+{}".format(W, H, px, py))

        self._build(categories, shortcut or {})

    def _field_label(self, parent, text):
        tk.Label(parent, text=text, bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(12, 3))

    def _entry_row(self, parent, value=""):
        var = tk.StringVar(value=value)
        tk.Entry(parent, textvariable=var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT).pack(fill="x", ipady=7)
        return var

    def _build(self, categories, s):
        # 1. Header (top)
        hdr = tk.Frame(self, bg=ACCENT2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  {}".format(self.title()),
                 bg=ACCENT2, fg="white", font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        # 2. Button bar (bottom) -- packed BEFORE form so it always has space
        btn_bar = tk.Frame(self, bg=BG, height=64)
        btn_bar.pack(side="bottom", fill="x")
        btn_bar.pack_propagate(False)
        tk.Button(btn_bar, text="  Cancel  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FONT_BODY,
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 18), pady=14)
        tk.Button(btn_bar, text="  Save  ", command=self._save,
                  bg=ACCENT, fg="white", font=FONT_BOLD,
                  relief="flat", padx=20, pady=8, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white"
                  ).pack(side="right", pady=14)

        # 3. Divider
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # 4. Form (fills remaining space)
        form = tk.Frame(self, bg=BG2, padx=26, pady=6)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        self._field_label(form, "Category  (pick existing or type new)")
        self.cat_var = tk.StringVar(value=s.get("category", ""))
        cb = ttk.Combobox(form, textvariable=self.cat_var,
                          values=categories, font=FONT_BODY)
        cb.pack(fill="x", ipady=5)
        self._style_combo()

        self._field_label(form, "Keys  (e.g.  Ctrl + T   |   Super + D)")
        self.keys_var = self._entry_row(form, s.get("keys", ""))

        self._field_label(form, "Description  (what does this shortcut do?)")
        self.desc_var = self._entry_row(form, s.get("description", ""))

        self._field_label(form, "Notes  (optional)")
        self.notes_var = self._entry_row(form, s.get("notes", ""))

        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _style_combo(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TCombobox",
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
            messagebox.showwarning("Missing Fields",
                "Category, Keys, and Description are required.", parent=self)
            return
        self.result = {"category": cat, "keys": keys,
                       "description": desc, "notes": notes}
        self.destroy()


# =============================================================================
# GitHub dialog
# =============================================================================

class GitHubDialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title("GitHub Sync")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()

        W, H = 560, 420
        self.geometry("{}x{}".format(W, H))
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry("{}x{}+{}+{}".format(W, H, px, py))

        self._build()

    def _entry(self, parent, value="", width=None):
        var = tk.StringVar(value=value)
        kw = {}
        if width:
            kw["width"] = width
        tk.Entry(parent, textvariable=var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT, **kw
                 ).pack(fill="x", ipady=7)
        return var

    def _lbl(self, parent, text, fg=FG_DIM):
        tk.Label(parent, text=text, bg=BG2, fg=fg,
                 font=FONT_SMALL, anchor="w").pack(fill="x", pady=(12, 3))

    def _build(self):
        cfg = load_github_config()

        # Header
        hdr = tk.Frame(self, bg=ACCENT2, height=50)
        hdr.pack(side="top", fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  GitHub Sync  --  Push & Pull",
                 bg=ACCENT2, fg="white", font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        # Button bar (bottom, packed before form)
        btn_bar = tk.Frame(self, bg=BG, height=64)
        btn_bar.pack(side="bottom", fill="x")
        btn_bar.pack_propagate(False)
        tk.Button(btn_bar, text="  Close  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FONT_BODY,
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 18), pady=14)
        tk.Button(btn_bar, text="  Pull  ", command=self._do_pull,
                  bg=WARNING, fg=BG, font=FONT_BOLD,
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right", padx=4, pady=14)
        tk.Button(btn_bar, text="  Push  ", command=self._do_push,
                  bg=SUCCESS, fg=BG, font=FONT_BOLD,
                  relief="flat", padx=16, pady=8, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right", pady=14)

        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # Form
        form = tk.Frame(self, bg=BG2, padx=26, pady=8)
        form.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        self._lbl(form, "GitHub Repository URL  (HTTPS or SSH)")
        self.url_var = self._entry(form, cfg.get("repo_url", ""))

        tk.Label(form,
                 text="  e.g. https://github.com/yourname/my-shortcuts.git",
                 bg=BG2, fg=FG_DIM, font=FONT_TINY, anchor="w"
                 ).pack(fill="x", pady=(2, 0))

        self._lbl(form, "Commit Message  (used when pushing)")
        self.msg_var = self._entry(form, "Update shortcuts")

        tk.Label(form,
                 text="  Pull = fetch + merge from GitHub into your local file\n"
                      "  Push = commit your local file and send it to GitHub",
                 bg=BG2, fg=FG_DIM, font=FONT_TINY, anchor="w", justify="left"
                 ).pack(fill="x", pady=(14, 0))

        # Status
        self.status_var = tk.StringVar(value="")
        self.status_lbl = tk.Label(form, textvariable=self.status_var,
                                   bg=BG2, fg=SUCCESS, font=FONT_SMALL,
                                   anchor="w", wraplength=490, justify="left")
        self.status_lbl.pack(fill="x", pady=(10, 0))

        self.bind("<Escape>", lambda _: self.destroy())

    def _save_url(self):
        url = self.url_var.get().strip()
        if url:
            cfg = load_github_config()
            cfg["repo_url"] = url
            save_github_config(cfg)
        return url

    def _ensure_git(self):
        if not shutil.which("git"):
            messagebox.showerror("git not found",
                "git is not installed.\nFix: sudo apt install git", parent=self)
            return False
        return True

    def _sync_dir(self):
        return os.path.expanduser("~/.jshortcuts-sync")

    def _prepare_repo(self, sync_dir, url, env):
        os.makedirs(sync_dir, exist_ok=True)
        shutil.copy(DATA_FILE, os.path.join(sync_dir, "jshortcuts.json"))
        readme = os.path.join(sync_dir, "README.md")
        if not os.path.exists(readme):
            with open(readme, "w") as rf:
                rf.write("# My jshortcuts\n\n"
                         "Managed by [jshortcuts-jubuntu]({}).\n".format(GITHUB))
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
                pass

    def _do_push(self):
        if not self._ensure_git():
            return
        url = self._save_url()
        if not url:
            messagebox.showwarning("URL required",
                "Please enter your GitHub repo URL.", parent=self)
            return

        msg = self.msg_var.get().strip() or "Update shortcuts"
        self.status_var.set("Pushing...")
        self.status_lbl.config(fg=WARNING)
        self.update()

        sync_dir = self._sync_dir()
        env = os.environ.copy()
        try:
            self._prepare_repo(sync_dir, url, env)
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
            pushed = False
            for branch in ("main", "master"):
                try:
                    subprocess.check_call(["git", "push", "-u", "origin", branch],
                                          cwd=sync_dir, env=env)
                    pushed = True
                    break
                except subprocess.CalledProcessError:
                    continue
            if pushed:
                self.status_var.set("Pushed successfully to:\n{}".format(url))
                self.status_lbl.config(fg=SUCCESS)
            else:
                self.status_var.set("Push failed. Check URL and access permissions.")
                self.status_lbl.config(fg=DANGER)
        except subprocess.CalledProcessError as e:
            self.status_var.set(
                "Push failed: {}\nCheck your URL and that you have push access.\n"
                "HTTPS repos need a GitHub Personal Access Token as password.".format(e))
            self.status_lbl.config(fg=DANGER)

    def _do_pull(self):
        if not self._ensure_git():
            return
        url = self._save_url()
        if not url:
            messagebox.showwarning("URL required",
                "Please enter your GitHub repo URL.", parent=self)
            return

        self.status_var.set("Fetching from remote...")
        self.status_lbl.config(fg=WARNING)
        self.update()

        sync_dir = self._sync_dir()
        env = os.environ.copy()
        try:
            self._prepare_repo(sync_dir, url, env)
            subprocess.check_call(["git", "fetch", "origin"], cwd=sync_dir, env=env)
            merged = False
            for branch in ("main", "master"):
                try:
                    subprocess.check_call(
                        ["git", "merge", "origin/{}".format(branch)],
                        cwd=sync_dir, env=env)
                    merged = True
                    break
                except subprocess.CalledProcessError:
                    continue

            if not merged:
                self.status_var.set(
                    "Merge failed -- there may be conflicts.\n"
                    "Resolve manually in: {}".format(sync_dir))
                self.status_lbl.config(fg=DANGER)
                return

            pulled = os.path.join(sync_dir, "jshortcuts.json")
            if os.path.exists(pulled):
                shutil.copy(pulled, DATA_FILE)
                self.status_var.set(
                    "Pull complete. {} updated.".format(DATA_FILE))
                self.status_lbl.config(fg=SUCCESS)
            else:
                self.status_var.set(
                    "Pulled OK but no jshortcuts.json found in repo.")
                self.status_lbl.config(fg=WARNING)
        except subprocess.CalledProcessError as e:
            self.status_var.set("Pull failed: {}".format(e))
            self.status_lbl.config(fg=DANGER)


# =============================================================================
# Main application
# =============================================================================

class JShortcutsApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("{} v{}".format(APP_NAME, VERSION))
        self.configure(bg=BG)
        self.geometry("940x640")
        self.minsize(680, 460)

        self._cat_color_map  = {}
        self._selected_id    = None
        self._rows           = {}          # id -> (row_frame, bar_frame, text_frame)
        self._app_rows       = {}          # app_name -> row_frame
        self._selected_cat   = tk.StringVar(value="All")
        self._search_var     = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._refresh_shortcuts())

        self._build_ui()
        self._refresh_shortcuts()
        self._refresh_apps()

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("940x640+{}+{}".format((sw - 940) // 2, (sh - 640) // 2))

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # =========================================================================
    # Top-level layout
    # =========================================================================

    def _build_ui(self):
        self._apply_notebook_style()

        # Status bar (bottom, packed first so always visible)
        status = tk.Frame(self, bg=BG2, height=28)
        status.pack(side="bottom", fill="x")
        status.pack_propagate(False)
        tk.Label(status,
                 text="  {} v{}  |  {}  |  {}".format(
                     APP_NAME, VERSION, COMPANY, GITHUB),
                 bg=BG2, fg=FG_DIM, font=FONT_TINY, anchor="w"
                 ).pack(side="left", pady=6, padx=4)
        tk.Label(status, text="data: {}  ".format(DATA_FILE),
                 bg=BG2, fg=FG_DIM, font=FONT_TINY, anchor="e"
                 ).pack(side="right", pady=6)

        # Top bar
        topbar = tk.Frame(self, bg=BG2, height=56)
        topbar.pack(side="top", fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text=APP_NAME, bg=BG2, fg=FG,
                 font=FONT_TITLE).pack(side="left", padx=(16, 0), pady=10)
        tk.Label(topbar, text="  my keyboard shortcuts",
                 bg=BG2, fg=FG_DIM, font=FONT_SMALL
                 ).pack(side="left", pady=14)

        # Top-bar right buttons
        for label, cmd, bg in [
            ("  Open File ", self._open_file, BG3),
            ("  GitHub ",    self._open_github_dialog, BG3),
        ]:
            tk.Button(topbar, text=label, command=cmd,
                      bg=bg, fg=FG_DIM, font=FONT_SMALL,
                      relief="flat", padx=8, pady=5, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=(4, 4), pady=12)

        # Search
        sf = tk.Frame(topbar, bg=BG3, padx=8, pady=4)
        sf.pack(side="right", padx=8, pady=10)
        tk.Label(sf, text="search:", bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left")
        tk.Entry(sf, textvariable=self._search_var,
                 bg=BG3, fg=FG, font=FONT_BODY,
                 relief="flat", width=18, insertbackground=ACCENT
                 ).pack(side="left", padx=(4, 0))

        # Notebook
        self._nb = ttk.Notebook(self, style="Dark.TNotebook")
        self._nb.pack(side="top", fill="both", expand=True)

        # Tab 1: Shortcuts
        self._tab_shortcuts = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_shortcuts, text="  Shortcuts  ")
        self._build_shortcuts_tab()

        # Tab 2: Apps
        self._tab_apps = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_apps, text="  Apps  ")
        self._build_apps_tab()

        # Tab 3: CLI Reference
        self._tab_cli = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_cli, text="  CLI Reference  ")
        self._build_cli_tab()

    def _apply_notebook_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dark.TNotebook",
                    background=BG2, borderwidth=0, tabmargins=[0, 0, 0, 0])
        s.configure("Dark.TNotebook.Tab",
                    background=BG2, foreground=FG_DIM,
                    padding=[16, 8], font=FONT_BODY, borderwidth=0)
        s.map("Dark.TNotebook.Tab",
              background=[("selected", BG), ("active", BG3)],
              foreground=[("selected", FG), ("active", FG)])
        s.configure("TCombobox",
                    fieldbackground=BG3, background=BG3,
                    foreground=FG, selectbackground=ACCENT,
                    selectforeground="white",
                    arrowcolor=FG_DIM, bordercolor=BG3,
                    lightcolor=BG3, darkcolor=BG3)

    # =========================================================================
    # Tab 1: Shortcuts
    # =========================================================================

    def _build_shortcuts_tab(self):
        tab = self._tab_shortcuts

        # Sidebar (left)
        self._sidebar = tk.Frame(tab, bg=BG2, width=170)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)

        tk.Label(self._sidebar, text="CATEGORIES", bg=BG2, fg=FG_DIM,
                 font=FONT_TINY, anchor="w"
                 ).pack(fill="x", padx=12, pady=(14, 6))
        self._cat_frame = tk.Frame(self._sidebar, bg=BG2)
        self._cat_frame.pack(fill="x")

        # Right pane
        right = tk.Frame(tab, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Toolbar
        toolbar = tk.Frame(right, bg=BG, pady=7, padx=14)
        toolbar.pack(side="top", fill="x")
        self._count_lbl = tk.Label(toolbar, text="", bg=BG, fg=FG_DIM, font=FONT_SMALL)
        self._count_lbl.pack(side="left")
        tk.Label(toolbar, text="double-click to edit",
                 bg=BG, fg=FG_DIM, font=FONT_TINY).pack(side="left", padx=12)
        for txt, cmd, clr in [
            ("Delete", self._delete_shortcut, DANGER),
            ("Edit",   self._edit_shortcut,   ACCENT),
            ("+ Add",  self._add_shortcut,    SUCCESS),
        ]:
            tk.Button(toolbar, text=txt, command=cmd,
                      bg=clr, fg="white", font=FONT_SMALL,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=3)

        # Scrollable list
        scroll_outer, self._list_inner, self._list_canvas = make_scrollable(right)
        scroll_outer.pack(side="top", fill="both", expand=True)

    # =========================================================================
    # Tab 2: Apps
    # =========================================================================

    def _build_apps_tab(self):
        tab = self._tab_apps

        # Left panel: app list
        left = tk.Frame(tab, bg=BG2, width=200)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="APPS", bg=BG2, fg=FG_DIM,
                 font=FONT_TINY, anchor="w"
                 ).pack(fill="x", padx=12, pady=(14, 6))

        # App list toolbar
        app_toolbar = tk.Frame(left, bg=BG2)
        app_toolbar.pack(fill="x", padx=8, pady=(0, 6))
        tk.Button(app_toolbar, text="+ App", command=self._add_app,
                  bg=SUCCESS, fg="white", font=FONT_SMALL,
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="left")
        tk.Button(app_toolbar, text="Delete", command=self._delete_app,
                  bg=DANGER, fg="white", font=FONT_SMALL,
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right")

        self._app_list_frame = tk.Frame(left, bg=BG2)
        self._app_list_frame.pack(fill="both", expand=True)

        tk.Frame(tab, bg=BG3, width=1).pack(side="left", fill="y")

        # Right panel: shortcuts for selected app
        right = tk.Frame(tab, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        app_right_toolbar = tk.Frame(right, bg=BG, pady=7, padx=14)
        app_right_toolbar.pack(side="top", fill="x")

        self._app_name_lbl = tk.Label(app_right_toolbar, text="Select an app",
                                      bg=BG, fg=FG_DIM, font=FONT_BOLD)
        self._app_name_lbl.pack(side="left")

        for txt, cmd, clr in [
            ("Delete", self._delete_app_shortcut, DANGER),
            ("Edit",   self._edit_app_shortcut,   ACCENT),
            ("+ Shortcut", self._add_app_shortcut, SUCCESS),
        ]:
            tk.Button(app_right_toolbar, text=txt, command=cmd,
                      bg=clr, fg="white", font=FONT_SMALL,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=3)

        scroll_outer2, self._app_sc_inner, _ = make_scrollable(right)
        scroll_outer2.pack(side="top", fill="both", expand=True)

        self._selected_app = None
        self._selected_app_sc_id = None
        self._app_sc_rows = {}

    # =========================================================================
    # Tab 3: CLI Reference
    # =========================================================================

    def _build_cli_tab(self):
        scroll_outer, inner, _ = make_scrollable(self._tab_cli)
        scroll_outer.pack(fill="both", expand=True)

        hdr = tk.Frame(inner, bg=BG2, height=44)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="  jshortcuts -- CLI Command Reference",
                 bg=BG2, fg=FG, font=FONT_BOLD, anchor="w"
                 ).pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text="v{}".format(VERSION),
                 bg=BG2, fg=FG_DIM, font=FONT_SMALL, anchor="e"
                 ).pack(side="right", padx=16)

        COMMANDS = [
            ("jshortcuts",
             "List all shortcuts",
             "Displays all shortcuts grouped by category with colour coding.\n"
             "Run with no arguments."),
            ("jshortcuts add",
             "Add a new shortcut",
             "Interactive prompts: category, keys, description, notes.\n"
             "Type a new category name or pick from the existing list."),
            ("jshortcuts edit <id>",
             "Edit a shortcut",
             "Shows current values in brackets. Press Enter to keep any field.\n"
             "Find the ID by running jshortcuts (shown as [N] on each row)."),
            ("jshortcuts del <id>",
             "Delete a shortcut",
             "Asks for confirmation before deleting permanently.\n"
             "Aliases: del  delete  rm"),
            ("jshortcuts cat <n>",
             "Filter by category",
             "Shows only shortcuts in that category (case-insensitive).\n"
             'Multi-word categories: jshortcuts cat "VS Code"'),
            ("jshortcuts search <q>",
             "Search shortcuts",
             "Searches keys, description, notes, and category fields.\n"
             "Example: jshortcuts search terminal"),
            ("jshortcuts open",
             "Open data file in editor",
             "Opens ~/.jshortcuts.json in gedit, mousepad, nano, etc.\n"
             "Launches detached so it does not block your terminal."),
            ("jshortcuts github push",
             "Push shortcuts to GitHub",
             "Prompts for repo URL and commit message, then git push.\n"
             "Stores URL in ~/.jshortcuts_github.json for next time."),
            ("jshortcuts github pull",
             "Pull from GitHub (fetch + merge)",
             "Fetches latest from your GitHub repo and merges into local file.\n"
             "Use this before pushing to avoid conflicts."),
            ("jshortcuts gui",
             "Open the GUI window",
             "Launches this graphical interface.\n"
             "Also available from the Ubuntu app menu (search 'jshortcuts')."),
            ("jshortcuts help",
             "Show help in terminal",
             "Prints a compact command reference in the terminal.\n"
             "Aliases: help  --help  -h"),
        ]

        for i, (cmd, summary, detail) in enumerate(COMMANDS):
            row = tk.Frame(inner, bg=BG2 if i % 2 == 0 else BG)
            row.pack(fill="x", padx=16, pady=(10, 0))

            chip = tk.Frame(row, bg=BG3)
            chip.pack(side="left", anchor="nw", padx=(0, 14), pady=4)
            tk.Label(chip, text="  {}  ".format(cmd),
                     bg=BG3, fg=ACCENT, font=FONT_BOLD, anchor="w"
                     ).pack(padx=2, pady=4)

            txt_col = tk.Frame(row, bg=row["bg"])
            txt_col.pack(side="left", fill="both", expand=True, anchor="nw")
            tk.Label(txt_col, text=summary, bg=row["bg"], fg=FG,
                     font=FONT_BOLD, anchor="w").pack(fill="x")
            tk.Label(txt_col, text=detail, bg=row["bg"], fg=FG_DIM,
                     font=FONT_SMALL, anchor="w", justify="left",
                     wraplength=560).pack(fill="x", pady=(2, 0))

        tk.Frame(inner, bg=BG3, height=1).pack(fill="x", padx=16, pady=16)
        note = tk.Frame(inner, bg=BG)
        note.pack(fill="x", padx=16, pady=(0, 16))
        tk.Label(note, text="Data file:", bg=BG, fg=FG_DIM, font=FONT_BOLD
                 ).pack(side="left")
        tk.Label(note, text="  {}".format(DATA_FILE),
                 bg=BG, fg=ACCENT, font=FONT_SMALL).pack(side="left")
        tk.Label(note,
                 text="  (CLI and GUI share this file -- always in sync)",
                 bg=BG, fg=FG_DIM, font=FONT_SMALL).pack(side="left")

        tk.Frame(inner, bg=BG3, height=1).pack(fill="x", padx=16, pady=(0, 8))
        repo = tk.Frame(inner, bg=BG)
        repo.pack(fill="x", padx=16, pady=(0, 20))
        tk.Label(repo, text="GitHub:", bg=BG, fg=FG_DIM, font=FONT_BOLD
                 ).pack(side="left")
        lnk = tk.Label(repo, text="  {}".format(GITHUB),
                       bg=BG, fg=ACCENT, font=FONT_SMALL, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda _: self._open_url(GITHUB))
        tk.Label(repo, text="    |    {}".format(COMPANY),
                 bg=BG, fg=FG_DIM, font=FONT_SMALL).pack(side="left")

    # =========================================================================
    # Sidebar (Shortcuts tab)
    # =========================================================================

    def _build_sidebar(self, categories):
        for w in self._cat_frame.winfo_children():
            w.destroy()
        for cat in ["All"] + categories:
            sel = (self._selected_cat.get() == cat)
            color = self._cat_color_map.get(cat, ACCENT) if cat != "All" else ACCENT
            bg = BG3 if sel else BG2
            fg = color if sel else FG_DIM
            tk.Button(self._cat_frame, text="  {}".format(cat),
                      command=lambda c=cat: self._select_cat(c),
                      bg=bg, fg=fg, font=FONT_SMALL,
                      relief="flat", anchor="w", padx=8, pady=5,
                      cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(fill="x")

    def _select_cat(self, cat):
        self._selected_cat.set(cat)
        self._refresh_shortcuts()

    # =========================================================================
    # Refresh shortcuts list
    # =========================================================================

    def _refresh_shortcuts(self):
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

        self._count_lbl.config(text="{} shortcut(s)".format(len(filtered)))
        self._render_shortcuts(filtered)

    def _render_shortcuts(self, shortcuts):
        for w in self._list_inner.winfo_children():
            w.destroy()
        self._selected_id = None
        self._rows = {}

        if not shortcuts:
            tk.Label(self._list_inner,
                     text="\n  No shortcuts found.\n  Click '+ Add' to create one.",
                     bg=BG, fg=FG_DIM, font=FONT_BODY, justify="left"
                     ).pack(padx=24, pady=40)
            return

        grouped = {}
        for s in shortcuts:
            grouped.setdefault(s["category"], []).append(s)

        for cat, items in grouped.items():
            color = self._cat_color_map.get(cat, ACCENT)
            hdr = tk.Frame(self._list_inner, bg=BG)
            hdr.pack(fill="x", padx=16, pady=(14, 5))
            tk.Frame(hdr, bg=color, width=4, height=16).pack(side="left")
            tk.Label(hdr, text="  {}".format(cat.upper()),
                     bg=BG, fg=color, font=("JetBrains Mono", 9, "bold")
                     ).pack(side="left")
            for s in items:
                self._make_shortcut_row(s, color)

    def _make_shortcut_row(self, s, cat_color):
        sid = s["id"]
        sel = (self._selected_id == sid)

        row = tk.Frame(self._list_inner, bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)

        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")

        tk.Label(row, text=" {} ".format(sid), bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(5, 0), pady=9)

        keys_lbl = tk.Label(row, text="  {}  ".format(s["keys"]),
                            bg=BG3, fg=cat_color, font=FONT_BOLD, padx=3)
        keys_lbl.pack(side="left", padx=7, pady=9)

        tf = tk.Frame(row, bg=row["bg"])
        tf.pack(side="left", fill="both", expand=True, pady=7)
        tk.Label(tf, text=s["description"], bg=tf["bg"], fg=FG,
                 font=FONT_BODY, anchor="w").pack(fill="x")
        if s.get("notes"):
            tk.Label(tf, text=s["notes"], bg=tf["bg"], fg=FG_DIM,
                     font=FONT_SMALL, anchor="w").pack(fill="x")

        def on_click(_e, i=sid):
            self._select_shortcut_row(i)

        def on_dbl(_e, i=sid):
            self._select_shortcut_row(i)
            self._edit_shortcut()          # same popup as Edit button

        def on_enter(_e, r=row, t=tf):
            if self._selected_id != sid:
                r.config(bg=BG3)
                t.config(bg=BG3)

        def on_leave(_e, r=row, b=bar, t=tf):
            if self._selected_id == sid:
                r.config(bg=BG_SEL)
                b.config(bg=ACCENT)
                t.config(bg=BG_SEL)
            else:
                r.config(bg=BG2)
                b.config(bg=BG3)
                t.config(bg=BG2)

        for w in (row, keys_lbl, tf):
            w.bind("<Button-1>", on_click)
            w.bind("<Double-1>", on_dbl)
            w.bind("<Enter>",    on_enter)
            w.bind("<Leave>",    on_leave)

        self._rows[sid] = (row, bar, tf)

    def _select_shortcut_row(self, sid):
        if self._selected_id and self._selected_id in self._rows:
            old_r, old_b, old_t = self._rows[self._selected_id]
            old_r.config(bg=BG2)
            old_b.config(bg=BG3)
            old_t.config(bg=BG2)
        self._selected_id = sid
        if sid in self._rows:
            r, b, t = self._rows[sid]
            r.config(bg=BG_SEL)
            b.config(bg=ACCENT)
            t.config(bg=BG_SEL)

    # =========================================================================
    # Shortcuts CRUD
    # =========================================================================

    def _shortcut_categories(self):
        data = load_data()
        seen = []
        for s in data["shortcuts"]:
            if s["category"] not in seen:
                seen.append(s["category"])
        return seen

    def _add_shortcut(self):
        dlg = ShortcutDialog(self, "Add Shortcut", self._shortcut_categories())
        self.wait_window(dlg)
        if dlg.result:
            data = load_data()
            data["shortcuts"].append({"id": data["next_id"], **dlg.result})
            data["next_id"] += 1
            save_data(data)
            self._refresh_shortcuts()

    def _edit_shortcut(self):
        if not self._selected_id:
            messagebox.showinfo("No selection",
                "Click a row to select it, then click Edit\n"
                "(or double-click any row directly).", parent=self)
            return
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == self._selected_id), None)
        if not match:
            return
        dlg = ShortcutDialog(self, "Edit Shortcut", self._shortcut_categories(), match)
        self.wait_window(dlg)
        if dlg.result:
            match.update(dlg.result)
            save_data(data)
            self._refresh_shortcuts()

    def _delete_shortcut(self):
        if not self._selected_id:
            messagebox.showinfo("No selection",
                "Click a row to select it, then click Delete.", parent=self)
            return
        sid   = self._selected_id
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == sid), None)
        if not match:
            return
        if messagebox.askyesno("Delete Shortcut",
                "Delete shortcut #{}?\n\n{}  --  {}".format(
                    sid, match["keys"], match["description"]),
                parent=self):
            data["shortcuts"] = [s for s in data["shortcuts"] if s["id"] != sid]
            save_data(data)
            self._selected_id = None
            self._refresh_shortcuts()

    # =========================================================================
    # Apps tab helpers
    # =========================================================================

    def _load_apps(self):
        data = load_data()
        return data.get("apps", {})

    def _save_apps(self, apps_dict):
        data = load_data()
        data["apps"] = apps_dict
        save_data(data)

    def _refresh_apps(self):
        for w in self._app_list_frame.winfo_children():
            w.destroy()
        self._app_rows = {}
        apps = self._load_apps()
        if not apps:
            tk.Label(self._app_list_frame,
                     text="\nNo apps yet.\nClick '+ App' to add one.",
                     bg=BG2, fg=FG_DIM, font=FONT_SMALL, justify="left"
                     ).pack(padx=12, pady=10)
            return
        for app_name in sorted(apps.keys()):
            self._make_app_row(app_name)
        # Refresh shortcuts for selected app
        if self._selected_app:
            self._render_app_shortcuts(self._selected_app)

    def _make_app_row(self, app_name):
        apps = self._load_apps()
        count = len(apps.get(app_name, {}).get("shortcuts", []))
        sel = (self._selected_app == app_name)

        row = tk.Frame(self._app_list_frame,
                       bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", padx=4, pady=2)

        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")

        inner = tk.Frame(row, bg=row["bg"])
        inner.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        tk.Label(inner, text=app_name, bg=inner["bg"], fg=FG,
                 font=FONT_BOLD, anchor="w").pack(fill="x")
        tk.Label(inner, text="{} shortcut(s)".format(count),
                 bg=inner["bg"], fg=FG_DIM, font=FONT_TINY, anchor="w"
                 ).pack(fill="x")

        def on_click(_e, n=app_name):
            self._select_app(n)

        for w in (row, inner):
            w.bind("<Button-1>", on_click)
            w.bind("<Enter>",    lambda _e, r=row, i=inner: (
                r.config(bg=BG3), i.config(bg=BG3)) if self._selected_app != app_name else None)
            w.bind("<Leave>",    lambda _e, r=row, i=inner, n=app_name: (
                r.config(bg=BG_SEL if self._selected_app == n else BG2),
                i.config(bg=BG_SEL if self._selected_app == n else BG2)))

        self._app_rows[app_name] = (row, bar, inner)

    def _select_app(self, app_name):
        # Deselect old
        if self._selected_app and self._selected_app in self._app_rows:
            old_r, old_b, old_i = self._app_rows[self._selected_app]
            old_r.config(bg=BG2)
            old_b.config(bg=BG3)
            old_i.config(bg=BG2)
        self._selected_app = app_name
        self._selected_app_sc_id = None
        self._app_sc_rows = {}
        if app_name in self._app_rows:
            r, b, i = self._app_rows[app_name]
            r.config(bg=BG_SEL)
            b.config(bg=ACCENT)
            i.config(bg=BG_SEL)
        self._app_name_lbl.config(text=app_name, fg=FG)
        self._render_app_shortcuts(app_name)

    def _render_app_shortcuts(self, app_name):
        for w in self._app_sc_inner.winfo_children():
            w.destroy()
        self._app_sc_rows = {}
        self._selected_app_sc_id = None
        apps = self._load_apps()
        shortcuts = apps.get(app_name, {}).get("shortcuts", [])

        if not shortcuts:
            tk.Label(self._app_sc_inner,
                     text="\n  No shortcuts for this app.\n  Click '+ Shortcut' to add one.",
                     bg=BG, fg=FG_DIM, font=FONT_BODY, justify="left"
                     ).pack(padx=24, pady=30)
            return

        # Find this app's category color
        apps_list = sorted(apps.keys())
        idx = apps_list.index(app_name) if app_name in apps_list else 0
        color = CAT_COLORS[idx % len(CAT_COLORS)]

        hdr = tk.Frame(self._app_sc_inner, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(12, 5))
        tk.Frame(hdr, bg=color, width=4, height=16).pack(side="left")
        tk.Label(hdr, text="  {}".format(app_name.upper()),
                 bg=BG, fg=color, font=("JetBrains Mono", 9, "bold")
                 ).pack(side="left")

        for sc in shortcuts:
            self._make_app_sc_row(sc, color, app_name)

    def _make_app_sc_row(self, sc, color, app_name):
        sc_id = sc["id"]
        sel = (self._selected_app_sc_id == sc_id)

        row = tk.Frame(self._app_sc_inner, bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)

        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")

        tk.Label(row, text=" {} ".format(sc_id), bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(5, 0), pady=9)

        keys_lbl = tk.Label(row, text="  {}  ".format(sc["keys"]),
                            bg=BG3, fg=color, font=FONT_BOLD, padx=3)
        keys_lbl.pack(side="left", padx=7, pady=9)

        tf = tk.Frame(row, bg=row["bg"])
        tf.pack(side="left", fill="both", expand=True, pady=7)
        tk.Label(tf, text=sc["description"], bg=tf["bg"], fg=FG,
                 font=FONT_BODY, anchor="w").pack(fill="x")
        if sc.get("notes"):
            tk.Label(tf, text=sc["notes"], bg=tf["bg"], fg=FG_DIM,
                     font=FONT_SMALL, anchor="w").pack(fill="x")

        def on_click(_e, i=sc_id):
            self._select_app_sc_row(i)

        def on_dbl(_e, i=sc_id):
            self._select_app_sc_row(i)
            self._edit_app_shortcut()

        def on_enter(_e, r=row, t=tf):
            if self._selected_app_sc_id != sc_id:
                r.config(bg=BG3)
                t.config(bg=BG3)

        def on_leave(_e, r=row, b=bar, t=tf):
            if self._selected_app_sc_id == sc_id:
                r.config(bg=BG_SEL)
                b.config(bg=ACCENT)
                t.config(bg=BG_SEL)
            else:
                r.config(bg=BG2)
                b.config(bg=BG3)
                t.config(bg=BG2)

        for w in (row, keys_lbl, tf):
            w.bind("<Button-1>", on_click)
            w.bind("<Double-1>", on_dbl)
            w.bind("<Enter>",    on_enter)
            w.bind("<Leave>",    on_leave)

        self._app_sc_rows[sc_id] = (row, bar, tf)

    def _select_app_sc_row(self, sc_id):
        if self._selected_app_sc_id and self._selected_app_sc_id in self._app_sc_rows:
            old_r, old_b, old_t = self._app_sc_rows[self._selected_app_sc_id]
            old_r.config(bg=BG2)
            old_b.config(bg=BG3)
            old_t.config(bg=BG2)
        self._selected_app_sc_id = sc_id
        if sc_id in self._app_sc_rows:
            r, b, t = self._app_sc_rows[sc_id]
            r.config(bg=BG_SEL)
            b.config(bg=ACCENT)
            t.config(bg=BG_SEL)

    # -- Apps CRUD -------------------------------------------------------------

    def _add_app(self):
        name = self._simple_input("Add App",
            "App name (e.g. VS Code, Firefox, Terminal):")
        if not name:
            return
        apps = self._load_apps()
        if name in apps:
            messagebox.showwarning("Exists",
                "An app named '{}' already exists.".format(name), parent=self)
            return
        apps[name] = {"shortcuts": [], "next_id": 1}
        self._save_apps(apps)
        self._refresh_apps()
        self._select_app(name)

    def _delete_app(self):
        if not self._selected_app:
            messagebox.showinfo("No selection",
                "Click an app to select it, then click Delete.", parent=self)
            return
        name = self._selected_app
        if messagebox.askyesno("Delete App",
                "Delete app '{}' and all its shortcuts?".format(name), parent=self):
            apps = self._load_apps()
            apps.pop(name, None)
            self._save_apps(apps)
            self._selected_app = None
            for w in self._app_sc_inner.winfo_children():
                w.destroy()
            self._app_name_lbl.config(text="Select an app", fg=FG_DIM)
            self._refresh_apps()

    def _add_app_shortcut(self):
        if not self._selected_app:
            messagebox.showinfo("No app selected",
                "Click an app in the left panel first.", parent=self)
            return
        cats = []   # no category needed for app shortcuts -- use empty list
        dlg = ShortcutDialog(self, "Add Shortcut to {}".format(self._selected_app), cats)
        self.wait_window(dlg)
        if dlg.result:
            apps = self._load_apps()
            app  = apps.setdefault(self._selected_app,
                                   {"shortcuts": [], "next_id": 1})
            entry = {"id": app.get("next_id", 1), **dlg.result}
            entry["category"] = self._selected_app   # category = app name
            app["shortcuts"].append(entry)
            app["next_id"] = app.get("next_id", 1) + 1
            self._save_apps(apps)
            self._refresh_apps()

    def _edit_app_shortcut(self):
        if not self._selected_app or not self._selected_app_sc_id:
            messagebox.showinfo("No selection",
                "Select an app and a shortcut row first.", parent=self)
            return
        apps  = self._load_apps()
        app   = apps.get(self._selected_app, {})
        match = next((s for s in app.get("shortcuts", [])
                      if s["id"] == self._selected_app_sc_id), None)
        if not match:
            return
        dlg = ShortcutDialog(self,
                             "Edit Shortcut -- {}".format(self._selected_app),
                             [], match)
        self.wait_window(dlg)
        if dlg.result:
            match.update(dlg.result)
            match["category"] = self._selected_app
            self._save_apps(apps)
            self._refresh_apps()

    def _delete_app_shortcut(self):
        if not self._selected_app or not self._selected_app_sc_id:
            messagebox.showinfo("No selection",
                "Select an app and a shortcut row first.", parent=self)
            return
        sc_id = self._selected_app_sc_id
        apps  = self._load_apps()
        app   = apps.get(self._selected_app, {})
        match = next((s for s in app.get("shortcuts", [])
                      if s["id"] == sc_id), None)
        if not match:
            return
        if messagebox.askyesno("Delete Shortcut",
                "Delete shortcut #{}?\n\n{}  --  {}".format(
                    sc_id, match["keys"], match["description"]), parent=self):
            app["shortcuts"] = [s for s in app["shortcuts"] if s["id"] != sc_id]
            self._save_apps(apps)
            self._selected_app_sc_id = None
            self._refresh_apps()

    # =========================================================================
    # Open file / GitHub / URL helpers
    # =========================================================================

    def _open_file(self):
        editors = ["xdg-open", "gedit", "mousepad", "kate", "pluma"]
        for ed in editors:
            if shutil.which(ed):
                try:
                    subprocess.Popen(
                        [ed, DATA_FILE],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        start_new_session=True   # detached: won't block terminal
                    )
                    return
                except Exception:
                    pass
        messagebox.showinfo("Open File",
            "No GUI editor found.\nOpen this file manually:\n{}".format(DATA_FILE),
            parent=self)

    def _open_github_dialog(self):
        dlg = GitHubDialog(self)
        self.wait_window(dlg)
        # Reload data in case a pull updated the file
        self._refresh_shortcuts()
        self._refresh_apps()

    def _open_url(self, url):
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", url],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)

    def _simple_input(self, title, prompt):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set()
        dlg.focus_set()

        W, H = 400, 160
        dlg.geometry("{}x{}".format(W, H))
        dlg.update_idletasks()
        px = self.winfo_x() + (self.winfo_width()  - W) // 2
        py = self.winfo_y() + (self.winfo_height() - H) // 2
        dlg.geometry("{}x{}+{}+{}".format(W, H, px, py))

        tk.Label(dlg, text=prompt, bg=BG, fg=FG, font=FONT_BODY,
                 anchor="w").pack(fill="x", padx=20, pady=(16, 6))
        var = tk.StringVar()
        tk.Entry(dlg, textvariable=var,
                 bg=BG3, fg=FG, font=FONT_BODY, relief="flat",
                 insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT).pack(fill="x", padx=20, ipady=7)

        result = [None]

        def ok(_e=None):
            v = var.get().strip()
            if v:
                result[0] = v
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=12)
        tk.Button(btn_row, text=" Cancel ", command=dlg.destroy,
                  bg=BG3, fg=FG_DIM, font=FONT_BODY, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(side="right", padx=(6, 0))
        tk.Button(btn_row, text=" OK ", command=ok,
                  bg=ACCENT, fg="white", font=FONT_BOLD, relief="flat",
                  padx=12, pady=5, cursor="hand2").pack(side="right")

        dlg.bind("<Return>", ok)
        dlg.bind("<Escape>", lambda _: dlg.destroy())
        self.wait_window(dlg)
        return result[0]


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    app = JShortcutsApp()
    app.mainloop()
