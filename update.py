#!/usr/bin/env python3
"""
ASO Screenshot Skill — Version Check & Update

Checks GitHub for the latest release and updates the local installation.

Usage:
  python3 update.py --check     # Check if a new version is available
  python3 update.py --update    # Pull the latest version
  python3 update.py --version   # Show current local version
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error

REPO = "abutun/claude-skill-aso-cosmicmeta-ss"
GITHUB_API = f"https://api.github.com/repos/{REPO}/releases/latest"
GITHUB_URL = f"https://github.com/{REPO}"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(SCRIPT_DIR, "VERSION")


def get_local_version():
    """Read the local VERSION file."""
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE) as f:
            return f.read().strip()
    return "unknown"


def get_remote_version():
    """Fetch the latest release from GitHub API."""
    req = urllib.request.Request(
        GITHUB_API,
        headers={"Accept": "application/vnd.github.v3+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            release = json.loads(resp.read().decode("utf-8"))
            if release:
                tag = release.get("tag_name", "")
                # Strip 'v' prefix if present
                return tag.lstrip("v")
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError):
        pass
    return None


def parse_version(v):
    """Parse version string into comparable tuple."""
    try:
        return tuple(int(x) for x in v.split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def check_update():
    """Check if a newer version is available on GitHub."""
    local = get_local_version()
    print(f"  Local version:  {local}")

    remote = get_remote_version()
    if remote is None:
        print("  Remote version: could not reach GitHub")
        return False

    print(f"  Latest version: {remote}")

    if parse_version(remote) > parse_version(local):
        print(f"\n  New version available: {remote}")
        print(f"  Run: python3 update.py --update")
        print(f"  Or:  cd {SCRIPT_DIR} && git pull")
        return True
    else:
        print("\n  You are up to date.")
        return False


def do_update():
    """Pull the latest version from GitHub."""
    local = get_local_version()
    remote = get_remote_version()

    if remote and parse_version(remote) <= parse_version(local):
        print(f"  Already up to date (v{local}).")
        return True

    # Check if we're in a git repo
    git_dir = os.path.join(SCRIPT_DIR, ".git")
    if os.path.isdir(git_dir):
        print("  Updating via git pull...")
        result = subprocess.run(
            ["git", "pull", "--rebase"],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            new_version = get_local_version()
            print(f"  Updated to v{new_version}")

            # Regenerate device frames after update
            print("  Regenerating device frames...")
            subprocess.run(
                [sys.executable, os.path.join(SCRIPT_DIR, "generate_frame.py")],
                cwd=SCRIPT_DIR,
            )
            return True
        else:
            print(f"  Git pull failed: {result.stderr.strip()}")
            print(f"  Try manually: cd {SCRIPT_DIR} && git pull")
            return False
    else:
        # Not a git repo — likely copied into skills dir
        print("  Not a git repository. To update manually:")
        print(f"  1. Download the latest from {GITHUB_URL}")
        print(f"  2. Replace the contents of {SCRIPT_DIR}")
        print(f"  3. Run: python3 generate_frame.py")
        return False


def main():
    p = argparse.ArgumentParser(
        description="ASO Screenshot Skill — Version Check & Update",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--check", action="store_true", help="Check if a new version is available"
    )
    group.add_argument(
        "--update", action="store_true", help="Pull the latest version from GitHub"
    )
    group.add_argument(
        "--version", action="store_true", help="Show current local version"
    )

    args = p.parse_args()

    if args.version:
        print(f"  v{get_local_version()}")
    elif args.check:
        check_update()
    elif args.update:
        do_update()


if __name__ == "__main__":
    main()
