"""Regression tests for package discovery, console entry points, and module execution."""

import importlib
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore


def test_subpackages_importable():
    """Verify all subpackages have __init__.py and are cleanly importable."""
    subpackages = [
        "cmeplus",
        "cmeplus.cli",
        "cmeplus.core",
        "cmeplus.protocols",
        "cmeplus.modules",
        "cmeplus.modules.builtin",
        "cmeplus.video",
        "cmeplus.config",
        "cmeplus.history",
        "cmeplus.output",
        "cmeplus.reports",
        "cmeplus.demo",
    ]
    for pkg in subpackages:
        mod = importlib.import_module(pkg)
        assert mod is not None


def test_pyproject_scripts_metadata():
    """Verify that pyproject.toml defines required console scripts."""
    root = Path(__file__).resolve().parent.parent
    pyproject_path = root / "pyproject.toml"
    assert pyproject_path.is_file()

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    scripts = data.get("project", {}).get("scripts", {})
    assert "crackmapexec+" in scripts
    assert "cme+" in scripts
    assert scripts["crackmapexec+"] == "cmeplus.cli.parser:main"
    assert scripts["cme+"] == "cmeplus.cli.parser:main"


def test_module_entry_point_execution():
    """Verify execution via `python -m cmeplus --version` without relying on global PATH."""
    result = subprocess.run(
        [sys.executable, "-m", "cmeplus", "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "CrackMapExec+ 0.1.0" in result.stdout


def test_module_entry_point_about():
    """Verify execution via `python -m cmeplus --about`."""
    result = subprocess.run(
        [sys.executable, "-m", "cmeplus", "--about"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "System Information" in result.stdout
    assert "CrackMapExec+" in result.stdout
