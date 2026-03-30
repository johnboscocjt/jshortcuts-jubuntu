#!/usr/bin/env bash
# =============================================================================
# uninstall.sh -- Remove jshortcuts from ~/bin
# Your data file (~/.jshortcuts.json) is kept unless you choose to delete it.
# =============================================================================
set -euo pipefail

INSTALL_DIR="${HOME}/bin"
DATA_FILE="${HOME}/.jshortcuts.json"
GITHUB_CFG="${HOME}/.jshortcuts_github.json"
DESKTOP_FILE="${HOME}/.local/share/applications/jshortcuts.desktop"

RESET='\033[0m'
BOLD='\033[1m'
GREEN='\033[32m'
CYAN='\033[36m'
YELLOW='\033[33m'
RED='\033[31m'
DIM='\033[2m'

ok()   { echo -e "  ${GREEN}[ok]${RESET}  $*"; }
warn() { echo -e "  ${YELLOW}[!!]${RESET}  $*"; }
info() { echo -e "  ${CYAN}[..]${RESET}  $*"; }
skip() { echo -e "  ${DIM}[--]  $* (not found, skipping)${RESET}"; }

echo ""
echo -e "  ${BOLD}${RED}jshortcuts -- uninstaller${RESET}"
echo -e "  ${DIM}----------------------------------------------${RESET}"
echo ""

# -- Remove installed scripts --------------------------------------------------
echo -e "  ${BOLD}Removing scripts from ~/bin/${RESET}"
for fname in jshortcuts jshortcuts-gui.py jshortcuts_default.json; do
    fpath="${INSTALL_DIR}/${fname}"
    if [ -f "${fpath}" ]; then
        rm "${fpath}"
        ok "Removed ${fpath}"
    else
        skip "${fpath}"
    fi
done

# -- Remove desktop launcher ---------------------------------------------------
echo ""
echo -e "  ${BOLD}Removing desktop launcher${RESET}"
if [ -f "${DESKTOP_FILE}" ]; then
    rm "${DESKTOP_FILE}"
    ok "Removed ${DESKTOP_FILE}"
else
    skip "${DESKTOP_FILE}"
fi

# -- GitHub config -------------------------------------------------------------
echo ""
echo -e "  ${BOLD}GitHub config${RESET}"
if [ -f "${GITHUB_CFG}" ]; then
    read -rp "  Remove GitHub config ${GITHUB_CFG}? (y/N): " gc
    if [ "${gc,,}" = "y" ]; then
        rm "${GITHUB_CFG}"
        ok "Removed ${GITHUB_CFG}"
    else
        info "Kept ${GITHUB_CFG}"
    fi
else
    skip "${GITHUB_CFG}"
fi

# -- Shortcut data file --------------------------------------------------------
echo ""
echo -e "  ${BOLD}Shortcut data file${RESET}"
if [ -f "${DATA_FILE}" ]; then
    echo -e "  ${YELLOW}Your shortcuts are in:${RESET} ${DATA_FILE}"
    read -rp "  Delete it too? (y/N): " dc
    if [ "${dc,,}" = "y" ]; then
        rm "${DATA_FILE}"
        ok "Deleted ${DATA_FILE}"
    else
        info "Kept ${DATA_FILE}  (you can keep or back it up)"
    fi
else
    skip "${DATA_FILE}"
fi

# -- PATH lines in shell configs -----------------------------------------------
echo ""
echo -e "  ${BOLD}PATH entries in shell configs${RESET}"
for RC in "${HOME}/.bashrc" "${HOME}/.zshrc" "${HOME}/.profile"; do
    if [ -f "${RC}" ] && grep -q "jshortcuts" "${RC}" 2>/dev/null; then
        info "Found jshortcuts PATH line in ${RC}"
        info "To remove it manually, open ${RC} and delete the two lines that mention jshortcuts"
    fi
done

# -- Done ----------------------------------------------------------------------
echo ""
echo -e "  ${DIM}----------------------------------------------${RESET}"
echo -e "  ${BOLD}${GREEN}jshortcuts has been uninstalled.${RESET}"
echo ""
echo -e "  To reinstall later:"
echo -e "  ${CYAN}git clone https://github.com/johnboscocjt/jshortcuts-jubuntu.git${RESET}"
echo -e "  ${CYAN}cd jshortcuts-jubuntu && bash install.sh${RESET}"
echo ""
