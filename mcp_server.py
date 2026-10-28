from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
mcp = FastMCP("coding-debugger")

SKIP = {".git", "venv", ".venv", "__pycache__", "node_modules", ".idea", "dist", "build"}
MAX_CHARS = 6000

ROOT = os.path.realpath(os.getenv("DEBUG_ROOT", "."))



def clip(text: str) -> str:
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS] + f"\n...[truncated, {len(text)} chars total]"
    return text
@mcp.tool()
def safe_path(path: str) -> str:
    """Resolve a path and make sure it stays inside ROOT."""
    full = os.path.realpath(os.path.join(ROOT, path))
    if os.path.commonpath([full, ROOT]) != ROOT:
        raise ValueError(f"Path '{path}' is outside the allowed root.")
    return full

@mcp.tool()
def list_files(directory: str = ".", max_results: int = 150) -> str:
    """List files in a directory recursively, skipping junk folders."""
    try:
        base = safe_path(directory)
        results = []
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in SKIP]
            for f in files:
                results.append(os.path.relpath(os.path.join(root, f), ROOT))
                if len(results) >= max_results:
                    return clip("\n".join(results) + f"\n...truncated at {max_results} files")
        return clip("\n".join(results) or "No files found.")
    except Exception as e:
        return f"Error listing files: {e}"

@mcp.tool()
def read_file(path: str, start_line: int = 1, end_line: int = 150) -> str:
    """Read a file between line numbers (max 150 lines per call)."""
    try:
        full = safe_path(path)
        start_line = max(1, start_line)
        end_line = min(end_line, start_line + 149)
        with open(full, "r", errors="replace") as f:
            lines = f.readlines()
        chunk = "".join(lines[start_line - 1:end_line])
        return clip(chunk or f"No content in lines {start_line}-{end_line} (file has {len(lines)} lines).")
    except Exception as e:
        return f"Error reading {path}: {e}"


@mcp.tool()
def search_code(pattern: str, directory: str = ".") -> str:
    """Regex search over code and text files (max 40 lines). Use it to find which file and line matters."""
    try:
        base = safe_path(directory)
        r = subprocess.run(
            ["rg", "-n", "--max-count", "5", "--max-columns", "200",
             "-g", "!.venv", "-g", "!venv", "-g", "!node_modules", "-g", "!.git",
             "-g", "*.py", "-g", "*.md", "-g", "*.txt", "-g", "*.yaml", "-g", "*.yml",
             "--", pattern, base],
            capture_output=True, text=True, timeout=15,
        )
        out = (r.stdout or r.stderr or "No matches found.").replace(ROOT + os.sep, "")
        return clip("\n".join(out.splitlines()[:40]))
    except Exception as e:
        return f"Error running search: {e}"

import shlex  # at the top

ALLOWED_COMMANDS = {"python", "pytest", "ruff"}

@mcp.tool()
def run_command(command: str) -> str:
    """Run an allowed program (python, pytest, ruff) in the project to reproduce or verify a bug. Shows exit code and output."""
    parts = shlex.split(command)
    if not parts or parts[0] not in ALLOWED_COMMANDS:
        return f"Refused: only {sorted(ALLOWED_COMMANDS)} are allowed."
    if parts[0] == "python":
        parts[0] = sys.executable   # add: import sys
    try:
        r = subprocess.run(parts, cwd=ROOT, capture_output=True, text=True, timeout=60)
        return clip(f"exit code {r.returncode}\n{r.stdout}{r.stderr}".replace(ROOT + os.sep, ""))
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def find_symbol(name: str) -> str:
    """Find where a function, class or variable is defined and where it is used."""
    import re
    n = re.escape(name)
    def rg(p):
        r = subprocess.run(["rg", "-n", "--max-count", "5", "--max-columns", "200",
                            "-g", "*.py", "-g", "!.venv", "--", p, ROOT],
                           capture_output=True, text=True, timeout=15)
        return (r.stdout or "none").replace(ROOT + os.sep, "")
    return clip(f"DEFINED:\n{rg(rf'(def|class)\s+{n}\b|^{n}\s*=')}\n\nUSED:\n{rg(rf'\b{n}\b')}")

if __name__ == "__main__":

    mcp.run()

## to get out put at the terminal we need to create a client that capture the output and 
##send it to the terminal.
## otherwise launhc a mcp client directly 
