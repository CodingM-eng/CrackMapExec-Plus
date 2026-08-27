#!/usr/bin/env bash
# ==============================================================================
# CrackMapExec+ (CME+) Automated Installer
# Next-Generation Security Lab, CTF, and Educational Testing Framework
# ==============================================================================
set -euo pipefail

BOLD="\033[1m"
CYAN="\033[0;36m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

print_banner() {
    echo -e "${CYAN}╭──────────────────────────────────────────────╮${NC}"
    echo -e "${CYAN}│          CrackMapExec+ Installer             │${NC}"
    echo -e "${CYAN}╰──────────────────────────────────────────────╯${NC}"
    echo ""
}

info() {
    echo -e "  ${GREEN}✓${NC} $1"
}

warn() {
    echo -e "  ${YELLOW}!${NC} $1"
}

fail() {
    echo -e "  ${RED}✗${NC} $1"
    exit 1
}

# 1. Check Python 3
check_python() {
    if command -v python3 &>/dev/null; then
        PY_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
        if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 10 ]; then
            info "Python detected ($PY_VER)"
        else
            fail "Python 3.10+ is required. Found Python $PY_VER."
        fi
    else
        fail "Python 3 is not installed or not in PATH."
    fi
}

# 2. Detect Linux Distro & Package Manager
detect_distro() {
    DISTRO="Unknown Linux"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO="${NAME:-Linux}"
    elif [ "$(uname)" = "Darwin" ]; then
        DISTRO="macOS"
    fi
    info "Operating System: $DISTRO"
}

# 3. Detect / Install pipx
ensure_pipx() {
    if command -v pipx &>/dev/null; then
        info "pipx detected ($(pipx --version 2>/dev/null || echo 'installed'))"
    else
        echo -e "  ${YELLOW}*${NC} pipx not found, attempting automatic installation..."
        if command -v apt-get &>/dev/null; then
            if [ "$EUID" -ne 0 ]; then
                sudo apt-get update -qq && sudo apt-get install -y -qq pipx
            else
                apt-get update -qq && apt-get install -y -qq pipx
            fi
        elif command -v dnf &>/dev/null; then
            if [ "$EUID" -ne 0 ]; then
                sudo dnf install -y -q pipx
            else
                dnf install -y -q pipx
            fi
        elif command -v pacman &>/dev/null; then
            if [ "$EUID" -ne 0 ]; then
                sudo pacman -S --noconfirm --needed python-pipx
            else
                pacman -S --noconfirm --needed python-pipx
            fi
        elif command -v brew &>/dev/null; then
            brew install pipx
        else
            python3 -m pip install --user pipx
        fi

        if command -v pipx &>/dev/null; then
            info "pipx successfully installed"
        else
            fail "Failed to automatically install pipx. Please install pipx manually (e.g. 'sudo apt install pipx')."
        fi
    fi

    # Ensure pipx PATH is configured
    pipx ensurepath >/dev/null 2>&1 || true
}

# 4. Install CrackMapExec+ via pipx
install_cmeplus() {
    info "Installing CrackMapExec+ into isolated environment"
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    # Check if --dev / -e flag passed
    DEV_MODE=false
    for arg in "$@"; do
        if [ "$arg" = "--dev" ] || [ "$arg" = "-e" ] || [ "$arg" = "--editable" ]; then
            DEV_MODE=true
            break
        fi
    done

    if [ "$DEV_MODE" = true ]; then
        pipx install --editable --force "$SCRIPT_DIR" >/dev/null
        info "Installed in development (editable) mode"
    else
        pipx install --force "$SCRIPT_DIR" >/dev/null
        info "Installed in standalone application mode"
    fi
}

# 5. Verify Installation
verify_commands() {
    # Check ~/.local/bin in PATH
    LOCAL_BIN="$HOME/.local/bin"
    if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
        export PATH="$LOCAL_BIN:$PATH"
    fi

    info "Registering CLI commands"

    VER_CMEP=$(crackmapexec+ --version 2>/dev/null || true)
    VER_CME=$(cme+ --version 2>/dev/null || true)

    if [ -n "$VER_CMEP" ] && [ -n "$VER_CME" ]; then
        info "Installation verified ($VER_CMEP)"
    else
        warn "CLI entry points installed to $LOCAL_BIN, but may need shell restart."
    fi
}

# Main Execution Flow
main() {
    print_banner
    check_python
    detect_distro
    ensure_pipx
    install_cmeplus "$@"
    verify_commands

    echo ""
    echo -e "${BOLD}Commands:${NC}"
    echo ""
    echo "  crackmapexec+ --help"
    echo "  cme+ --help"
    echo "  crackmapexec+ doctor"
    echo ""
    echo -e "${GREEN}${BOLD}Installation complete.${NC}"

    # PATH check advisory if needed
    if ! command -v crackmapexec+ &>/dev/null; then
        echo ""
        echo -e "${YELLOW}Notice:${NC} If commands are not found in your current shell, run:"
        echo -e "  ${CYAN}source ~/.bashrc${NC}  (or ${CYAN}source ~/.zshrc${NC})"
    fi
}

main "$@"
