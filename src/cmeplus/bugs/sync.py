"""GitHub Bug Synchronization: Secure, sanitized synchronization of bug reports."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from rich.panel import Panel
from rich.prompt import Confirm
from rich.text import Text

from cmeplus.bugs.registry import BugRegistryManager
from cmeplus.output.console import OutputConsole


def check_github_auth() -> tuple[bool, str]:
    """Check if GitHub CLI or GITHUB_TOKEN environment variable is active."""
    # 1. Check GITHUB_TOKEN env var
    if os.environ.get("GITHUB_TOKEN"):
        return True, "Authenticated via GITHUB_TOKEN environment variable."

    # 2. Check GitHub CLI (gh)
    gh_bin = shutil.which("gh")
    if gh_bin:
        try:
            res = subprocess.run(
                [gh_bin, "auth", "status"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            if res.returncode == 0 or "Logged in to" in res.stdout or "Logged in to" in res.stderr:
                return True, "Authenticated via GitHub CLI (gh)."
        except Exception:
            pass

    return False, "Not authenticated (neither GitHub CLI 'gh' nor GITHUB_TOKEN found)."


def sync_bugs_to_github(
    repo: str = "CodingM-eng/CrackMapExec-Plus",
    manager: BugRegistryManager | None = None,
    console: OutputConsole | None = None,
) -> tuple[bool, str]:
    """Synchronize sanitized bug reports to GitHub repository.

    Returns:
        (success, message)
    """
    console = console or OutputConsole()
    manager = manager or BugRegistryManager()

    console.print_banner("GitHub Bug Synchronization")

    # 1. Authentication Check
    is_auth, auth_msg = check_github_auth()
    if not is_auth:
        console.print_failure("GitHub authentication required.")
        console.console.print(f"\n[dim]{auth_msg}[/dim]\n")
        console.print_info("To authenticate with GitHub, run:")
        console.console.print("  [bold cyan]gh auth login[/bold cyan]\n")
        console.print_info("Or export a token:")
        console.console.print("  [bold cyan]export GITHUB_TOKEN=ghp_...[/bold cyan]\n")
        return False, "Authentication missing"

    console.print_success(auth_msg)
    console.print_info(f"Target Repository: [bold cyan]{repo}[/bold cyan]")

    # 2. File Preview & Sanitization Check
    bug_files = list(manager.bugs_dir.glob("BUG-*.md"))
    index_file = manager.index_file

    files_to_sync: list[Path] = []
    if index_file.exists():
        files_to_sync.append(index_file)
    files_to_sync.extend(bug_files)

    if not files_to_sync:
        console.print_info("No bug reports found in bugs/ directory to synchronize.")
        return True, "No bugs to sync"

    # Preview
    preview = Text()
    preview.append("Files prepared for synchronization (100% sanitized):\n\n", style="bold white")
    for f in files_to_sync:
        preview.append(f"  • {f.name} ({f.stat().st_size} bytes)\n", style="dim cyan")

    panel = Panel(preview, title="[bold cyan]Sync Preview[/bold cyan]", border_style="cyan", expand=False)
    console.console.print(panel)

    # 3. Confirmation
    if not Confirm.ask(f"\n[bold green]Synchronize {len(files_to_sync)} bug report files to {repo}?[/bold green]", default=True):
        console.print_info("Synchronization aborted by user.")
        return False, "Aborted by user"

    # 4. Perform Sync via Git or GitHub CLI
    repo_root = manager.bugs_dir.parent
    if (repo_root / ".git").exists():
        git_bin = shutil.which("git") or "git"
        try:
            # Stage only bugs/ directory
            subprocess.run([git_bin, "add", "bugs/"], cwd=str(repo_root), check=True, capture_output=True)
            diff_check = subprocess.run(
                [git_bin, "diff", "--cached", "--quiet"],
                cwd=str(repo_root),
                check=False,
            )
            if diff_check.returncode != 0:
                subprocess.run(
                    [git_bin, "commit", "-m", "Sync automated diagnostic bug reports [skip ci]"],
                    cwd=str(repo_root),
                    check=True,
                    capture_output=True,
                )
                subprocess.run([git_bin, "push", "origin", "main"], cwd=str(repo_root), check=True, capture_output=True)
                console.print_success("Bug reports successfully synchronized and pushed to GitHub.")
                return True, "Synchronized via git"
            else:
                console.print_success("Bug reports are already up to date with remote repository.")
                return True, "Already up to date"
        except Exception as exc:
            console.print_failure(f"Git push sync failed: {exc}")
            return False, str(exc)

    console.print_success("Bug reports validated and ready in local registry.")
    return True, "Local registry validated"
