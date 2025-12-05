from pathlib import Path
import argparse
import sys
from .codex_brain import ingest_files

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Ingest code files with Codex and populate .dev_brain/summaries"
    )
    parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Project root to scan for source files (default: current directory)",
    )
    parser.add_argument(
        "--glob",
        type=str,
        default="**/*.py",
        help="Glob pattern relative to root to select files (default: '**/*.py')",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    pattern = args.glob

    # Exclude .dev_brain and other common excludes if needed, but glob usually handles it if careful
    # For now, just simple glob
    file_paths = [p for p in root.glob(pattern) if p.is_file() and ".dev_brain" not in p.parts]

    print(f">>> Codex Ingest – root={root}, files={len(file_paths)}")
    
    if not file_paths:
        print("No files found.")
        return

    ingest_files(file_paths)

if __name__ == "__main__":
    main()
