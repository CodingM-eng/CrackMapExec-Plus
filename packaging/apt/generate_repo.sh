#!/usr/bin/env bash
# ==============================================================================
# CrackMapExec+ APT Repository Metadata Generator
# Generates standard Packages, Packages.gz, and Release metadata files
# ==============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_NAME="stable"
COMPONENT="main"
ARCH="binary-all"
POOL_DIR="$REPO_ROOT/pool/$COMPONENT"
DISTS_DIR="$REPO_ROOT/dists/$DIST_NAME/$COMPONENT/$ARCH"

echo "Setting up APT repository layout in: $REPO_ROOT"
mkdir -p "$POOL_DIR"
mkdir -p "$DISTS_DIR"

# Copy deb files to pool if present in parent directory
if ls "$REPO_ROOT"/../*.deb 1> /dev/null 2>&1; then
    cp "$REPO_ROOT"/../*.deb "$POOL_DIR/"
fi

echo "* Scanning packages in pool/..."
if command -v dpkg-scanpackages &>/dev/null; then
    cd "$REPO_ROOT"
    dpkg-scanpackages --multiversion "pool/$COMPONENT" > "$DISTS_DIR/Packages"
    gzip -9c "$DISTS_DIR/Packages" > "$DISTS_DIR/Packages.gz"
    echo "✓ Generated Packages and Packages.gz"
elif command -v apt-ftparchive &>/dev/null; then
    cd "$REPO_ROOT"
    apt-ftparchive packages "pool/$COMPONENT" > "$DISTS_DIR/Packages"
    gzip -9c "$DISTS_DIR/Packages" > "$DISTS_DIR/Packages.gz"
    echo "✓ Generated Packages and Packages.gz"
else
    echo "Notice: dpkg-scanpackages / apt-ftparchive not found. Generating basic Packages manifest."
    # Basic fallback generator
    > "$DISTS_DIR/Packages"
    for deb in "$POOL_DIR"/*.deb; do
        if [ -f "$deb" ]; then
            dpkg-deb -I "$deb" control >> "$DISTS_DIR/Packages" 2>/dev/null || true
            echo "Filename: pool/$COMPONENT/$(basename "$deb")" >> "$DISTS_DIR/Packages"
            echo "Size: $(wc -c < "$deb")" >> "$DISTS_DIR/Packages"
            echo "SHA256: $(sha256sum "$deb" | cut -d' ' -f1)" >> "$DISTS_DIR/Packages"
            echo "" >> "$DISTS_DIR/Packages"
        fi
    done
    gzip -9c "$DISTS_DIR/Packages" > "$DISTS_DIR/Packages.gz"
fi

# Generate Release file
echo "* Generating Release manifest..."
RELEASE_FILE="$REPO_ROOT/dists/$DIST_NAME/Release"
cat <<EOF > "$RELEASE_FILE"
Origin: CrackMapExec-Plus
Label: CrackMapExec+ Repository
Suite: $DIST_NAME
Codename: $DIST_NAME
Architectures: all amd64 arm64
Components: $COMPONENT
Description: Official APT repository for CrackMapExec+ security testing framework
Date: $(date -Ru)
EOF

echo "✓ Generated dists/$DIST_NAME/Release"

# Optional GPG signature
if [ -n "${GPG_KEY_ID:-}" ]; then
    echo "* Signing Release file with GPG key: $GPG_KEY_ID"
    gpg --default-key "$GPG_KEY_ID" -abs -o "$REPO_ROOT/dists/$DIST_NAME/Release.gpg" "$RELEASE_FILE"
    gpg --default-key "$GPG_KEY_ID" --clearsign -o "$REPO_ROOT/dists/$DIST_NAME/InRelease" "$RELEASE_FILE"
    echo "✓ Signed Release.gpg and InRelease"
else
    echo "* Note: Set GPG_KEY_ID to sign Release metadata with GPG."
fi

echo ""
echo "APT Repository ready at: $REPO_ROOT"
