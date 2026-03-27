#!/usr/bin/env bash
# =============================================================================
# uninstall.sh — Remove jshortcuts from ~/bin
# Your data file (~/.jshortcuts.json) is kept by default.
# =============================================================================
set -euo pipefail

INSTALL_DIR="$HOME/bin"
DATA_FILE="$HOME/.jshortcuts.json"
DESKTOP_FILE="$HOME/.local/share/applications/jshortcuts.desktop"

# ── Colours ───────────────────────────────────────────────────────────────────
RESET='\033[0m'; BOLD='\033[1m'
GREEN='\033[32m'; CYAN='\033[36m'; YELLOW='\033[33m'; RED='\033[31m'

success() { echo -e "  ${GREEN}✓${RESET} $*"; }
warn()    { echo -e "  ${YELLOW}⚠${RESET} $*"; }
info()    { echo -e "  ${CYAN}→${RESET} $*"; }

echo ""
echo -e "  ${BOLD}${RED}⌨  Uninstalling jshortcuts${RESET}"
echo ""

# ── Remove scripts ────────────────────────────────────────────────────────────
FILES=(
    "$INSTALL_DIR/jshortcuts"
    "$INSTALL_DIR/jshortcuts-gui.py"
    "$INSTALL_DIR/jshortcuts_default.json"
)

for f in "${FILES[@]}"; do
    if [ -f "$f" ]; then
        rm "$f"
        success "Removed $f"
    else
        warn "Not found (skipping): $f"
    fi
done

# ── Remove desktop launcher ───────────────────────────────────────────────────
if [ -f "$DESKTOP_FILE" ]; then
    rm "$DESKTOP_FILE"
    success "Removed desktop launcher"
fi

# ── Data file ─────────────────────────────────────────────────────────────────
echo ""
if [ -f "$DATA_FILE" ]; then
    echo -e "  ${YELLOW}Your data file was kept:${RESET} $DATA_FILE"
    echo ""
    read -rp "  Delete your shortcuts data too? (y/N): " confirm
    if [[ "${confirm,,}" == "y" ]]; then
        rm "$DATA_FILE"
        success "Data file deleted."
    else
        info "Data file kept. You can delete it manually later:"
        echo "      rm $DATA_FILE"
    fi
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "  ${BOLD}${GREEN}jshortcuts uninstalled.${RESET}"
echo ""
