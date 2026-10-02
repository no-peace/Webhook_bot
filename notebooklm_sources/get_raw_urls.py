#!/usr/bin/env python3
"""
sync_to_notebook.py — Automatically downloads and groups repo files into .md chunks for AI Notebooks.

============================================================
USAGE
============================================================
  # Fetch from public repo and generate .md files in an 'ai_sources' folder
  python sync_to_notebook.py --repo no-peace/Hoho_manager

  # Pass token if rate limited
  python sync_to_notebook.py --repo no-peace/Hoho_manager --token ghp_YOUR_TOKEN
============================================================
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from collections import defaultdict

# Ignore heavy/unnecessary files
SKIP_DIRS = {".git", "node_modules", "dist", "build", ".next", "coverage", "__pycache__", "assets", ".vite", "test"}
SKIP_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".lock", ".sqlite", ".sqlite-shm", ".sqlite-wal", ".exe", ".node", ".map", ".d.ts"}
SKIP_NAMES = {".DS_Store", "Thumbs.db", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"}

def get_raw_content(owner_repo: str, branch: str, path: str, token: str = None) -> str:
    url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{path}"
    headers = {"User-Agent": "notebook-sync-script"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"// ERROR FETCHING FILE: {e}"

def fetch_tree(owner_repo: str, branch: str, token: str = None) -> list:
    url = f"https://api.github.com/repos/{owner_repo}/git/trees/{branch}?recursive=1"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "notebook-sync-script"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return [item["path"] for item in data.get("tree", []) if item.get("type") == "blob"]
    except urllib.error.HTTPError as e:
        sys.exit(f"GitHub API Error: {e.code}. If rate limited, use --token.")

def smart_group_path(path: str) -> str:
    """Smartly groups files into logical markdown chunks based on dynamic architecture"""
    parts = path.split('/')
    
    if len(parts) == 1:
        return "root_config"
        
    top_dir = parts[0]
    
    # Handle standard monorepo structures (client/server/bot)
    if top_dir in ["client", "server", "bot", "shared"]:
        if len(parts) > 2 and parts[1] == "src":
            return f"{top_dir}_{parts[2]}" # e.g., client_components, server_actions
        return f"{top_dir}_core"
        
    # Handle packages/ workspaces (like Discohook)
    if top_dir == "packages" and len(parts) > 1:
        if len(parts) > 3 and parts[2] == "src":
            return f"pkg_{parts[1]}_{parts[3]}" # e.g., pkg_bot_commands
        return f"pkg_{parts[1]}_core" # e.g., pkg_site_core
        
    return f"{top_dir}_misc"

def main():
    parser = argparse.ArgumentParser(description="Download and group repo code into .md files.")
    parser.add_argument("--repo", required=True, help="owner/name (e.g., no-peace/Hoho_manager)")
    parser.add_argument("--branch", default="main", help="Branch (default: main)")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub token")
    parser.add_argument("--outdir", default="ai_sources", help="Output directory for .md files")
    args = parser.parse_args()

    print(f"Fetching file tree from {args.repo}...")
    all_paths = fetch_tree(args.repo, args.branch, args.token)
    
    # Filter paths
    valid_paths = []
    for path in all_paths:
        if any(f"/{d}/" in f"/{path}" for d in SKIP_DIRS) or any(path.startswith(f"{d}/") for d in SKIP_DIRS): continue
        if any(path.endswith(ext) for ext in SKIP_EXTS): continue
        if path.split('/')[-1] in SKIP_NAMES: continue
        valid_paths.append(path)

    # Group paths
    groups = defaultdict(list)
    for path in valid_paths:
        groups[smart_group_path(path)].append(path)

    os.makedirs(args.outdir, exist_ok=True)

    # Download and write
    for group_name, paths in groups.items():
        out_file = Path(args.outdir) / f"{group_name}.md"
        print(f"\nBuilding {out_file.name} ({len(paths)} files)...")
        
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(f"# Repository Context Group: {group_name}\n")
            f.write(f"# Source Repository: {args.repo}\n\n")
            
            for path in paths:
                print(f"  -> Downloading {path}...")
                content = get_raw_content(args.repo, args.branch, path, args.token)
                ext = path.split('.')[-1] if '.' in path else "text"
                
                f.write(f"### File: `{path}`\n")
                f.write(f"```{ext}\n")
                f.write(content)
                f.write(f"\n```\n\n")

    print(f"\n✅ Success! All sources have been grouped and saved to the '{args.outdir}' folder.")
    print("Please upload these .md files to your Google Notebook sources.")

if __name__ == "__main__":
    main()