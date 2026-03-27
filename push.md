# 1. Clone your empty repo
git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git
cd jshortcuts-jubuntu

# 2. Copy all the downloaded files into this folder
#    (the full structure shown below)

# 3. Stage everything
git add .

# 4. Commit
git commit -m "feat: initial release v1.0.0 — CLI + GUI shortcut manager"

# 5. Push
git push origin main
```

---

## Complete repository structure
```
jshortcuts-jubuntu/
├── README.md                  ← Full docs, table of contents, examples
├── LICENSE                    ← MIT (your existing one)
├── CHANGELOG.md               ← Version history + roadmap
├── CONTRIBUTING.md            ← How others can contribute
├── .gitignore                 ← Python, OS, editor ignores
│
├── jshortcuts                 ← CLI script (make executable)
├── jshortcuts-gui.py          ← GUI popup app
├── jshortcuts_default.json    ← 12 starter shortcuts
│
├── install.sh                 ← Installs to ~/bin + creates app launcher
├── uninstall.sh               ← Removes files, optionally deletes data
│
└── docs/
    ├── CLI_USAGE.md           ← Full CLI reference with terminal examples
    └── GUI_USAGE.md           ← Full GUI reference with layout diagrams
