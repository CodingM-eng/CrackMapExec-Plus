# CrackMapExec+ APT Repository Deployment Guide

This directory provides the infrastructure and tooling to host an official Debian/Kali APT package repository for **CrackMapExec+** (`crackmapexec-plus`).

---

## 1. Structure of the Repository

Standard Debian repository directory layout:

```text
packaging/apt/
├── generate_repo.sh          # Repository generation script
├── pool/
│   └── main/
│       └── crackmapexec-plus_0.1.0-1_all.deb
└── dists/
    └── stable/
        ├── Release
        ├── Release.gpg
        ├── InRelease
        └── main/
            └── binary-all/
                ├── Packages
                └── Packages.gz
```

---

## 2. Generating Repository Metadata

1. Build the Debian package:
   ```bash
   ./packaging/build_deb.sh
   ```
2. Place the resulting `crackmapexec-plus_*.deb` into `packaging/apt/pool/main/`.
3. Run the repository generation script:
   ```bash
   ./packaging/apt/generate_repo.sh
   ```

To sign the repository with your release GPG key:
```bash
GPG_KEY_ID="security@example.com" ./packaging/apt/generate_repo.sh
```

---

## 3. End-User Installation via APT

Once published to a web server (e.g. GitHub Pages or S3 CDN), users configure APT with:

```bash
# 1. Download repository GPG signing key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://repo.example.com/cmeplus-archive-keyring.gpg | sudo tee /etc/apt/keyrings/crackmapexec-plus.gpg > /dev/null

# 2. Add repository source list
echo "deb [signed-by=/etc/apt/keyrings/crackmapexec-plus.gpg] https://repo.example.com/apt stable main" | sudo tee /etc/apt/sources.list.d/crackmapexec-plus.list

# 3. Update and install
sudo apt update
sudo apt install crackmapexec-plus
```

Both entry points are then available system-wide:
```bash
crackmapexec+ --version
cme+ --version
```
