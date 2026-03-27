# Changelog

All notable changes to jshortcuts-jubuntu are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2026-03-27

### Added
- `jshortcuts` CLI tool with colour-coded output
- `jshortcuts-gui.py` dark popup GUI window (tkinter)
- Shared data file `~/.jshortcuts.json` used by both tools
- CLI commands: list, add, edit, del, cat, search, gui, help
- GUI features: category sidebar, search box, add/edit/delete dialogs
- `install.sh` automated installer with PATH check and `.desktop` launcher
- `uninstall.sh` with optional data-file removal
- Default example shortcuts across Navigation, Terminal, Browser, System
- `docs/CLI_USAGE.md` — full CLI reference
- `docs/GUI_USAGE.md` — full GUI reference

---

## Roadmap

- [ ] Import/export shortcuts as CSV
- [ ] Duplicate a shortcut
- [ ] Reorder shortcuts via drag-and-drop (GUI)
- [ ] `jshortcuts backup` command
- [ ] Optional system tray icon
