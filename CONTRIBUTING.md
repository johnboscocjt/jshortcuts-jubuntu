# Contributing to jshortcuts-jubuntu

Thank you for your interest in contributing!  
jshortcuts is a simple personal tool, and contributions of any size are welcome.

---

## Ways to contribute

- 🐛 **Report a bug** — open a [GitHub Issue](https://github.com/johnboscocjt/jshortcuts-jubuntu/issues)
- 💡 **Suggest a feature** — open an Issue with the `enhancement` label
- 🔧 **Fix a bug or build a feature** — open a Pull Request

---

## Development setup

```bash
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu

# No dependencies beyond Python 3.8+ and tkinter
python3 -c "import tkinter; print('GUI ready')"

# Test the CLI directly
python3 jshortcuts

# Test the GUI directly
python3 jshortcuts-gui.py
```

---

## Project structure

```
jshortcuts-jubuntu/
├── jshortcuts               # CLI tool (Python, executable)
├── jshortcuts-gui.py        # GUI app  (Python + tkinter)
├── jshortcuts_default.json  # Default shortcut examples
├── install.sh               # Automated installer
├── uninstall.sh             # Automated uninstaller
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── docs/
    ├── CLI_USAGE.md
    └── GUI_USAGE.md
```

---

## Pull Request guidelines

1. Fork the repo and create a branch: `git checkout -b feature/your-feature`
2. Keep commits small and focused
3. Use clear commit messages, e.g. `fix: handle missing notes field`
4. Test both the CLI and the GUI before submitting
5. Update `CHANGELOG.md` under an `[Unreleased]` section
6. Open the PR against the `main` branch

---

## Commit message style

```
type: short description

Types: feat | fix | docs | style | refactor | test | chore
```

Examples:
```
feat: add CSV export command
fix: crash when notes field is missing
docs: add GUI screenshot to README
```

---

## Code style

- Python 3.8+ compatible
- No external dependencies (stdlib + tkinter only)
- Keep the CLI and GUI sharing the same `~/.jshortcuts.json` format
- 4-space indentation, max line length ~100 chars
