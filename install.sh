#!/usr/bin/env bash
# =============================================================================
# install.sh — Install jshortcuts and make it globally accessible
# =============================================================================
# What this script does automatically (no manual steps needed):
#   1. Checks for Python 3 and tkinter
#   2. Copies scripts to ~/bin/
#   3. Makes scripts executable
#   4. Creates your ~/.jshortcuts.json with example shortcuts (if not present)
#   5. Adds ~/bin to PATH in your shell config (~/.bashrc and/or ~/.zshrc)
#   6. Creates a .desktop app launcher (shows in Ubuntu app menu)
# =============================================================================
set -euo pipefail

INSTALL_DIR="$HOME/bin"
DATA_FILE="$HOME/.jshortcuts.json"
DESKTOP_FILE="$HOME/.local/share/applications/jshortcuts.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PATH_LINE='export PATH="$HOME/bin:$PATH"'
PATH_COMMENT='# jshortcuts — added by install.sh'

# ── Colours ───────────────────────────────────────────────────────────────────
RESET='\033[0m'; BOLD='\033[1m'; DIM='\033[2m'
GREEN='\033[32m'; CYAN='\033[36m'; YELLOW='\033[33m'; RED='\033[31m'

info()    { echo -e "  ${CYAN}→${RESET} $*"; }
success() { echo -e "  ${GREEN}✓${RESET} $*"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET} $*"; }
error()   { echo -e "  ${RED}✗${RESET} $*"; exit 1; }
skip()    { echo -e "  ${DIM}–${RESET} $* ${DIM}(already done)${RESET}"; }

echo ""
echo -e "  ${BOLD}${CYAN}⌨  jshortcuts — installer${RESET}"
echo -e "  ${DIM}──────────────────────────────────────${RESET}"
echo ""

# ── Step 1: Python 3 ──────────────────────────────────────────────────────────
echo -e "  ${BOLD}[1/6] Checking Python 3${RESET}"
if ! command -v python3 &>/dev/null; then
    error "python3 not found. Install it with:  sudo apt install python3"
fi
PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
success "Python $PYVER found"
echo ""

# ── Step 2: tkinter ───────────────────────────────────────────────────────────
echo -e "  ${BOLD}[2/6] Checking tkinter (for GUI)${RESET}"
if python3 -c "import tkinter" &>/dev/null; then
    success "tkinter available — GUI will work"
else
    warn "tkinter not found — the GUI will not open."
    warn "Fix with:  sudo apt install python3-tk"
    warn "The CLI tool will still work without it."
fi
echo ""

# ── Step 3: Copy scripts ──────────────────────────────────────────────────────
echo -e "  ${BOLD}[3/6] Installing scripts to ~/bin/${RESET}"
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR/jshortcuts"              "$INSTALL_DIR/jshortcuts"
cp "$SCRIPT_DIR/jshortcuts-gui.py"       "$INSTALL_DIR/jshortcuts-gui.py"
cp "$SCRIPT_DIR/jshortcuts_default.json" "$INSTALL_DIR/jshortcuts_default.json"
chmod +x "$INSTALL_DIR/jshortcuts"
chmod +x "$INSTALL_DIR/jshortcuts-gui.py"
success "jshortcuts         → $INSTALL_DIR/jshortcuts"
success "jshortcuts-gui.py  → $INSTALL_DIR/jshortcuts-gui.py"
echo ""

# ── Step 4: Create default data ───────────────────────────────────────────────
echo -e "  ${BOLD}[4/6] Setting up shortcut data${RESET}"
if [ ! -f "$DATA_FILE" ]; then
    cp "$SCRIPT_DIR/jshortcuts_default.json" "$DATA_FILE"
    success "Created $DATA_FILE with 12 example shortcuts"
else
    skip "$DATA_FILE already exists — your shortcuts are kept"
fi
echo ""

# ── Step 5: Auto-add ~/bin to PATH ────────────────────────────────────────────
echo -e "  ${BOLD}[5/6] Adding ~/bin to PATH (globally)${RESET}"

# Check if already in current PATH
if echo "$PATH" | grep -q "$HOME/bin"; then
    skip "~/bin is already in your active PATH"
    PATH_ADDED=false
else
    PATH_ADDED=true
fi

# Detect which shell config files exist and patch them
RC_FILES=()
[ -f "$HOME/.bashrc"  ] && RC_FILES+=("$HOME/.bashrc")
[ -f "$HOME/.zshrc"   ] && RC_FILES+=("$HOME/.zshrc")
[ -f "$HOME/.profile" ] && RC_FILES+=("$HOME/.profile")

# If no RC files found, create .bashrc
if [ ${#RC_FILES[@]} -eq 0 ]; then
    RC_FILES=("$HOME/.bashrc")
    touch "$HOME/.bashrc"
fi

PATCHED_ANY=false
for RC in "${RC_FILES[@]}"; do
    if grep -q "jshortcuts" "$RC" 2>/dev/null; then
        skip "PATH entry already in $RC"
    else
        echo "" >> "$RC"
        echo "$PATH_COMMENT" >> "$RC"
        echo "$PATH_LINE"    >> "$RC"
        success "Added PATH entry to $RC"
        PATCHED_ANY=true
    fi
done

# Also export into the current shell session so it works immediately
export PATH="$HOME/bin:$PATH"
success "~/bin is now active in this terminal session"
echo ""

# ── Step 6: Desktop app launcher ─────────────────────────────────────────────
echo -e "  ${BOLD}[6/6] Creating desktop app launcher${RESET}"
mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=jshortcuts
Comment=Personal keyboard shortcuts manager
Exec=python3 ${INSTALL_DIR}/jshortcuts-gui.py
Icon=input-keyboard
Type=Application
Categories=Utility;
Terminal=false
StartupNotify=false
EOF
success "Launcher created — search 'jshortcuts' in your app menu"
echo ""

# ── Summary ───────────────────────────────────────────────────────────────────
echo -e "  ${DIM}──────────────────────────────────────${RESET}"
echo -e "  ${BOLD}${GREEN}✓  Installation complete!${RESET}"
echo ""
echo -e "  ${BOLD}You can now use jshortcuts right away in this terminal:${RESET}"
echo ""
echo -e "    ${CYAN}jshortcuts${RESET}           — list all your shortcuts"
echo -e "    ${CYAN}jshortcuts add${RESET}        — add a new shortcut"
echo -e "    ${CYAN}jshortcuts edit 1${RESET}     — edit shortcut #1"
echo -e "    ${CYAN}jshortcuts del 1${RESET}      — delete shortcut #1"
echo -e "    ${CYAN}jshortcuts gui${RESET}        — open the GUI popup"
echo -e "    ${CYAN}jshortcuts help${RESET}       — show all commands"
echo ""

if [ "$PATCHED_ANY" = true ]; then
    echo -e "  ${YELLOW}Note:${RESET} New terminal windows will pick up the PATH automatically."
    echo -e "  In ${BOLD}this${RESET} terminal it's already active — no need to source anything."
    echo ""
fi#!/usr/bin/env bash
# =============================================================================
# install.sh — Install jshortcuts to ~/bin
# =============================================================================
set -euo pipefail

INSTALL_DIR="$HOME/bin"
DATA_FILE="$HOME/.jshortcuts.json"
DESKTOP_FILE="$HOME/.local/share/applications/jshortcuts.desktop"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Colours ───────────────────────────────────────────────────────────────────
RESET='\033[0m'; BOLD='\033[1m'
GREEN='\033[32m'; CYAN='\033[36m'; YELLOW='\033[33m'; RED='\033[31m'

info()    { echo -e "  ${CYAN}→${RESET} $*"; }
success() { echo -e "  ${GREEN}✓${RESET} $*"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET} $*"; }
error()   { echo -e "  ${RED}✗${RESET} $*"; }

echo ""
echo -e "  ${BOLD}${CYAN}⌨  Installing jshortcuts${RESET}"
echo ""

# ── Check Python ──────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    error "python3 is not installed. Install it with: sudo apt install python3"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
info "Python $PYTHON_VERSION found"

# ── Check tkinter ─────────────────────────────────────────────────────────────
if ! python3 -c "import tkinter" &>/dev/null; then
    warn "tkinter not found. The GUI will not work."
    warn "Install it with: sudo apt install python3-tk"
else
    info "tkinter available"
fi

# ── Create ~/bin if needed ────────────────────────────────────────────────────
mkdir -p "$INSTALL_DIR"
info "Install directory: $INSTALL_DIR"

# ── Copy files ────────────────────────────────────────────────────────────────
cp "$SCRIPT_DIR/jshortcuts"              "$INSTALL_DIR/jshortcuts"
cp "$SCRIPT_DIR/jshortcuts-gui.py"       "$INSTALL_DIR/jshortcuts-gui.py"
cp "$SCRIPT_DIR/jshortcuts_default.json" "$INSTALL_DIR/jshortcuts_default.json"

chmod +x "$INSTALL_DIR/jshortcuts"
chmod +x "$INSTALL_DIR/jshortcuts-gui.py"
success "Scripts installed to $INSTALL_DIR/"

# ── Create default data if missing ───────────────────────────────────────────
if [ ! -f "$DATA_FILE" ]; then
    cp "$SCRIPT_DIR/jshortcuts_default.json" "$DATA_FILE"
    success "Created default config: $DATA_FILE"
else
    info "Existing config kept: $DATA_FILE"
fi

# ── PATH check ───────────────────────────────────────────────────────────────
echo ""
if echo "$PATH" | grep -q "$HOME/bin"; then
    success "$HOME/bin is already in your PATH"
else
    warn "$HOME/bin is not yet in your PATH"
    echo ""
    echo "    Add the following line to your ~/.bashrc or ~/.zshrc:"
    echo ""
    echo -e "    ${CYAN}export PATH=\"\$HOME/bin:\$PATH\"${RESET}"
    echo ""
    echo "    Then run:  source ~/.bashrc"
fi

# ── Desktop launcher ─────────────────────────────────────────────────────────
mkdir -p "$HOME/.local/share/applications"
cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=jshortcuts
Comment=Personal keyboard shortcuts manager
Exec=python3 ${INSTALL_DIR}/jshortcuts-gui.py
Icon=input-keyboard
Type=Application
Categories=Utility;
Terminal=false
EOF

success "Desktop launcher created (search 'jshortcuts' in your app menu)"

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}${GREEN}Done!${RESET} 🎉"
echo ""
echo "  Quick start:"
echo -e "    ${CYAN}jshortcuts${RESET}           list all shortcuts"
echo -e "    ${CYAN}jshortcuts add${RESET}        add a new shortcut"
echo -e "    ${CYAN}jshortcuts gui${RESET}        open the GUI window"
echo ""
