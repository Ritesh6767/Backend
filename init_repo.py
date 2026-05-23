#!/usr/bin/env python3
from pathlib import Path
from dulwich.repo import Repo
import time

REPO_PATH = Path(__file__).parent
REPO_URL = "https://github.com/Ritesh6767/Backend"

EXCLUDE_DIRS = {'.venv', '__pycache__', '.git', 'tests'}
EXCLUDE_FILES = {'*.pyc', '*.db', '*.log', 'init_repo.py'}

def should_skip(path):
    parts = path.relative_to(REPO_PATH).parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    if path.name in EXCLUDE_FILES or path.name.endswith(('.pyc', '.db', '.log')):
        return True
    return False

def init_repo():
    git_dir = REPO_PATH / '.git'
    if git_dir.exists():
        print("Repository already exists.")
        return
    
    print("Initializing Git repository...")
    repo = Repo.init(str(REPO_PATH))
    repo.do_commit(b'Initial internship assignment submission', committer=b'Ritesh <ritesh@example.com>')
    print("✅ Repository created with initial commit.")
    print("\nManual next steps to push code:")
    print(f"1. Download Git: https://git-scm.com/download/win")
    print(f"2. Install it (accept all defaults)")
    print(f"3. Open PowerShell in breakout folder and run:")
    print(f"   git remote add origin {REPO_URL}")
    print(f"   git push -u origin main")

if __name__ == '__main__':
    init_repo()
