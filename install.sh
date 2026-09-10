#!/usr/bin/env bash
# ==============================================================================
# CrackMapExec+ (CME+) Automated Production Installer
# Next-Generation Security Lab, CTF, and Educational Testing Framework
# ==============================================================================
set -euo pipefail

BOLD="\033[1m"
CYAN="\033[0;36m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"

print_banner() {
    echo -e "${CYAN}╭────────────────────────────────────────────────────────────╮${NC}"
    echo -e "${CYAN}│               CrackMapExec+ Installer                     │${NC}"
    echo -e "${CYAN}│      Zero-Error Clean Installation & Environment Setup     │${NC}"
    echo -e "${CYAN}╰────────────────────────────────────────────────────────────╯${NC}"
    echo ""
}

info() {
    echo -e "  ${GREEN}✓${NC} $1"
}

warn() {
    echo -e "  ${YELLOW}!${NC} $1"
}

fail() {
    echo -e "  ${RED}✗${NC} $1" >&2
    exit 1
}

# 1. Detect and Validate Python (>= 3.11 required)
PYTHON_BIN=""
check_python() {
    for candidate in python3 python python3.13 python3.12 python3.11; do
        if command -v "$candidate" &>/dev/null; then
            if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)' 2>/dev/null; then
                PYTHON_BIN="$(command -v "$candidate")"
                break
            fi
        fi
    done

    if [ -z "$PYTHON_BIN" ]; then
        if command -v python3 &>/dev/null; then
            FOUND_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "unknown")
            fail "Python 3.11+ is required by pyproject.toml. Found Python $FOUND_VER. Please install Python 3.11 or newer."
        else
            fail "Python 3 (>= 3.11) is not installed or not in PATH."
        fi
    fi

    PY_VER=$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
    info "Python runtime verified ($PYTHON_BIN -> v$PY_VER)"

    # Verify that venv module is functional
    if ! "$PYTHON_BIN" -c 'import venv, ensurepip' 2>/dev/null; then
        fail "Python 'venv' or 'ensurepip' module is missing. On Debian/Ubuntu/Kali, please run: sudo apt-get install -y python3-venv"
    fi
}

# 2. Operating System / Environment Detection
detect_environment() {
    OS_NAME="$(uname -s 2>/dev/null || echo 'Unknown')"
    DISTRO="Linux"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO="${NAME:-Linux}"
    elif [ "$OS_NAME" = "Darwin" ]; then
        DISTRO="macOS"
    fi

    if grep -qi microsoft /proc/version 2>/dev/null || [ -n "${WSL_DISTRO_NAME:-}" ]; then
        DISTRO="$DISTRO (WSL)"
    fi
    info "Platform environment: $DISTRO ($OS_NAME $(uname -m 2>/dev/null || echo ''))"
}

# 3. Setup Virtual Environment (Self-Healing & Idempotent)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
VENV_PYTHON=""

setup_venv() {
    local NEED_CREATE=false

    if [ -d "$VENV_DIR" ]; then
        # Test if existing virtualenv is healthy
        if [ -x "$VENV_DIR/bin/python" ] && "$VENV_DIR/bin/python" -c 'import sys; sys.exit(0)' 2>/dev/null; then
            info "Existing virtual environment verified at $VENV_DIR"
        else
            warn "Existing .venv is broken or points to a non-existent interpreter. Recreating cleanly..."
            rm -rf "$VENV_DIR"
            NEED_CREATE=true
        fi
    else
        NEED_CREATE=true
    fi

    if [ "$NEED_CREATE" = true ]; then
        info "Creating dedicated isolated environment at $VENV_DIR..."
        "$PYTHON_BIN" -m venv "$VENV_DIR" || fail "Failed to create virtual environment with $PYTHON_BIN"
    fi

    VENV_PYTHON="$VENV_DIR/bin/python"
    [ -x "$VENV_PYTHON" ] || fail "Virtual environment Python executable not found at $VENV_PYTHON"
    info "Virtual environment ready"
}

# 4. Install Dependencies & Package
install_package() {
    info "Upgrading pip, setuptools, and wheel in virtual environment..."
    "$VENV_PYTHON" -m pip install --quiet --upgrade pip setuptools wheel || warn "Pip self-upgrade encountered a warning; continuing..."

    local DEV_MODE=false
    for arg in "$@"; do
        if [ "$arg" = "--dev" ] || [ "$arg" = "-e" ] || [ "$arg" = "--editable" ]; then
            DEV_MODE=true
            break
        fi
    done

    info "Installing CrackMapExec+ package..."
    if [ "$DEV_MODE" = true ]; then
        "$VENV_PYTHON" -m pip install --quiet -e "$SCRIPT_DIR[dev]" || fail "Failed to install CrackMapExec+ in development mode."
        info "Installed in editable development mode with test suite dependencies"
    else
        "$VENV_PYTHON" -m pip install --quiet -e "$SCRIPT_DIR" || fail "Failed to install CrackMapExec+."
        info "Installed CrackMapExec+ successfully"
    fi

    # Verify package imports
    local INSTALLED_VER
    INSTALLED_VER=$("$VENV_PYTHON" -c 'import cmeplus; print(cmeplus.__version__)' 2>/dev/null || echo "")
    [ -n "$INSTALLED_VER" ] || fail "Package verification failed: cannot import cmeplus from virtual environment."
    info "Package import verified: cmeplus v$INSTALLED_VER"
}

# 5. Create Standalone Launchers (No virtualenv activation needed)
install_launchers() {
    local USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"

    local COMMAND_NAMES=("crackmapexec+" "cme+" "crackmapexec-plus" "cme-plus" "crackmapexecplus" "cmeplus")

    # A. Install wrappers in ~/.local/bin
    for cmd in "${COMMAND_NAMES[@]}"; do
        local target_wrapper="$USER_BIN/$cmd"
        cat << EOF > "$target_wrapper"
#!/usr/bin/env bash
# CrackMapExec+ Standalone Launcher (No manual virtual environment activation required)
set -e
VENV_PY="$VENV_PYTHON"
if [ ! -x "\$VENV_PY" ]; then
    echo "[!] CrackMapExec+ virtual environment not found at: \$VENV_PY" >&2
    echo "[!] Please run ./install.sh in $SCRIPT_DIR" >&2
    exit 1
fi
exec "\$VENV_PY" -m cmeplus.cli.parser "\$@"
EOF
        chmod 755 "$target_wrapper"
    done
    info "Installed standalone launchers into $USER_BIN"

    # B. Also install into /usr/local/bin if root or writable
    if [ "$EUID" -eq 0 ] || [ -w /usr/local/bin ]; then
        for cmd in "${COMMAND_NAMES[@]}"; do
            local sys_wrapper="/usr/local/bin/$cmd"
            cat << EOF > "$sys_wrapper"
#!/usr/bin/env bash
set -e
VENV_PY="$VENV_PYTHON"
if [ ! -x "\$VENV_PY" ]; then
    echo "[!] CrackMapExec+ virtual environment not found at: \$VENV_PY" >&2
    exit 1
fi
exec "\$VENV_PY" -m cmeplus.cli.parser "\$@"
EOF
            chmod 755 "$sys_wrapper" 2>/dev/null || true
        done
        info "Installed system-wide launchers into /usr/local/bin"
    fi

    # C. Also create repository-local executables ./crackmapexec+ and ./cme+
    for cmd in "crackmapexec+" "cme+"; do
        local local_launcher="$SCRIPT_DIR/$cmd"
        cat << 'EOF' > "$local_launcher"
#!/usr/bin/env bash
# CrackMapExec+ Repository-Local Launcher
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$SCRIPT_DIR/.venv/bin/python"
[ -x "$VENV_PY" ] || VENV_PY="$SCRIPT_DIR/.venv/bin/python3"
if [ ! -x "$VENV_PY" ]; then
    echo "[!] Virtual environment not initialized. Please run ./install.sh first." >&2
    exit 1
fi
exec "$VENV_PY" -m cmeplus.cli.parser "$@"
EOF
        chmod 755 "$local_launcher"
    done
    info "Repository-local launchers ready (./crackmapexec+ and ./cme+)"
}

# 6. Configure Shell PATH Persistence
configure_path() {
    local USER_BIN="$HOME/.local/bin"

    # Add to current installer subshell PATH
    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        export PATH="$USER_BIN:$PATH"
    fi

    # Persist in user shell configuration files if not already present
    local SHELL_FILES=("$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile" "$HOME/.bash_profile")
    local EXPORT_LINE='export PATH="$HOME/.local/bin:$PATH"'
    local CONFIGURED_ANY=false

    for sh_file in "${SHELL_FILES[@]}"; do
        if [ -f "$sh_file" ]; then
            if ! grep -Fq '.local/bin' "$sh_file" 2>/dev/null; then
                echo "" >> "$sh_file"
                echo "# Added by CrackMapExec+ installer" >> "$sh_file"
                echo "$EXPORT_LINE" >> "$sh_file"
                CONFIGURED_ANY=true
            fi
        fi
    done

    # If no shell files existed, create ~/.profile
    if [ "$CONFIGURED_ANY" = false ] && [ ! -f "$HOME/.bashrc" ] && [ ! -f "$HOME/.zshrc" ]; then
        echo "$EXPORT_LINE" >> "$HOME/.profile"
    fi

    info "User PATH persistence ensured ($USER_BIN)"
}

# 7. Verify Clean-Install Contract
verify_contract() {
    local USER_BIN="$HOME/.local/bin"

    info "Verifying execution contract outside activated environment..."

    local VER_OUT
    VER_OUT=$("$USER_BIN/crackmapexec+" --version 2>/dev/null || true)
    if [ -z "$VER_OUT" ]; then
        fail "Installed command '$USER_BIN/crackmapexec+ --version' failed to execute."
    fi
    info "Command verification: $VER_OUT"

    local CME_VER_OUT
    CME_VER_OUT=$("$USER_BIN/cme+" --version 2>/dev/null || true)
    if [ -z "$CME_VER_OUT" ]; then
        fail "Alias command '$USER_BIN/cme+ --version' failed to execute."
    fi
    info "Alias verification: cme+ verified"

    # Run quick doctor check
    if "$USER_BIN/crackmapexec+" doctor >/dev/null 2>&1; then
        info "Diagnostic doctor check: HEALTHY"
    else
        warn "Doctor check returned non-zero. Run 'crackmapexec+ doctor' for details."
    fi
}

# Main Execution Flow
main() {
    print_banner
    check_python
    detect_environment
    setup_venv
    install_package "$@"
    install_launchers
    configure_path
    verify_contract

    echo ""
    echo -e "${BOLD}${GREEN}Installation succeeded!${NC}"
    echo ""
    echo -e "You can now run CrackMapExec+ from ${BOLD}any directory or shell${NC} without activating .venv:"
    echo ""
    echo -e "  ${CYAN}crackmapexec+ --help${NC}"
    echo -e "  ${CYAN}crackmapexec+ doctor${NC}"
    echo -e "  ${CYAN}cme+ --demo${NC}"
    echo ""
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}Note:${NC} To update your current active shell's PATH immediately, run:"
        echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}  or  ${CYAN}source ~/.bashrc${NC}"
        echo ""
    fi
}

main "$@"
