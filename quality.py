"""根目录质量入口：python quality.py <目标> <命令>，失败立即返回原退出码。"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    """目标为 backend/frontend/all；只有 format 命令会主动格式化源码。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=["backend", "frontend", "all"])
    parser.add_argument(
        "command", choices=["lint", "format", "format-check", "test", "quality-check"]
    )
    args = parser.parse_args()
    backend = {
        "lint": [[sys.executable, "-m", "ruff", "check", "."]],
        "format": [[sys.executable, "-m", "ruff", "format", "."]],
        "format-check": [[sys.executable, "-m", "ruff", "format", "--check", "."]],
        "test": [[sys.executable, "-m", "pytest", "tests", "-q"]],
    }
    backend["quality-check"] = backend["lint"] + backend["format-check"] + backend["test"]
    npm = shutil.which("npm") or "npm"
    frontend_command = {"format-check": "format:check", "test": "test:run"}.get(
        args.command, args.command
    )
    for target in ["backend", "frontend"] if args.target == "all" else [args.target]:
        commands = (
            backend[args.command] if target == "backend" else [[npm, "run", frontend_command]]
        )
        for command in commands:
            print(f"[{target}] {' '.join(command)}", flush=True)
            result = subprocess.run(command, cwd=ROOT if target == "backend" else ROOT / "frontend")
            if result.returncode:
                return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
