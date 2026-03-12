from __future__ import annotations

import os
import sys
from pathlib import Path


def _venv_python(project_root: Path) -> Path:
    if os.name == "nt":
        return project_root / "venv" / "Scripts" / "python.exe"
    return project_root / "venv" / "bin" / "python"


def main() -> int:
    project_root = Path(__file__).resolve().parent
    venv_python = _venv_python(project_root)

    if not venv_python.exists():
        print(
            f"Could not find project venv python at: {venv_python}\n"
            "Create it with:\n"
            "  python3 -m venv venv\n"
            "  ./venv/bin/python -m pip install -r requirements.txt"
        )
        return 2

    if len(sys.argv) < 2:
        print("Usage:\n  python run.py <script.py> [args...]\n")
        print("Example:\n  python run.py notebooks/test_briefing.py\n")
        return 2

    args = [str(venv_python), *sys.argv[1:]]
    os.execv(str(venv_python), args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

