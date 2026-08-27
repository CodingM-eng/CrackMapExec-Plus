#!/usr/bin/env bash
# ==============================================================================
# CrackMapExec+ Debian (.deb) Package Builder
# ==============================================================================
set -euo pipefail

CYAN="\033[0;36m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m"

echo -e "${CYAN}====================================================${NC}"
echo -e "${CYAN} Building Debian Package: crackmapexec-plus         ${NC}"
echo -e "${CYAN}====================================================${NC}"

# Check for Debian build tools
if ! command -v dpkg-buildpackage &>/dev/null; then
    echo -e "${YELLOW}Warning: dpkg-buildpackage not found.${NC}"
    echo -e "Install Debian build tools on Kali/Debian/Ubuntu with:"
    echo -e "  ${CYAN}sudo apt-get install -y build-essential debhelper dh-python python3-all python3-setuptools${NC}"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# Clean prior build artifacts
echo -e "${GREEN}* Cleaning previous build artifacts...${NC}"
rm -rf debian/.debhelper/ debian/crackmapexec-plus/ debian/files debian/*.substvars debian/*.log build/ dist/

# Run dpkg-buildpackage
echo -e "${GREEN}* Running dpkg-buildpackage (-us -uc -b)...${NC}"
dpkg-buildpackage -us -uc -b

echo -e "\n${GREEN}✓ Build completed successfully!${NC}"
echo -e "Package output is located in parent directory: ../crackmapexec-plus_*.deb\n"
echo -e "To install and test on your Kali/Debian system:"
echo -e "  ${CYAN}sudo apt install ../crackmapexec-plus_*.deb${NC}"
echo -e "  ${CYAN}crackmapexec+ --version${NC}"
echo -e "  ${CYAN}cme+ --version${NC}"
