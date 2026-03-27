#!/usr/bin/env bash
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
