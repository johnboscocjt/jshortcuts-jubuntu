#!/usr/bin/env python3
"""
jshortcuts-gui — Dark popup GUI for managing personal keyboard shortcuts.
Reads/writes the same ~/.jshortcuts.json as the CLI tool.

Launch:
  python3 jshortcuts-gui.py
  jshortcuts gui          (via CLI companion)
"""

import json
import os
import sys
import shutil
import tkinter as tk
from tkinter import ttk, messagebox

# ── Colour palette ────────────────────────────────────────────────────────────
BG       = "#0f1117"
BG2      = "#161b27"
BG3      = "#1e2436"
ACCENT   = "#5b8af5"
ACCENT2  = "#3d6ae0"
FG       = "#e2e8f0"
FG_DIM   = "#6b7a99"
SUCCESS  = "#48bb78"
DANGER   = "#fc5c65"
WARNING  = "#f6ad55"

CAT_COLORS = ["#5b8af5", "#f6ad55", "#48bb78", "#fc5c65", "#b794f4", "#4fd1c5"]

FONT_TITLE = ("JetBrains Mono", 14, "bold")
FONT_BOLD  = ("JetBrains Mono", 10, "bold")
FONT_BODY  = ("JetBrains Mono", 10)
FONT_SMALL = ("JetBrains Mono", 9)

DATA_FILE    = os.path.expanduser("~/.jshortcuts.json")
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
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Add / Edit dialog ─────────────────────────────────────────────────────────

class ShortcutDialog(tk.Toplevel):
    """Modal dialog for creating or editing a shortcut."""

    def __init__(self, parent, title, categories, shortcut=None):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        self.geometry("500x380")
        self.update_idletasks()
        px = parent.winfo_x() + (parent.winfo_width()  - 500) // 2
        py = parent.winfo_y() + (parent.winfo_height() - 380) // 2
        self.geometry(f"+{px}+{py}")

        self._build(categories, shortcut or {})

    def _entry(self, parent, label, row, value=""):
        tk.Label(parent, text=label, bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL, anchor="w").grid(
            row=row, column=0, sticky="w", pady=(10, 2))
        var = tk.StringVar(value=value)
        e = tk.Entry(parent, textvariable=var, bg=BG3, fg=FG,
                     font=FONT_BODY, relief="flat",
                     insertbackground=ACCENT,
                     highlightthickness=1,
                     highlightbackground=BG3,
                     highlightcolor=ACCENT)
        e.grid(row=row + 1, column=0, sticky="ew", ipady=6)
        return var

    def _build(self, categories, s):
        # Header bar
        hdr = tk.Frame(self, bg=ACCENT2, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"  ⌨  {self.title()}", bg=ACCENT2, fg="white",
                 font=FONT_BOLD, anchor="w").pack(side="left", padx=12, pady=10)

        # Form
        form = tk.Frame(self, bg=BG2, padx=24, pady=16)
        form.pack(fill="both", expand=True, padx=16, pady=12)
        form.columnconfigure(0, weight=1)

        # Category combobox
        tk.Label(form, text="Category", bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL, anchor="w").grid(
            row=0, column=0, sticky="w", pady=(0, 2))
        self.cat_var = tk.StringVar(value=s.get("category", ""))
        combo = ttk.Combobox(form, textvariable=self.cat_var,
                             values=categories, font=FONT_BODY)
        combo.grid(row=1, column=0, sticky="ew", ipady=4)
        self._style_combo()

        self.keys_var  = self._entry(form, "Keys (e.g. Ctrl + T)",  2, s.get("keys", ""))
        self.desc_var  = self._entry(form, "Description",           4, s.get("description", ""))
        self.notes_var = self._entry(form, "Notes (optional)",      6, s.get("notes", ""))

        # Buttons
        btn_row = tk.Frame(self, bg=BG, pady=8)
        btn_row.pack(fill="x", padx=20, pady=(0, 16))

        tk.Button(btn_row, text="Cancel", command=self.destroy,
                  bg=BG3, fg=FG_DIM, font=FONT_BODY,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  activebackground=BG2, activeforeground=FG).pack(
            side="right", padx=(8, 0))

        tk.Button(btn_row, text="  Save  ", command=self._save,
                  bg=ACCENT, fg="white", font=FONT_BOLD,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  activebackground=ACCENT2, activeforeground="white").pack(
            side="right")

        self.bind("<Return>", lambda _: self._save())
        self.bind("<Escape>", lambda _: self.destroy())

    def _style_combo(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox",
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


# ── Main application window ───────────────────────────────────────────────────

class JShortcutsApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("jshortcuts")
        self.configure(bg=BG)
        self.geometry("820x580")
        self.minsize(600, 400)

        self._cat_color_map  = {}
        self._selected_id    = None
        self._rows           = {}
        self._search_var     = tk.StringVar()
        self._selected_cat   = tk.StringVar(value="All")
        self._search_var.trace_add("write", lambda *_: self._refresh())

        self._build_ui()
        self._refresh()

        # Centre on screen
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"820x580+{(sw - 820)//2}+{(sh - 580)//2}")

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self, bg=BG2, height=56)
        topbar.pack(fill="x")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="⌨", bg=BG2, fg=ACCENT,
                 font=("JetBrains Mono", 20)).pack(side="left", padx=(16, 6), pady=10)
        tk.Label(topbar, text="jshortcuts", bg=BG2, fg=FG,
                 font=FONT_TITLE).pack(side="left", pady=10)
        tk.Label(topbar, text="my keyboard shortcuts", bg=BG2, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(8, 0), pady=14)

        # Search box
        sf = tk.Frame(topbar, bg=BG3, padx=8, pady=4)
        sf.pack(side="right", padx=16, pady=10)
        tk.Label(sf, text="⌕", bg=BG3, fg=FG_DIM,
                 font=("JetBrains Mono", 12)).pack(side="left")
        tk.Entry(sf, textvariable=self._search_var,
                 bg=BG3, fg=FG, font=FONT_BODY,
                 relief="flat", width=20,
                 insertbackground=ACCENT).pack(side="left", padx=4)

        # Main area: sidebar + list
        main_area = tk.Frame(self, bg=BG)
        main_area.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main_area, bg=BG2, width=160)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CATEGORIES", bg=BG2, fg=FG_DIM,
                 font=("JetBrains Mono", 8), anchor="w").pack(
            fill="x", padx=12, pady=(16, 8))

        self._cat_frame = tk.Frame(sidebar, bg=BG2)
        self._cat_frame.pack(fill="x")

        # Right pane
        right = tk.Frame(main_area, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Toolbar
        toolbar = tk.Frame(right, bg=BG, pady=8, padx=16)
        toolbar.pack(fill="x")

        self._count_label = tk.Label(toolbar, text="", bg=BG,
                                     fg=FG_DIM, font=FONT_SMALL)
        self._count_label.pack(side="left")

        for text, cmd, color in [
            ("+ Add",    self._add,    SUCCESS),
            ("✎ Edit",   self._edit,   ACCENT),
            ("✕ Delete", self._delete, DANGER),
        ]:
            tk.Button(toolbar, text=text, command=cmd,
                      bg=color, fg="white", font=FONT_SMALL,
                      relief="flat", padx=10, pady=4, cursor="hand2",
                      activebackground=BG3, activeforeground=FG).pack(
                side="right", padx=4)

        # Scrollable canvas
        canvas_frame = tk.Frame(right, bg=BG)
        canvas_frame.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(canvas_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical",
                                 command=self._canvas.yview, bg=BG2)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
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

        # Status bar
        status = tk.Frame(self, bg=BG2, height=28)
        status.pack(fill="x", side="bottom")
        status.pack_propagate(False)
        tk.Label(status, text=f"  data: {DATA_FILE}", bg=BG2, fg=FG_DIM,
                 font=("JetBrains Mono", 8), anchor="w").pack(
            side="left", pady=6)

    # ── Sidebar ───────────────────────────────────────────────────────────────

    def _build_sidebar(self, categories):
        for w in self._cat_frame.winfo_children():
            w.destroy()

        for cat in ["All"] + categories:
            selected = (self._selected_cat.get() == cat)
            color = self._cat_color_map.get(cat, ACCENT) if cat != "All" else ACCENT
            bg    = BG3  if selected else BG2
            fg    = color if selected else FG_DIM

            tk.Button(self._cat_frame, text=cat,
                      command=lambda c=cat: self._select_cat(c),
                      bg=bg, fg=fg, font=FONT_SMALL,
                      relief="flat", anchor="w", padx=12, pady=5,
                      cursor="hand2",
                      activebackground=BG3,
                      activeforeground=FG).pack(fill="x")

    def _select_cat(self, cat):
        self._selected_cat.set(cat)
        self._refresh()

    # ── Refresh ───────────────────────────────────────────────────────────────

    def _refresh(self):
        data      = load_data()
        shortcuts = data["shortcuts"]

        # Rebuild category colour map
        cats = []
        for s in shortcuts:
            if s["category"] not in cats:
                cats.append(s["category"])
        for i, cat in enumerate(cats):
            self._cat_color_map[cat] = CAT_COLORS[i % len(CAT_COLORS)]

        self._build_sidebar(cats)

        # Apply filters
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

            # Category header
            hdr = tk.Frame(self._list_frame, bg=BG)
            hdr.pack(fill="x", padx=16, pady=(16, 6))
            tk.Frame(hdr, bg=color, width=4, height=18).pack(side="left")
            tk.Label(hdr, text=f"  {cat.upper()}", bg=BG, fg=color,
                     font=("JetBrains Mono", 9, "bold")).pack(side="left")

            for s in items:
                self._make_row(s, color)

    def _make_row(self, s, cat_color):
        sid = s["id"]
        row = tk.Frame(self._list_frame, bg=BG2, cursor="hand2")
        row.pack(fill="x", padx=16, pady=2)

        tk.Frame(row, bg=BG3, width=4).pack(side="left", fill="y")
        tk.Label(row, text=f" {sid} ", bg=BG3, fg=FG_DIM,
                 font=FONT_SMALL).pack(side="left", padx=(6, 0), pady=8)

        keys_lbl = tk.Label(row, text=f"  {s['keys']}  ", bg=BG3,
                            fg=cat_color, font=FONT_BOLD, padx=4)
        keys_lbl.pack(side="left", padx=8, pady=8)

        text_frame = tk.Frame(row, bg=BG2)
        text_frame.pack(side="left", fill="both", expand=True, pady=8)
        tk.Label(text_frame, text=s["description"], bg=BG2, fg=FG,
                 font=FONT_BODY, anchor="w").pack(fill="x")
        if s.get("notes"):
            tk.Label(text_frame, text=s["notes"], bg=BG2, fg=FG_DIM,
                     font=FONT_SMALL, anchor="w").pack(fill="x")

        for widget in (row, keys_lbl, text_frame):
            widget.bind("<Button-1>", lambda _, i=sid: self._select_row(i))
            widget.bind("<Double-1>", lambda _, i=sid: self._edit_id(i))
            widget.bind("<Enter>",    lambda _, r=row: r.config(bg=BG3))
            widget.bind("<Leave>",    lambda _, r=row, i=sid: r.config(
                bg=BG3 if self._selected_id == i else BG2))

        self._rows[sid] = row

    def _select_row(self, sid):
        if self._selected_id and self._selected_id in self._rows:
            self._rows[self._selected_id].config(bg=BG2)
        self._selected_id = sid
        if sid in self._rows:
            self._rows[sid].config(bg=BG3)

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
            messagebox.showinfo("Select a shortcut",
                "Click a row first, then click ✎ Edit.", parent=self)
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
            messagebox.showinfo("Select a shortcut",
                "Click a row first, then click ✕ Delete.", parent=self)
            return
        sid   = self._selected_id
        data  = load_data()
        match = next((s for s in data["shortcuts"] if s["id"] == sid), None)
        if not match:
            return
        if messagebox.askyesno(
                "Delete Shortcut",
                f"Delete shortcut #{sid}?\n\n{match['keys']} — {match['description']}",
                parent=self):
            data["shortcuts"] = [s for s in data["shortcuts"] if s["id"] != sid]
            save_data(data)
            self._selected_id = None
            self._refresh()


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = JShortcutsApp()
    app.mainloop()
