"""Installation Method Detector & Package Updater Adapter."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from enum import Enum
from pathlib import Path


class InstallationMethod(str, Enum):
    PIPX = "pipx"
    EDITABLE = "editable development install"
    VIRTUALENV = "virtualenv"
    DEBIAN = "Debian package"
    SYSTEM = "system package"


def detect_installation_method() -> InstallationMethod:
    """Detect how CrackMapExec+ is currently installed and executed."""
    # 1. Check Debian package path
    pkg_file = Path(__file__).resolve()
    if "/usr/lib/python3/dist-packages" in str(pkg_file) or "/usr/share" in str(pkg_file):
        return InstallationMethod.DEBIAN

    # 2. Check for pipx environment
    prefix_str = str(sys.prefix).lower()
    if "pipx" in prefix_str or "pipx" in os.environ.get("PIPX_HOME", "").lower():
        return InstallationMethod.PIPX
    if Path(sys.prefix).parent.name.lower() == "venvs" and "pipx" in str(Path(sys.prefix).parent.parent).lower():
        return InstallationMethod.PIPX

    # 3. Check for editable development install (src tree in local git repo)
    repo_root = pkg_file.parents[3]  # src/cmeplus/update/installer.py -> root
    if (repo_root / "pyproject.toml").exists() and (repo_root / ".git").exists():
        return InstallationMethod.EDITABLE

    # 4. Standard Virtualenv
    if sys.prefix != sys.base_prefix:
        return InstallationMethod.VIRTUALENV

    # 5. System wide
    return InstallationMethod.SYSTEM


def execute_update(
    method: InstallationMethod,
    repo: str = "CodingM-eng/CrackMapExec-Plus",
) -> tuple[bool, str]:
    """Execute update operation according to the detected installation method.

    Returns:
        (success, message)
    """
    git_url = f"git+https://github.com/{repo}.git"

    if method == InstallationMethod.PIPX:
        pipx_bin = shutil.which("pipx") or "pipx"
        try:
            res = subprocess.run(
                [pipx_bin, "install", "--force", git_url],
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if res.returncode == 0:
                return True, "Successfully updated via pipx."
            return False, f"pipx upgrade failed: {res.stderr.strip() or res.stdout.strip()}"
        except Exception as exc:
            return False, f"Failed to execute pipx update: {exc}"

    elif method == InstallationMethod.EDITABLE:
        repo_root = Path(__file__).resolve().parents[3]
        git_bin = shutil.which("git") or "git"
        try:
            # 1. Git pull
            pull_res = subprocess.run(
                [git_bin, "pull"],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
            )
            if pull_res.returncode != 0:
                return False, f"Git pull failed: {pull_res.stderr.strip()}"

            # 2. Pip install -e .
            pip_res = subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                cwd=str(repo_root),
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if pip_res.returncode == 0:
                return True, "Successfully pulled latest commits and re-installed editable package."
            return False, f"pip install -e failed: {pip_res.stderr.strip()}"
        except Exception as exc:
            return False, f"Failed to execute editable development update: {exc}"

    elif method == InstallationMethod.VIRTUALENV:
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--upgrade", git_url],
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
            if res.returncode == 0:
                return True, "Successfully updated package inside active virtualenv."
            return False, f"Virtualenv pip update failed: {res.stderr.strip()}"
        except Exception as exc:
            return False, f"Failed to execute virtualenv update: {exc}"

    elif method == InstallationMethod.DEBIAN:
        msg = (
            "Update method not supported automatically.\n\n"
            "Detected installation:\n"
            "Debian package\n\n"
            "Use your package manager to update CrackMapExec+:\n"
            "  sudo apt update && sudo apt install --only-upgrade crackmapexec-plus"
        )
        return False, msg

    else:
        msg = (
            "Update method not supported automatically for system-wide installation.\n\n"
            "Detected installation:\n"
            "System package\n\n"
            "Please update via pipx, apt, or your system package manager."
        )
        return False, msg
