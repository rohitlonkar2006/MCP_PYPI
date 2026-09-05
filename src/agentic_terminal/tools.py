import glob as glob_module
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("agentic_terminal")


def _run_process(command, *, shell: bool = False) -> str:
    """Run a subprocess and return a single string of stdout/stderr."""
    result = subprocess.run(
        command,
        shell=shell,
        capture_output=True,
        text=True,
        check=False,
    )

    output_parts = []
    if result.stdout:
        output_parts.append(result.stdout.strip())
    if result.stderr:
        output_parts.append(result.stderr.strip())
    if result.returncode not in (0, None):
        output_parts.append(f"Command exited with code {result.returncode}.")

    return "\n".join(part for part in output_parts if part)


@mcp.tool
def bash(command: str) -> str:
    """Execute a shell command and return its output."""
    return _run_process(command, shell=True)


@mcp.tool
def python_code(code: str) -> str:
    """Run Python code using the current interpreter and return its output."""
    return _run_process([sys.executable, "-c", code], shell=False)


@mcp.tool
def python_file(file: str) -> str:
    """Execute a Python file and return its output."""
    return _run_process([sys.executable, str(file)], shell=False)


@mcp.tool
def glob(pattern: str):
    """Return a list of files that match the given glob pattern."""
    return glob_module.glob(pattern, recursive=True)


@mcp.tool
def grep(pattern: str, file: str) -> str:
    """Search for a regex pattern in a file and return matching lines."""
    matches: list[str] = []
    file_path = Path(file)

    if not file_path.exists():
        return f"File not found: {file}"

    with file_path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            if re.search(pattern, line):
                matches.append(f"{line_number}: {line.rstrip()}")

    return "\n".join(matches)


@mcp.tool
def read_file(file: str) -> str:
    """Read the contents of a file and return them as a string."""
    file_path = Path(file)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file}")
    return file_path.read_text(encoding="utf-8", errors="replace")


@mcp.tool
def write_file(file: str, content: str) -> str:
    """Write text content to a file and return a confirmation message."""
    file_path = Path(file)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {file_path}"


@mcp.tool
def create_folder(folder: str) -> str:
    """Create a folder and any missing parent folders."""
    folder_path = Path(folder)
    folder_path.mkdir(parents=True, exist_ok=True)
    return f"Created folder: {folder_path}"


@mcp.tool
def delete_folder(folder: str) -> str:
    """Delete a folder or file at the given path."""
    path = Path(folder)
    if not path.exists():
        return f"Path not found: {folder}"

    if path.is_dir():
        shutil.rmtree(path)
        return f"Deleted folder: {path}"

    path.unlink()
    return f"Deleted file: {path}"


__all__ = [
    "bash",
    "python_code",
    "python_file",
    "glob",
    "grep",
    "read_file",
    "write_file",
    "create_folder",
    "delete_folder",
    "mcp",
]