#!/usr/bin/env python3
"""
jshortcuts-gui v1.3.0
Braintel Technologies | github.com/johnboscocjt/jshortcuts-jubuntu

Tabs:
  Shortcuts  -- global shortcuts grouped by category
  Apps       -- per-app shortcut groups
  All My Apps -- directory of apps with descriptions, links, tags
  CLI Ref    -- built-in command reference

Fixes v1.3.0:
  - Apps sidebar: entire row is clickable (not just border)
  - Shortcuts tab smooth scroll works everywhere (same as CLI tab)
  - GitHub pull actually reloads all tabs after updating the file
  - Open File lets user choose editor; falls back to VS Code, then others
  - AllMyApps tab with dynamic fields, edit/delete/create
  - Scrollbar only appears when content actually overflows
"""

import json
import os
import shutil
import signal
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox

signal.signal(signal.SIGINT, signal.SIG_DFL)

# -- Constants -----------------------------------------------------------------
VERSION  = "1.3.0"
APP_NAME = "jshortcuts"
COMPANY  = "Braintel Technologies"
GITHUB   = "https://github.com/johnboscocjt/jshortcuts-jubuntu"

DATA_FILE    = os.path.expanduser("~/.jshortcuts.json")
CONFIG_FILE  = os.path.expanduser("~/.jshortcuts_github.json")
DEFAULT_DATA = {"shortcuts": [], "next_id": 1, "apps": {}, "my_apps": []}

# -- Colours -------------------------------------------------------------------
BG      = "#0f1117"
BG2     = "#161b27"
BG3     = "#1e2436"
BG_SEL  = "#1a2d50"
ACCENT  = "#5b8af5"
ACCENT2 = "#3d6ae0"
FG      = "#e2e8f0"
FG_DIM  = "#6b7a99"
SUCCESS = "#48bb78"
DANGER  = "#fc5c65"
WARNING = "#f6ad55"

CAT_COLORS = [
    "#5b8af5","#f6ad55","#48bb78","#fc5c65","#b794f4","#4fd1c5",
    "#f97316","#06b6d4","#a3e635","#e879f9","#fbbf24","#34d399",
]

FT = ("JetBrains Mono", 13, "bold")   # title
FB = ("JetBrains Mono", 10, "bold")   # bold body
FN = ("JetBrains Mono", 10)           # normal body
FS = ("JetBrains Mono", 9)            # small
FT2 = ("JetBrains Mono", 8)          # tiny


# =============================================================================
# Data layer
# =============================================================================

def load_data():
    if not os.path.exists(DATA_FILE):
        sd = os.path.dirname(os.path.abspath(__file__))
        df = os.path.join(sd, "jshortcuts_default.json")
        if os.path.exists(df):
            shutil.copy(df, DATA_FILE)
        else:
            save_data(DEFAULT_DATA)
    with open(DATA_FILE) as f:
        data = json.load(f)
    data.setdefault("apps", {})
    data.setdefault("my_apps", [])
    return data


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
# Scrollable canvas helper
# Scrollbar only appears when content height > canvas height.
# Mouse-wheel works anywhere inside the canvas (not just on the scrollbar).
# =============================================================================

class ScrollFrame(tk.Frame):
    """A frame that scrolls vertically. Use .inner as the parent for widgets."""

    def __init__(self, parent, bg=BG, **kw):
        super().__init__(parent, bg=bg, **kw)
        self._bg = bg

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self._sb = tk.Scrollbar(self, orient="vertical",
                                command=self._canvas.yview,
                                bg=BG2, troughcolor=BG2,
                                activebackground=BG3)
        self._canvas.configure(yscrollcommand=self._sb.set)

        self.inner = tk.Frame(self._canvas, bg=bg)
        self._cw = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self._canvas.pack(side="left", fill="both", expand=True)

        self.inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind wheel everywhere inside this widget
        self._canvas.bind("<MouseWheel>", self._scroll)
        self._canvas.bind("<Button-4>",   self._scroll)
        self._canvas.bind("<Button-5>",   self._scroll)

    def _on_inner_configure(self, _e=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._maybe_show_sb()

    def _on_canvas_configure(self, e):
        self._canvas.itemconfig(self._cw, width=e.width)
        self._maybe_show_sb()

    def _maybe_show_sb(self):
        ch = self._canvas.winfo_height()
        ih = self.inner.winfo_reqheight()
        if ih > ch and ch > 1:
            self._sb.pack(side="right", fill="y", before=self._canvas)
        else:
            self._sb.pack_forget()

    def _scroll(self, e):
        if self.inner.winfo_reqheight() <= self._canvas.winfo_height():
            return
        if e.num == 4 or (hasattr(e, "delta") and e.delta > 0):
            self._canvas.yview_scroll(-1, "units")
        else:
            self._canvas.yview_scroll(1, "units")

    def bind_scroll_recursive(self, widget):
        """Propagate scroll events from all child widgets to this canvas."""
        widget.bind("<MouseWheel>", self._scroll, add="+")
        widget.bind("<Button-4>",   self._scroll, add="+")
        widget.bind("<Button-5>",   self._scroll, add="+")
        for child in widget.winfo_children():
            self.bind_scroll_recursive(child)


# =============================================================================
# Shared shortcut Add/Edit dialog
# =============================================================================

class ShortcutDialog(tk.Toplevel):
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

    def _lbl(self, p, t):
        tk.Label(p, text=t, bg=BG2, fg=FG_DIM, font=FS, anchor="w").pack(
            fill="x", pady=(11, 3))

    def _ent(self, p, val=""):
        v = tk.StringVar(value=val)
        tk.Entry(p, textvariable=v, bg=BG3, fg=FG, font=FN, relief="flat",
                 insertbackground=ACCENT, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT
                 ).pack(fill="x", ipady=7)
        return v

    def _build(self, cats, s):
        # Header
        h = tk.Frame(self, bg=ACCENT2, height=50)
        h.pack(side="top", fill="x"); h.pack_propagate(False)
        tk.Label(h, text="  " + self.title(), bg=ACCENT2, fg="white",
                 font=FB, anchor="w").pack(side="left", padx=14, pady=13)

        # Buttons (bottom, before form)
        bb = tk.Frame(self, bg=BG, height=64)
        bb.pack(side="bottom", fill="x"); bb.pack_propagate(False)
        tk.Button(bb, text="  Cancel  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FN, relief="flat",
                  padx=14, pady=8, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 18), pady=14)
        tk.Button(bb, text="  Save  ", command=self._save,
                  bg=ACCENT, fg="white", font=FB, relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white"
                  ).pack(side="right", pady=14)
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # Form
        f = tk.Frame(self, bg=BG2, padx=26, pady=6)
        f.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        self._lbl(f, "Category  (pick existing or type new)")
        self.cat_v = tk.StringVar(value=s.get("category", ""))
        cb = ttk.Combobox(f, textvariable=self.cat_v, values=cats, font=FN)
        cb.pack(fill="x", ipady=5)
        self._style_combo()

        self._lbl(f, "Keys  (e.g. Ctrl + T  |  Super + D)")
        self.keys_v = self._ent(f, s.get("keys", ""))
        self._lbl(f, "Description")
        self.desc_v = self._ent(f, s.get("description", ""))
        self._lbl(f, "Notes  (optional)")
        self.notes_v = self._ent(f, s.get("notes", ""))

        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _style_combo(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("TCombobox", fieldbackground=BG3, background=BG3,
                     foreground=FG, selectbackground=ACCENT,
                     selectforeground="white", arrowcolor=FG_DIM,
                     bordercolor=BG3, lightcolor=BG3, darkcolor=BG3)

    def _save(self):
        cat   = self.cat_v.get().strip()
        keys  = self.keys_v.get().strip()
        desc  = self.desc_v.get().strip()
        notes = self.notes_v.get().strip()
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
    def __init__(self, parent, on_pull_success=None):
        super().__init__(parent)
        self._on_pull_success = on_pull_success
        self.title("GitHub Sync")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        W, H = 570, 430
        self.geometry("{}x{}".format(W, H))
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry("{}x{}+{}+{}".format(W, H, px, py))
        self._build()

    def _ent(self, p, val=""):
        v = tk.StringVar(value=val)
        tk.Entry(p, textvariable=v, bg=BG3, fg=FG, font=FN, relief="flat",
                 insertbackground=ACCENT, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT
                 ).pack(fill="x", ipady=7)
        return v

    def _build(self):
        cfg = load_github_config()

        h = tk.Frame(self, bg=ACCENT2, height=50)
        h.pack(side="top", fill="x"); h.pack_propagate(False)
        tk.Label(h, text="  GitHub Sync -- Push & Pull",
                 bg=ACCENT2, fg="white", font=FB, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        bb = tk.Frame(self, bg=BG, height=64)
        bb.pack(side="bottom", fill="x"); bb.pack_propagate(False)
        tk.Button(bb, text="  Close  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FN, relief="flat",
                  padx=14, pady=8, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 18), pady=14)
        tk.Button(bb, text="  Pull  ", command=self._do_pull,
                  bg=WARNING, fg=BG, font=FB, relief="flat",
                  padx=16, pady=8, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right", padx=4, pady=14)
        tk.Button(bb, text="  Push  ", command=self._do_push,
                  bg=SUCCESS, fg=BG, font=FB, relief="flat",
                  padx=16, pady=8, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right", pady=14)
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        f = tk.Frame(self, bg=BG2, padx=26, pady=12)
        f.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))

        tk.Label(f, text="GitHub Repository URL  (HTTPS or SSH)",
                 bg=BG2, fg=FG_DIM, font=FS, anchor="w"
                 ).pack(fill="x", pady=(4, 3))
        self.url_v = self._ent(f, cfg.get("repo_url", ""))
        tk.Label(f, text="  e.g. https://github.com/yourname/my-shortcuts.git",
                 bg=BG2, fg=FG_DIM, font=FT2, anchor="w"
                 ).pack(fill="x", pady=(2, 14))

        tk.Label(f, text="Commit Message  (used when pushing)",
                 bg=BG2, fg=FG_DIM, font=FS, anchor="w"
                 ).pack(fill="x", pady=(0, 3))
        self.msg_v = self._ent(f, "Update shortcuts")

        tk.Label(f, text="  Pull = fetch + merge from GitHub into your local file\n"
                         "  Push = commit your local changes and send to GitHub",
                 bg=BG2, fg=FG_DIM, font=FT2, anchor="w", justify="left"
                 ).pack(fill="x", pady=(12, 0))

        self.status_v = tk.StringVar(value="")
        self.status_lbl = tk.Label(f, textvariable=self.status_v,
                                   bg=BG2, fg=SUCCESS, font=FS,
                                   anchor="w", wraplength=500, justify="left")
        self.status_lbl.pack(fill="x", pady=(10, 0))
        self.bind("<Escape>", lambda _: self.destroy())

    def _save_url(self):
        url = self.url_v.get().strip()
        if url:
            cfg = load_github_config()
            cfg["repo_url"] = url
            save_github_config(cfg)
        return url

    def _check_git(self):
        if not shutil.which("git"):
            messagebox.showerror("git not found",
                "git is not installed.\nFix: sudo apt install git", parent=self)
            return False
        return True

    def _sync_dir(self):
        return os.path.expanduser("~/.jshortcuts-sync")

    def _prep(self, sync_dir, url, env):
        os.makedirs(sync_dir, exist_ok=True)
        shutil.copy(DATA_FILE, os.path.join(sync_dir, "jshortcuts.json"))
        readme = os.path.join(sync_dir, "README.md")
        if not os.path.exists(readme):
            with open(readme, "w") as rf:
                rf.write("# My jshortcuts\n\nManaged by [jshortcuts-jubuntu]({}).\n".format(GITHUB))
        gd = os.path.join(sync_dir, ".git")
        if not os.path.isdir(gd):
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
        if not self._check_git():
            return
        url = self._save_url()
        if not url:
            messagebox.showwarning("URL required",
                "Please enter your GitHub repo URL.", parent=self)
            return
        msg = self.msg_v.get().strip() or "Update shortcuts"
        self.status_v.set("Pushing...")
        self.status_lbl.config(fg=WARNING)
        self.update()
        sd = self._sync_dir()
        env = os.environ.copy()
        try:
            self._prep(sd, url, env)
            subprocess.check_call(["git", "add", "."], cwd=sd, env=env,
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=sd, env=env)
            if diff.returncode == 0:
                self.status_v.set("Nothing changed since last push.")
                self.status_lbl.config(fg=FG_DIM)
                return
            subprocess.check_call(["git", "commit", "-m", msg], cwd=sd, env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            pushed = False
            for branch in ("main", "master"):
                try:
                    subprocess.check_call(["git", "push", "-u", "origin", branch],
                                          cwd=sd, env=env)
                    pushed = True
                    break
                except subprocess.CalledProcessError:
                    continue
            if pushed:
                self.status_v.set("Pushed successfully to:\n{}".format(url))
                self.status_lbl.config(fg=SUCCESS)
            else:
                self.status_v.set("Push failed. Check URL and access permissions.")
                self.status_lbl.config(fg=DANGER)
        except subprocess.CalledProcessError as e:
            self.status_v.set("Push failed: {}\nFor HTTPS repos use a GitHub Personal Access Token.".format(e))
            self.status_lbl.config(fg=DANGER)

    def _do_pull(self):
        if not self._check_git():
            return
        url = self._save_url()
        if not url:
            messagebox.showwarning("URL required",
                "Please enter your GitHub repo URL.", parent=self)
            return
        self.status_v.set("Fetching from remote...")
        self.status_lbl.config(fg=WARNING)
        self.update()
        sd = self._sync_dir()
        env = os.environ.copy()
        try:
            self._prep(sd, url, env)
            subprocess.check_call(["git", "fetch", "origin"], cwd=sd, env=env)
            merged = False
            for branch in ("main", "master"):
                try:
                    subprocess.check_call(
                        ["git", "merge", "--no-edit", "--strategy-option=theirs",
                         "origin/{}".format(branch)],
                        cwd=sd, env=env)
                    merged = True
                    break
                except subprocess.CalledProcessError:
                    continue
            if not merged:
                self.status_v.set("Merge failed. Resolve conflicts in:\n{}".format(sd))
                self.status_lbl.config(fg=DANGER)
                return
            pf = os.path.join(sd, "jshortcuts.json")
            if os.path.exists(pf):
                shutil.copy(pf, DATA_FILE)
                data = load_data()
                sc  = len(data.get("shortcuts", []))
                ap  = len(data.get("apps", {}))
                ma  = len(data.get("my_apps", []))
                self.status_v.set(
                    "Pull complete. Data file updated.\n"
                    "Loaded: {} shortcuts  |  {} app groups  |  {} my apps".format(sc, ap, ma))
                self.status_lbl.config(fg=SUCCESS)
                # Notify parent to refresh all tabs
                if self._on_pull_success:
                    self._on_pull_success()
            else:
                self.status_v.set("Pulled OK but jshortcuts.json not found in repo.")
                self.status_lbl.config(fg=WARNING)
        except subprocess.CalledProcessError as e:
            self.status_v.set("Pull failed: {}".format(e))
            self.status_lbl.config(fg=DANGER)


# =============================================================================
# Open-file dialog
# =============================================================================

KNOWN_EDITORS = [
    ("code",     "VS Code"),
    ("gedit",    "gedit (GNOME)"),
    ("mousepad", "Mousepad (XFCE)"),
    ("kate",     "Kate (KDE)"),
    ("pluma",    "Pluma (MATE)"),
    ("xed",      "Xed (Cinnamon)"),
    ("geany",    "Geany"),
    ("xdg-open", "System default"),
    ("nano",     "nano (terminal)"),
]


class OpenFileDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Open Data File")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.focus_set()
        W, H = 420, 320
        self.geometry("{}x{}".format(W, H))
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry("{}x{}+{}+{}".format(W, H, px, py))
        self._build()

    def _build(self):
        h = tk.Frame(self, bg=ACCENT2, height=50)
        h.pack(side="top", fill="x"); h.pack_propagate(False)
        tk.Label(h, text="  Open Data File With...",
                 bg=ACCENT2, fg="white", font=FB, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        bb = tk.Frame(self, bg=BG, height=56)
        bb.pack(side="bottom", fill="x"); bb.pack_propagate(False)
        tk.Button(bb, text="  Cancel  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FN, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 16), pady=12)
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        body = tk.Frame(self, bg=BG, padx=20, pady=12)
        body.pack(side="top", fill="both", expand=True)

        tk.Label(body, text=DATA_FILE, bg=BG, fg=FG_DIM, font=FT2,
                 anchor="w", wraplength=380).pack(fill="x", pady=(0, 10))

        available = [(cmd, lbl) for cmd, lbl in KNOWN_EDITORS if shutil.which(cmd)]
        if not available:
            tk.Label(body, text="No known editor found on this system.\nInstall VS Code, gedit, or nano.",
                     bg=BG, fg=DANGER, font=FN).pack(pady=20)
            return

        self._var = tk.IntVar(value=0)
        for i, (cmd, lbl) in enumerate(available):
            rb = tk.Radiobutton(body, text="  {}  ({})".format(lbl, cmd),
                                variable=self._var, value=i,
                                bg=BG, fg=FG, font=FN,
                                selectcolor=BG3, activebackground=BG,
                                activeforeground=FG,
                                indicatoron=True, cursor="hand2")
            rb.pack(anchor="w", pady=2)

        self._available = available

        tk.Button(body, text="  Open  ", command=self._open,
                  bg=ACCENT, fg="white", font=FB, relief="flat",
                  padx=14, pady=6, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white"
                  ).pack(anchor="e", pady=(10, 0))

        self.bind("<Return>", lambda _: self._open())
        self.bind("<Escape>", lambda _: self.destroy())

    def _open(self):
        idx = self._var.get()
        if idx < 0 or idx >= len(self._available):
            return
        cmd, _ = self._available[idx]
        try:
            subprocess.Popen([cmd, DATA_FILE],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             stdin=subprocess.DEVNULL,
                             start_new_session=True)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)
            return
        self.destroy()


# =============================================================================
# AllMyApps entry dialog
# =============================================================================

BUILTIN_FIELDS = [
    ("name",        "App Name",                True),
    ("description", "What it does / Purpose",  True),
    ("repo_url",    "Repo / Website URL",       False),
    ("yt_how_to",   "YouTube: How-to-install",  False),
    ("yt_desc",     "YouTube: Description/demo",False),
]


class MyAppDialog(tk.Toplevel):
    """Dialog to add or edit an entry in All My Apps."""

    def __init__(self, parent, app=None):
        super().__init__(parent)
        self.result = None
        mode = "Edit App" if app else "Add App"
        self.title(mode)
        self.configure(bg=BG)
        self.resizable(True, True)
        self.grab_set()
        self.focus_set()
        W, H = 580, 600
        self.geometry("{}x{}".format(W, H))
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - W) // 2
        py = parent.winfo_y() + (parent.winfo_height() - H) // 2
        self.geometry("{}x{}+{}+{}".format(W, H, max(0,px), max(0,py)))
        self._app = app or {}
        self._custom_vars = []   # list of (key_var, val_var, row_frame)
        self._build()

    def _lbl(self, p, t, req=False):
        row = tk.Frame(p, bg=BG2)
        row.pack(fill="x", pady=(10, 2))
        tk.Label(row, text=t, bg=BG2, fg=FG_DIM, font=FS, anchor="w").pack(side="left")
        if req:
            tk.Label(row, text=" *", bg=BG2, fg=DANGER, font=FS).pack(side="left")

    def _ent(self, p, val=""):
        v = tk.StringVar(value=val)
        tk.Entry(p, textvariable=v, bg=BG3, fg=FG, font=FN, relief="flat",
                 insertbackground=ACCENT, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT
                 ).pack(fill="x", ipady=6)
        return v

    def _build(self):
        h = tk.Frame(self, bg=ACCENT2, height=50)
        h.pack(side="top", fill="x"); h.pack_propagate(False)
        tk.Label(h, text="  " + self.title(),
                 bg=ACCENT2, fg="white", font=FB, anchor="w"
                 ).pack(side="left", padx=14, pady=13)

        bb = tk.Frame(self, bg=BG, height=64)
        bb.pack(side="bottom", fill="x"); bb.pack_propagate(False)
        tk.Button(bb, text="  Cancel  ", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FN, relief="flat",
                  padx=14, pady=8, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(side="right", padx=(6, 18), pady=14)
        tk.Button(bb, text="  Save  ", command=self._save,
                  bg=ACCENT, fg="white", font=FB, relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white"
                  ).pack(side="right", pady=14)
        tk.Frame(self, bg=BG3, height=1).pack(side="bottom", fill="x")

        # Scrollable form
        sf = ScrollFrame(self, bg=BG2)
        sf.pack(side="top", fill="both", expand=True, padx=14, pady=(8, 0))
        form = sf.inner

        form.configure(padx=22, pady=8)

        # Built-in fields
        self._field_vars = {}
        a = self._app
        for key, label, required in BUILTIN_FIELDS:
            self._lbl(form, label, required)
            self._field_vars[key] = self._ent(form, a.get(key, ""))

        # Custom fields section
        tk.Frame(form, bg=BG3, height=1).pack(fill="x", pady=(18, 6))
        tk.Label(form, text="Custom Fields  (add any extra info you want)",
                 bg=BG2, fg=FG_DIM, font=FS, anchor="w").pack(fill="x")

        self._custom_frame = tk.Frame(form, bg=BG2)
        self._custom_frame.pack(fill="x")

        # Load existing custom fields
        for cf in a.get("custom_fields", []):
            self._add_custom_row(cf.get("key", ""), cf.get("value", ""))

        tk.Button(form, text="+ Add Custom Field", command=self._add_custom_row,
                  bg=BG3, fg=FG_DIM, font=FS, relief="flat",
                  padx=10, pady=4, cursor="hand2",
                  activebackground=BG2, activeforeground=FG
                  ).pack(anchor="w", pady=(6, 0))

        sf.bind_scroll_recursive(form)
        self.bind("<Escape>", lambda _: self.destroy())

    def _add_custom_row(self, key="", value=""):
        row = tk.Frame(self._custom_frame, bg=BG2)
        row.pack(fill="x", pady=(6, 0))

        kv = tk.StringVar(value=key)
        vv = tk.StringVar(value=value)

        tk.Label(row, text="Field name:", bg=BG2, fg=FG_DIM, font=FT2
                 ).pack(side="left")
        tk.Entry(row, textvariable=kv, bg=BG3, fg=FG, font=FS,
                 relief="flat", width=14, insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT
                 ).pack(side="left", padx=(4, 8), ipady=4)
        tk.Label(row, text="Value:", bg=BG2, fg=FG_DIM, font=FT2
                 ).pack(side="left")
        tk.Entry(row, textvariable=vv, bg=BG3, fg=FG, font=FS,
                 relief="flat", insertbackground=ACCENT,
                 highlightthickness=1, highlightbackground=BG3,
                 highlightcolor=ACCENT
                 ).pack(side="left", fill="x", expand=True, padx=(4, 8), ipady=4)

        entry = [kv, vv, row]
        self._custom_vars.append(entry)

        def remove(e=entry):
            e[2].destroy()
            self._custom_vars.remove(e)

        tk.Button(row, text="x", command=remove,
                  bg=DANGER, fg="white", font=FT2, relief="flat",
                  padx=5, pady=2, cursor="hand2"
                  ).pack(side="left")

    def _save(self):
        result = {}
        for key, label, required in BUILTIN_FIELDS:
            val = self._field_vars[key].get().strip()
            if required and not val:
                messagebox.showwarning("Required",
                    "'{}' is required.".format(label), parent=self)
                return
            result[key] = val

        custom = []
        for kv, vv, _ in self._custom_vars:
            k = kv.get().strip()
            v = vv.get().strip()
            if k:
                custom.append({"key": k, "value": v})
        result["custom_fields"] = custom
        self.result = result
        self.destroy()


# =============================================================================
# Main application
# =============================================================================

class JShortcutsApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("{} v{}".format(APP_NAME, VERSION))
        self.configure(bg=BG)
        self.geometry("960x660")
        self.minsize(700, 480)

        self._cat_colors   = {}
        self._sel_id       = None           # selected shortcut id
        self._sc_rows      = {}             # id -> (row,bar,tf)
        self._sel_cat      = tk.StringVar(value="All")
        self._search_v     = tk.StringVar()
        self._search_v.trace_add("write", lambda *_: self._refresh_shortcuts())

        self._sel_app      = None           # selected app name (Apps tab)
        self._sel_app_scid = None           # selected shortcut id in Apps tab
        self._app_sc_rows  = {}
        self._app_rows_map = {}             # app_name -> (row,bar,inner)

        self._sel_myapp_idx = None          # index in my_apps list
        self._myapp_rows   = {}             # idx -> row_frame

        self._apply_style()
        self._build_ui()
        self._refresh_all()

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry("960x660+{}+{}".format((sw-960)//2, (sh-660)//2))
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    # -------------------------------------------------------------------------
    # Styles
    # -------------------------------------------------------------------------

    def _apply_style(self):
        s = ttk.Style()
        s.theme_use("clam")
        s.configure("Dark.TNotebook", background=BG2, borderwidth=0,
                    tabmargins=[0,0,0,0])
        s.configure("Dark.TNotebook.Tab", background=BG2, foreground=FG_DIM,
                    padding=[16,8], font=FN, borderwidth=0)
        s.map("Dark.TNotebook.Tab",
              background=[("selected", BG), ("active", BG3)],
              foreground=[("selected", FG), ("active", FG)])
        s.configure("TCombobox", fieldbackground=BG3, background=BG3,
                    foreground=FG, selectbackground=ACCENT,
                    selectforeground="white", arrowcolor=FG_DIM,
                    bordercolor=BG3, lightcolor=BG3, darkcolor=BG3)

    # -------------------------------------------------------------------------
    # Top-level UI
    # -------------------------------------------------------------------------

    def _build_ui(self):
        # Status bar
        sb = tk.Frame(self, bg=BG2, height=28)
        sb.pack(side="bottom", fill="x"); sb.pack_propagate(False)
        tk.Label(sb, text="  {} v{}  |  {}  |  {}".format(
                     APP_NAME, VERSION, COMPANY, GITHUB),
                 bg=BG2, fg=FG_DIM, font=FT2, anchor="w"
                 ).pack(side="left", pady=6, padx=4)
        tk.Label(sb, text="data: {}  ".format(DATA_FILE),
                 bg=BG2, fg=FG_DIM, font=FT2, anchor="e"
                 ).pack(side="right", pady=6)

        # Top bar
        top = tk.Frame(self, bg=BG2, height=56)
        top.pack(side="top", fill="x"); top.pack_propagate(False)

        tk.Label(top, text=APP_NAME, bg=BG2, fg=FG, font=FT
                 ).pack(side="left", padx=(16,0), pady=10)
        tk.Label(top, text="  my keyboard shortcuts", bg=BG2, fg=FG_DIM, font=FS
                 ).pack(side="left", pady=14)

        # Right side buttons
        for lbl, cmd in [("  Open File ", self._open_file),
                         ("  GitHub ",    self._open_github)]:
            tk.Button(top, text=lbl, command=cmd,
                      bg=BG3, fg=FG_DIM, font=FS, relief="flat",
                      padx=8, pady=5, cursor="hand2",
                      activebackground=ACCENT2, activeforeground=FG
                      ).pack(side="right", padx=(4,4), pady=12)

        # Search
        sf = tk.Frame(top, bg=BG3, padx=8, pady=4)
        sf.pack(side="right", padx=8, pady=10)
        tk.Label(sf, text="search:", bg=BG3, fg=FG_DIM, font=FS).pack(side="left")
        tk.Entry(sf, textvariable=self._search_v,
                 bg=BG3, fg=FG, font=FN, relief="flat", width=18,
                 insertbackground=ACCENT).pack(side="left", padx=(4,0))

        # Notebook
        self._nb = ttk.Notebook(self, style="Dark.TNotebook")
        self._nb.pack(side="top", fill="both", expand=True)

        self._tab_sc  = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_sc,  text="  Shortcuts  ")
        self._build_shortcuts_tab()

        self._tab_ap  = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_ap,  text="  Apps  ")
        self._build_apps_tab()

        self._tab_ma  = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_ma,  text="  All My Apps  ")
        self._build_myapps_tab()

        self._tab_cli = tk.Frame(self._nb, bg=BG)
        self._nb.add(self._tab_cli, text="  CLI Reference  ")
        self._build_cli_tab()

    # =========================================================================
    # TAB 1: Shortcuts
    # =========================================================================

    def _build_shortcuts_tab(self):
        t = self._tab_sc

        # Sidebar
        self._sc_sidebar = tk.Frame(t, bg=BG2, width=170)
        self._sc_sidebar.pack(side="left", fill="y")
        self._sc_sidebar.pack_propagate(False)
        tk.Label(self._sc_sidebar, text="CATEGORIES", bg=BG2, fg=FG_DIM,
                 font=FT2, anchor="w").pack(fill="x", padx=12, pady=(14,6))
        self._cat_frame = tk.Frame(self._sc_sidebar, bg=BG2)
        self._cat_frame.pack(fill="x")

        # Right pane
        right = tk.Frame(t, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Toolbar
        bar = tk.Frame(right, bg=BG, pady=7, padx=14)
        bar.pack(side="top", fill="x")
        self._sc_count = tk.Label(bar, text="", bg=BG, fg=FG_DIM, font=FS)
        self._sc_count.pack(side="left")
        tk.Label(bar, text="double-click to edit", bg=BG, fg=FG_DIM, font=FT2
                 ).pack(side="left", padx=10)
        for txt, cmd, clr in [
            ("Delete", self._del_sc,  DANGER),
            ("Edit",   self._edit_sc, ACCENT),
            ("+ Add",  self._add_sc,  SUCCESS),
        ]:
            tk.Button(bar, text=txt, command=cmd,
                      bg=clr, fg="white", font=FS,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=3)

        # Scrollable list using ScrollFrame
        self._sc_sf = ScrollFrame(right, bg=BG)
        self._sc_sf.pack(side="top", fill="both", expand=True)

    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------

    def _build_sidebar(self, cats):
        for w in self._cat_frame.winfo_children():
            w.destroy()
        for cat in ["All"] + cats:
            sel = (self._sel_cat.get() == cat)
            col = self._cat_colors.get(cat, ACCENT) if cat != "All" else ACCENT
            bg  = BG3 if sel else BG2
            fg  = col if sel else FG_DIM
            tk.Button(self._cat_frame, text="  " + cat,
                      command=lambda c=cat: self._sel_cat_click(c),
                      bg=bg, fg=fg, font=FS, relief="flat",
                      anchor="w", padx=8, pady=5, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(fill="x")

    def _sel_cat_click(self, cat):
        self._sel_cat.set(cat)
        self._refresh_shortcuts()

    # -------------------------------------------------------------------------
    # Refresh shortcuts
    # -------------------------------------------------------------------------

    def _refresh_shortcuts(self):
        data = load_data()
        scs  = data["shortcuts"]
        cats = []
        for s in scs:
            if s["category"] not in cats:
                cats.append(s["category"])
        for i, c in enumerate(cats):
            self._cat_colors[c] = CAT_COLORS[i % len(CAT_COLORS)]
        self._build_sidebar(cats)

        sel  = self._sel_cat.get()
        qry  = self._search_v.get().strip().lower()
        filt = scs
        if sel != "All":
            filt = [s for s in filt if s["category"] == sel]
        if qry:
            filt = [s for s in filt if
                    qry in s["keys"].lower() or
                    qry in s["description"].lower() or
                    qry in s.get("notes","").lower() or
                    qry in s["category"].lower()]

        self._sc_count.config(text="{} shortcut(s)".format(len(filt)))
        self._render_shortcuts(filt)

    def _render_shortcuts(self, scs):
        for w in self._sc_sf.inner.winfo_children():
            w.destroy()
        self._sel_id  = None
        self._sc_rows = {}

        if not scs:
            tk.Label(self._sc_sf.inner,
                     text="\n  No shortcuts found.\n  Click '+ Add' to create one.",
                     bg=BG, fg=FG_DIM, font=FN, justify="left"
                     ).pack(padx=24, pady=40)
            return

        grouped = {}
        for s in scs:
            grouped.setdefault(s["category"], []).append(s)

        for cat, items in grouped.items():
            col = self._cat_colors.get(cat, ACCENT)
            hdr = tk.Frame(self._sc_sf.inner, bg=BG)
            hdr.pack(fill="x", padx=16, pady=(14,5))
            tk.Frame(hdr, bg=col, width=4, height=16).pack(side="left")
            tk.Label(hdr, text="  " + cat.upper(), bg=BG, fg=col,
                     font=("JetBrains Mono", 9, "bold")).pack(side="left")
            self._sc_sf.bind_scroll_recursive(hdr)
            for s in items:
                self._make_sc_row(s, col)

    def _make_sc_row(self, s, col):
        sid = s["id"]
        sel = (self._sel_id == sid)
        row = tk.Frame(self._sc_sf.inner, bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)
        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")
        tk.Label(row, text=" {} ".format(sid), bg=BG3, fg=FG_DIM, font=FS
                 ).pack(side="left", padx=(5,0), pady=9)
        kl = tk.Label(row, text="  {}  ".format(s["keys"]),
                      bg=BG3, fg=col, font=FB, padx=3)
        kl.pack(side="left", padx=7, pady=9)
        tf = tk.Frame(row, bg=row["bg"])
        tf.pack(side="left", fill="both", expand=True, pady=7)
        tk.Label(tf, text=s["description"], bg=tf["bg"], fg=FG, font=FN, anchor="w").pack(fill="x")
        if s.get("notes"):
            tk.Label(tf, text=s["notes"], bg=tf["bg"], fg=FG_DIM, font=FS, anchor="w").pack(fill="x")

        def click(_e, i=sid): self._sel_sc_row(i)
        def dbl(_e, i=sid):
            self._sel_sc_row(i)
            self._edit_sc()
        def enter(_e, r=row, t=tf):
            if self._sel_id != sid:
                r.config(bg=BG3); t.config(bg=BG3)
        def leave(_e, r=row, b=bar, t=tf):
            if self._sel_id == sid:
                r.config(bg=BG_SEL); b.config(bg=ACCENT); t.config(bg=BG_SEL)
            else:
                r.config(bg=BG2); b.config(bg=BG3); t.config(bg=BG2)

        for w in (row, kl, tf):
            w.bind("<Button-1>", click)
            w.bind("<Double-1>", dbl)
            w.bind("<Enter>",    enter)
            w.bind("<Leave>",    leave)
        self._sc_sf.bind_scroll_recursive(row)
        self._sc_rows[sid] = (row, bar, tf)

    def _sel_sc_row(self, sid):
        if self._sel_id and self._sel_id in self._sc_rows:
            r, b, t = self._sc_rows[self._sel_id]
            r.config(bg=BG2); b.config(bg=BG3); t.config(bg=BG2)
        self._sel_id = sid
        if sid in self._sc_rows:
            r, b, t = self._sc_rows[sid]
            r.config(bg=BG_SEL); b.config(bg=ACCENT); t.config(bg=BG_SEL)

    # -------------------------------------------------------------------------
    # Shortcuts CRUD
    # -------------------------------------------------------------------------

    def _sc_cats(self):
        data = load_data()
        seen = []
        for s in data["shortcuts"]:
            if s["category"] not in seen:
                seen.append(s["category"])
        return seen

    def _add_sc(self):
        dlg = ShortcutDialog(self, "Add Shortcut", self._sc_cats())
        self.wait_window(dlg)
        if dlg.result:
            data = load_data()
            data["shortcuts"].append({"id": data["next_id"], **dlg.result})
            data["next_id"] += 1
            save_data(data)
            self._refresh_shortcuts()

    def _edit_sc(self):
        if not self._sel_id:
            messagebox.showinfo("No selection",
                "Click a row to select it, then click Edit\n(or double-click any row).",
                parent=self)
            return
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == self._sel_id), None)
        if not match:
            return
        dlg = ShortcutDialog(self, "Edit Shortcut", self._sc_cats(), match)
        self.wait_window(dlg)
        if dlg.result:
            match.update(dlg.result)
            save_data(data)
            self._refresh_shortcuts()

    def _del_sc(self):
        if not self._sel_id:
            messagebox.showinfo("No selection",
                "Click a row to select it, then click Delete.", parent=self)
            return
        sid   = self._sel_id
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == sid), None)
        if not match:
            return
        if messagebox.askyesno("Delete Shortcut",
                "Delete #{}?\n\n{}  --  {}".format(sid, match["keys"], match["description"]),
                parent=self):
            data["shortcuts"] = [s for s in data["shortcuts"] if s["id"] != sid]
            save_data(data)
            self._sel_id = None
            self._refresh_shortcuts()

    # =========================================================================
    # TAB 2: Apps
    # =========================================================================

    def _build_apps_tab(self):
        t = self._tab_ap

        # Left panel: app list
        left = tk.Frame(t, bg=BG2, width=200)
        left.pack(side="left", fill="y"); left.pack_propagate(False)

        tk.Label(left, text="APPS", bg=BG2, fg=FG_DIM, font=FT2, anchor="w"
                 ).pack(fill="x", padx=12, pady=(14,4))

        atb = tk.Frame(left, bg=BG2)
        atb.pack(fill="x", padx=8, pady=(0,6))
        tk.Button(atb, text="+ App", command=self._add_app,
                  bg=SUCCESS, fg="white", font=FS, relief="flat",
                  padx=8, pady=3, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="left")
        tk.Button(atb, text="Delete", command=self._del_app,
                  bg=DANGER, fg="white", font=FS, relief="flat",
                  padx=8, pady=3, cursor="hand2",
                  activebackground=BG3, activeforeground=FG
                  ).pack(side="right")

        self._app_list_frame = tk.Frame(left, bg=BG2)
        self._app_list_frame.pack(fill="both", expand=True)

        tk.Frame(t, bg=BG3, width=1).pack(side="left", fill="y")

        # Right panel
        right = tk.Frame(t, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        rtb = tk.Frame(right, bg=BG, pady=7, padx=14)
        rtb.pack(side="top", fill="x")
        self._app_name_lbl = tk.Label(rtb, text="Select an app",
                                      bg=BG, fg=FG_DIM, font=FB)
        self._app_name_lbl.pack(side="left")
        for txt, cmd, clr in [
            ("Delete", self._del_app_sc,  DANGER),
            ("Edit",   self._edit_app_sc, ACCENT),
            ("+ Shortcut", self._add_app_sc, SUCCESS),
        ]:
            tk.Button(rtb, text=txt, command=cmd,
                      bg=clr, fg="white", font=FS, relief="flat",
                      padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=3)

        self._app_sc_sf = ScrollFrame(right, bg=BG)
        self._app_sc_sf.pack(side="top", fill="both", expand=True)

    # -------------------------------------------------------------------------
    # Apps list rendering
    # -------------------------------------------------------------------------

    def _refresh_apps(self):
        for w in self._app_list_frame.winfo_children():
            w.destroy()
        self._app_rows_map = {}
        apps = load_data().get("apps", {})
        if not apps:
            tk.Label(self._app_list_frame,
                     text="\nNo apps yet.\nClick '+ App' to add.",
                     bg=BG2, fg=FG_DIM, font=FS, justify="left"
                     ).pack(padx=12, pady=10)
        else:
            for name in sorted(apps.keys()):
                self._make_app_row(name, apps[name])
        if self._sel_app:
            self._render_app_shortcuts(self._sel_app)

    def _make_app_row(self, name, app_data):
        count = len(app_data.get("shortcuts", []))
        sel   = (self._sel_app == name)
        # The row IS the full-width clickable area
        row   = tk.Frame(self._app_list_frame,
                         bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", pady=2, padx=4)

        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")

        inner = tk.Frame(row, bg=row["bg"])
        inner.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        tk.Label(inner, text=name, bg=inner["bg"], fg=FG, font=FB, anchor="w"
                 ).pack(fill="x")
        tk.Label(inner, text="{} shortcut(s)".format(count),
                 bg=inner["bg"], fg=FG_DIM, font=FT2, anchor="w"
                 ).pack(fill="x")

        # Bind click to the ENTIRE row (row + inner + all children)
        def click(_e, n=name):
            self._select_app(n)

        for widget in (row, bar, inner):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>",  lambda _e, r=row, i=inner:
                (r.config(bg=BG3), i.config(bg=BG3)) if self._sel_app != name else None)
            widget.bind("<Leave>",  lambda _e, r=row, i=inner, n2=name:
                (r.config(bg=BG_SEL if self._sel_app==n2 else BG2),
                 i.config(bg=BG_SEL if self._sel_app==n2 else BG2)))
        for child in inner.winfo_children():
            child.bind("<Button-1>", click)

        self._app_rows_map[name] = (row, bar, inner)

    def _select_app(self, name):
        if self._sel_app and self._sel_app in self._app_rows_map:
            r, b, i = self._app_rows_map[self._sel_app]
            r.config(bg=BG2); b.config(bg=BG3); i.config(bg=BG2)
        self._sel_app = name
        self._sel_app_scid = None
        self._app_sc_rows  = {}
        if name in self._app_rows_map:
            r, b, i = self._app_rows_map[name]
            r.config(bg=BG_SEL); b.config(bg=ACCENT); i.config(bg=BG_SEL)
        self._app_name_lbl.config(text=name, fg=FG)
        self._render_app_shortcuts(name)

    def _render_app_shortcuts(self, name):
        for w in self._app_sc_sf.inner.winfo_children():
            w.destroy()
        self._app_sc_rows  = {}
        self._sel_app_scid = None
        apps = load_data().get("apps", {})
        scs  = apps.get(name, {}).get("shortcuts", [])
        if not scs:
            tk.Label(self._app_sc_sf.inner,
                     text="\n  No shortcuts for this app.\n  Click '+ Shortcut' to add one.",
                     bg=BG, fg=FG_DIM, font=FN, justify="left"
                     ).pack(padx=24, pady=30)
            return
        app_list = sorted(apps.keys())
        idx = app_list.index(name) if name in app_list else 0
        col = CAT_COLORS[idx % len(CAT_COLORS)]
        hdr = tk.Frame(self._app_sc_sf.inner, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(12,5))
        tk.Frame(hdr, bg=col, width=4, height=16).pack(side="left")
        tk.Label(hdr, text="  " + name.upper(), bg=BG, fg=col,
                 font=("JetBrains Mono",9,"bold")).pack(side="left")
        self._app_sc_sf.bind_scroll_recursive(hdr)
        for sc in scs:
            self._make_app_sc_row(sc, col)

    def _make_app_sc_row(self, sc, col):
        sid = sc["id"]
        sel = (self._sel_app_scid == sid)
        row = tk.Frame(self._app_sc_sf.inner, bg=BG_SEL if sel else BG2, cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)
        bar = tk.Frame(row, bg=ACCENT if sel else BG3, width=4)
        bar.pack(side="left", fill="y")
        tk.Label(row, text=" {} ".format(sid), bg=BG3, fg=FG_DIM, font=FS
                 ).pack(side="left", padx=(5,0), pady=9)
        kl = tk.Label(row, text="  {}  ".format(sc["keys"]),
                      bg=BG3, fg=col, font=FB, padx=3)
        kl.pack(side="left", padx=7, pady=9)
        tf = tk.Frame(row, bg=row["bg"])
        tf.pack(side="left", fill="both", expand=True, pady=7)
        tk.Label(tf, text=sc["description"], bg=tf["bg"], fg=FG, font=FN, anchor="w").pack(fill="x")
        if sc.get("notes"):
            tk.Label(tf, text=sc["notes"], bg=tf["bg"], fg=FG_DIM, font=FS, anchor="w").pack(fill="x")

        def click(_e, i=sid): self._sel_app_sc_row(i)
        def dbl(_e, i=sid):
            self._sel_app_sc_row(i)
            self._edit_app_sc()
        def enter(_e, r=row, t=tf):
            if self._sel_app_scid != sid:
                r.config(bg=BG3); t.config(bg=BG3)
        def leave(_e, r=row, b=bar, t=tf):
            if self._sel_app_scid == sid:
                r.config(bg=BG_SEL); b.config(bg=ACCENT); t.config(bg=BG_SEL)
            else:
                r.config(bg=BG2); b.config(bg=BG3); t.config(bg=BG2)

        for w in (row, kl, tf):
            w.bind("<Button-1>", click)
            w.bind("<Double-1>", dbl)
            w.bind("<Enter>",    enter)
            w.bind("<Leave>",    leave)
        self._app_sc_sf.bind_scroll_recursive(row)
        self._app_sc_rows[sid] = (row, bar, tf)

    def _sel_app_sc_row(self, sid):
        if self._sel_app_scid and self._sel_app_scid in self._app_sc_rows:
            r, b, t = self._app_sc_rows[self._sel_app_scid]
            r.config(bg=BG2); b.config(bg=BG3); t.config(bg=BG2)
        self._sel_app_scid = sid
        if sid in self._app_sc_rows:
            r, b, t = self._app_sc_rows[sid]
            r.config(bg=BG_SEL); b.config(bg=ACCENT); t.config(bg=BG_SEL)

    # -------------------------------------------------------------------------
    # Apps CRUD
    # -------------------------------------------------------------------------

    def _add_app(self):
        name = self._mini_input("Add App", "App name (e.g. VS Code, Firefox):")
        if not name:
            return
        data = load_data()
        if name in data["apps"]:
            messagebox.showwarning("Exists",
                "'{}' already exists.".format(name), parent=self)
            return
        data["apps"][name] = {"shortcuts": [], "next_id": 1}
        save_data(data)
        self._refresh_apps()
        # Re-render so new row is visible before selecting
        self.update_idletasks()
        self._select_app(name)

    def _del_app(self):
        if not self._sel_app:
            messagebox.showinfo("No selection",
                "Click an app to select it first.", parent=self)
            return
        name = self._sel_app
        if messagebox.askyesno("Delete App",
                "Delete app '{}' and all its shortcuts?".format(name), parent=self):
            data = load_data()
            data["apps"].pop(name, None)
            save_data(data)
            self._sel_app = None
            for w in self._app_sc_sf.inner.winfo_children():
                w.destroy()
            self._app_name_lbl.config(text="Select an app", fg=FG_DIM)
            self._refresh_apps()

    def _add_app_sc(self):
        if not self._sel_app:
            messagebox.showinfo("No app", "Click an app in the left panel first.", parent=self)
            return
        dlg = ShortcutDialog(self, "Add Shortcut -- " + self._sel_app, [])
        self.wait_window(dlg)
        if dlg.result:
            data = load_data()
            app  = data["apps"].setdefault(self._sel_app, {"shortcuts":[],"next_id":1})
            entry = {"id": app.get("next_id", 1), **dlg.result}
            entry["category"] = self._sel_app
            app["shortcuts"].append(entry)
            app["next_id"] = app.get("next_id", 1) + 1
            save_data(data)
            self._refresh_apps()

    def _edit_app_sc(self):
        if not self._sel_app or not self._sel_app_scid:
            messagebox.showinfo("No selection",
                "Select an app and a shortcut row first.", parent=self)
            return
        data  = load_data()
        app   = data["apps"].get(self._sel_app, {})
        match = next((s for s in app.get("shortcuts",[]) if s["id"]==self._sel_app_scid), None)
        if not match:
            return
        dlg = ShortcutDialog(self, "Edit Shortcut -- " + self._sel_app, [], match)
        self.wait_window(dlg)
        if dlg.result:
            match.update(dlg.result)
            match["category"] = self._sel_app
            save_data(data)
            self._refresh_apps()

    def _del_app_sc(self):
        if not self._sel_app or not self._sel_app_scid:
            messagebox.showinfo("No selection",
                "Select an app and a shortcut row first.", parent=self)
            return
        sid   = self._sel_app_scid
        data  = load_data()
        app   = data["apps"].get(self._sel_app, {})
        match = next((s for s in app.get("shortcuts",[]) if s["id"]==sid), None)
        if not match:
            return
        if messagebox.askyesno("Delete Shortcut",
                "Delete #{}?\n{} -- {}".format(sid, match["keys"], match["description"]),
                parent=self):
            app["shortcuts"] = [s for s in app["shortcuts"] if s["id"] != sid]
            save_data(data)
            self._sel_app_scid = None
            self._refresh_apps()

    # =========================================================================
    # TAB 3: All My Apps
    # =========================================================================

    def _build_myapps_tab(self):
        t = self._tab_ma

        # Toolbar
        bar = tk.Frame(t, bg=BG, pady=8, padx=16)
        bar.pack(side="top", fill="x")
        tk.Label(bar, text="All My Apps  --  your personal app directory",
                 bg=BG, fg=FG_DIM, font=FS).pack(side="left")
        for txt, cmd, clr in [
            ("Delete", self._del_myapp,  DANGER),
            ("Edit",   self._edit_myapp, ACCENT),
            ("+ App",  self._add_myapp,  SUCCESS),
        ]:
            tk.Button(bar, text=txt, command=cmd,
                      bg=clr, fg="white", font=FS, relief="flat",
                      padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG
                      ).pack(side="right", padx=3)

        self._ma_sf = ScrollFrame(t, bg=BG)
        self._ma_sf.pack(side="top", fill="both", expand=True)

    def _refresh_myapps(self):
        for w in self._ma_sf.inner.winfo_children():
            w.destroy()
        self._myapp_rows    = {}
        self._sel_myapp_idx = None
        data = load_data()
        apps = data.get("my_apps", [])

        if not apps:
            tk.Label(self._ma_sf.inner,
                     text="\n  No apps yet.\n  Click '+ App' to add an entry to your app directory.",
                     bg=BG, fg=FG_DIM, font=FN, justify="left"
                     ).pack(padx=24, pady=40)
            return

        for idx, app in enumerate(apps):
            self._make_myapp_card(idx, app)

    def _make_myapp_card(self, idx, app):
        sel = (self._sel_myapp_idx == idx)
        col = CAT_COLORS[idx % len(CAT_COLORS)]

        card = tk.Frame(self._ma_sf.inner,
                        bg=BG_SEL if sel else BG2,
                        cursor="hand2")
        card.pack(fill="x", padx=16, pady=5)

        # Left accent
        tk.Frame(card, bg=ACCENT if sel else col, width=5).pack(side="left", fill="y")

        body = tk.Frame(card, bg=card["bg"], padx=14, pady=10)
        body.pack(side="left", fill="both", expand=True)

        # Top row: name + indicators
        top_row = tk.Frame(body, bg=body["bg"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=app.get("name","(unnamed)"),
                 bg=body["bg"], fg=FG, font=FB).pack(side="left")

        # Tag pills for which optional fields are filled
        for field, label, req in BUILTIN_FIELDS:
            if not req and app.get(field, "").strip():
                pill = tk.Label(top_row,
                                text=" {} ".format(label.split(":")[0]),
                                bg=col, fg=BG, font=FT2)
                pill.pack(side="left", padx=(6,0), pady=2)

        for cf in app.get("custom_fields", []):
            if cf.get("key") and cf.get("value"):
                pill = tk.Label(top_row, text=" {} ".format(cf["key"]),
                                bg=BG3, fg=FG_DIM, font=FT2)
                pill.pack(side="left", padx=(4,0), pady=2)

        # Description
        desc = app.get("description","").strip()
        if desc:
            tk.Label(body, text=desc, bg=body["bg"], fg=FG_DIM,
                     font=FS, anchor="w", wraplength=700, justify="left"
                     ).pack(fill="x", pady=(4,0))

        # Links
        for field in ("repo_url","yt_how_to","yt_desc"):
            val = app.get(field,"").strip()
            if val:
                lbl_map = {"repo_url":"Repo","yt_how_to":"YT How-to","yt_desc":"YT Demo"}
                lrow = tk.Frame(body, bg=body["bg"])
                lrow.pack(fill="x", pady=(2,0))
                tk.Label(lrow, text=lbl_map[field]+":",
                         bg=body["bg"], fg=FG_DIM, font=FT2).pack(side="left")
                lnk = tk.Label(lrow, text="  "+val,
                               bg=body["bg"], fg=ACCENT, font=FT2,
                               cursor="hand2")
                lnk.pack(side="left")
                lnk.bind("<Button-1>", lambda _e, u=val: self._open_url(u))

        # Custom fields
        for cf in app.get("custom_fields",[]):
            k = cf.get("key","").strip()
            v = cf.get("value","").strip()
            if k and v:
                crow = tk.Frame(body, bg=body["bg"])
                crow.pack(fill="x", pady=(2,0))
                tk.Label(crow, text="{}:".format(k),
                         bg=body["bg"], fg=FG_DIM, font=FT2).pack(side="left")
                tk.Label(crow, text="  "+v,
                         bg=body["bg"], fg=FG, font=FT2, anchor="w"
                         ).pack(side="left")

        def click(_e, i=idx):
            self._sel_myapp(i)

        for w in (card, body, top_row):
            w.bind("<Button-1>", click)
        for child in body.winfo_children():
            child.bind("<Button-1>", click)
        self._ma_sf.bind_scroll_recursive(card)
        self._myapp_rows[idx] = card

    def _sel_myapp(self, idx):
        if self._sel_myapp_idx is not None and self._sel_myapp_idx in self._myapp_rows:
            self._myapp_rows[self._sel_myapp_idx].config(bg=BG2)
        self._sel_myapp_idx = idx
        if idx in self._myapp_rows:
            self._myapp_rows[idx].config(bg=BG_SEL)

    def _add_myapp(self):
        dlg = MyAppDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            data = load_data()
            data.setdefault("my_apps", []).append(dlg.result)
            save_data(data)
            self._refresh_myapps()

    def _edit_myapp(self):
        if self._sel_myapp_idx is None:
            messagebox.showinfo("No selection",
                "Click an app card to select it, then click Edit.", parent=self)
            return
        data = load_data()
        apps = data.get("my_apps", [])
        if self._sel_myapp_idx >= len(apps):
            return
        dlg = MyAppDialog(self, apps[self._sel_myapp_idx])
        self.wait_window(dlg)
        if dlg.result:
            apps[self._sel_myapp_idx] = dlg.result
            save_data(data)
            self._refresh_myapps()

    def _del_myapp(self):
        if self._sel_myapp_idx is None:
            messagebox.showinfo("No selection",
                "Click an app card to select it, then click Delete.", parent=self)
            return
        data = load_data()
        apps = data.get("my_apps", [])
        if self._sel_myapp_idx >= len(apps):
            return
        name = apps[self._sel_myapp_idx].get("name","this app")
        if messagebox.askyesno("Delete App",
                "Remove '{}' from your app directory?".format(name), parent=self):
            apps.pop(self._sel_myapp_idx)
            save_data(data)
            self._sel_myapp_idx = None
            self._refresh_myapps()

    # =========================================================================
    # TAB 4: CLI Reference
    # =========================================================================

    def _build_cli_tab(self):
        sf = ScrollFrame(self._tab_cli, bg=BG)
        sf.pack(fill="both", expand=True)
        inn = sf.inner

        hdr = tk.Frame(inn, bg=BG2, height=44)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="  jshortcuts -- CLI Command Reference",
                 bg=BG2, fg=FG, font=FB, anchor="w").pack(side="left", padx=16, pady=12)
        tk.Label(hdr, text="v{}".format(VERSION),
                 bg=BG2, fg=FG_DIM, font=FS, anchor="e").pack(side="right", padx=16)

        CMDS = [
            ("jshortcuts",              "List all shortcuts",
             "Displays all shortcuts grouped by category with colour coding."),
            ("jshortcuts add",          "Add a new shortcut",
             "Interactive prompts: category, keys, description, notes.\n"
             "Type a new category or pick from existing ones."),
            ("jshortcuts edit <id>",    "Edit a shortcut",
             "Shows current values in brackets. Press Enter to keep any field.\n"
             "Find the ID by running: jshortcuts"),
            ("jshortcuts del <id>",     "Delete a shortcut",
             "Asks for confirmation. Aliases: del  delete  rm"),
            ("jshortcuts cat <n>",      "Filter by category",
             "Case-insensitive. Multi-word: jshortcuts cat \"VS Code\""),
            ("jshortcuts search <q>",   "Search shortcuts",
             "Searches keys, description, notes, and category."),
            ("jshortcuts open",         "Open data file (choose editor)",
             "Shows a numbered list of available editors.\n"
             "Falls back to VS Code if available, then other editors.\n"
             "Launches detached -- does not block your terminal."),
            ("jshortcuts github push",  "Push to GitHub",
             "Prompts for repo URL and commit message, then git push.\n"
             "Saves URL in ~/.jshortcuts_github.json for next time."),
            ("jshortcuts github pull",  "Pull from GitHub (fetch+merge)",
             "Fetches latest and merges into local data file.\n"
             "Reloads all GUI tabs after pulling.\n"
             "Run pull before push to avoid conflicts."),
            ("jshortcuts gui",          "Open the GUI",
             "Launches this graphical interface.\n"
             "Also available from the Ubuntu app menu."),
            ("jshortcuts help",         "Show help in terminal",
             "Aliases: help  --help  -h"),
        ]

        for i, (cmd, summary, detail) in enumerate(CMDS):
            row = tk.Frame(inn, bg=BG2 if i % 2 == 0 else BG)
            row.pack(fill="x", padx=16, pady=(10,0))
            chip = tk.Frame(row, bg=BG3)
            chip.pack(side="left", anchor="nw", padx=(0,14), pady=4)
            tk.Label(chip, text="  {}  ".format(cmd),
                     bg=BG3, fg=ACCENT, font=FB, anchor="w"
                     ).pack(padx=2, pady=4)
            tcol = tk.Frame(row, bg=row["bg"])
            tcol.pack(side="left", fill="both", expand=True, anchor="nw")
            tk.Label(tcol, text=summary, bg=row["bg"], fg=FG, font=FB, anchor="w").pack(fill="x")
            tk.Label(tcol, text=detail, bg=row["bg"], fg=FG_DIM, font=FS,
                     anchor="w", justify="left", wraplength=580).pack(fill="x", pady=(2,0))
            sf.bind_scroll_recursive(row)

        tk.Frame(inn, bg=BG3, height=1).pack(fill="x", padx=16, pady=16)
        nf = tk.Frame(inn, bg=BG)
        nf.pack(fill="x", padx=16, pady=(0,8))
        tk.Label(nf, text="Data file:", bg=BG, fg=FG_DIM, font=FB).pack(side="left")
        tk.Label(nf, text="  "+DATA_FILE, bg=BG, fg=ACCENT, font=FS).pack(side="left")

        tk.Frame(inn, bg=BG3, height=1).pack(fill="x", padx=16, pady=(0,8))
        rf = tk.Frame(inn, bg=BG)
        rf.pack(fill="x", padx=16, pady=(0,20))
        tk.Label(rf, text="GitHub:", bg=BG, fg=FG_DIM, font=FB).pack(side="left")
        lnk = tk.Label(rf, text="  "+GITHUB, bg=BG, fg=ACCENT, font=FS, cursor="hand2")
        lnk.pack(side="left")
        lnk.bind("<Button-1>", lambda _: self._open_url(GITHUB))
        tk.Label(rf, text="    |    "+COMPANY, bg=BG, fg=FG_DIM, font=FS).pack(side="left")
        sf.bind_scroll_recursive(inn)

    # =========================================================================
    # Helpers: open file, GitHub, URL
    # =========================================================================

    def _open_file(self):
        dlg = OpenFileDialog(self)
        self.wait_window(dlg)

    def _open_github(self):
        dlg = GitHubDialog(self, on_pull_success=self._refresh_all)
        self.wait_window(dlg)

    def _open_url(self, url):
        if shutil.which("xdg-open"):
            subprocess.Popen(["xdg-open", url],
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             start_new_session=True)

    def _mini_input(self, title, prompt_text):
        dlg = tk.Toplevel(self)
        dlg.title(title)
        dlg.configure(bg=BG)
        dlg.resizable(False, False)
        dlg.grab_set(); dlg.focus_set()
        W, H = 400, 160
        dlg.geometry("{}x{}".format(W, H))
        dlg.update_idletasks()
        px = self.winfo_x() + (self.winfo_width()  - W) // 2
        py = self.winfo_y() + (self.winfo_height() - H) // 2
        dlg.geometry("{}x{}+{}+{}".format(W, H, max(0,px), max(0,py)))
        tk.Label(dlg, text=prompt_text, bg=BG, fg=FG, font=FN, anchor="w"
                 ).pack(fill="x", padx=20, pady=(16,6))
        var = tk.StringVar()
        tk.Entry(dlg, textvariable=var, bg=BG3, fg=FG, font=FN, relief="flat",
                 insertbackground=ACCENT, highlightthickness=1,
                 highlightbackground=BG3, highlightcolor=ACCENT
                 ).pack(fill="x", padx=20, ipady=7)
        result = [None]
        def ok(_e=None):
            v = var.get().strip()
            if v: result[0] = v
            dlg.destroy()
        br = tk.Frame(dlg, bg=BG)
        br.pack(fill="x", padx=20, pady=12)
        tk.Button(br, text=" Cancel ", command=dlg.destroy,
                  bg=BG3, fg=FG_DIM, font=FN, relief="flat",
                  padx=10, pady=5, cursor="hand2").pack(side="right", padx=(6,0))
        tk.Button(br, text=" OK ", command=ok,
                  bg=ACCENT, fg="white", font=FB, relief="flat",
                  padx=12, pady=5, cursor="hand2").pack(side="right")
        dlg.bind("<Return>", ok)
        dlg.bind("<Escape>", lambda _: dlg.destroy())
        self.wait_window(dlg)
        return result[0]

    # =========================================================================
    # Global refresh (called after GitHub pull)
    # =========================================================================

    def _refresh_all(self):
        self._refresh_shortcuts()
        self._refresh_apps()
        self._refresh_myapps()


# =============================================================================
# Entry point
# =============================================================================

if __name__ == "__main__":
    app = JShortcutsApp()
    app.mainloop()
