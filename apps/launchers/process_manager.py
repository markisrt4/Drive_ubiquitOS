from __future__ import annotations

import os
import signal
import subprocess
import time
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


DEFAULT_DISPLAY_APP_PATTERNS = (
    "sdrpp",
    "sdr\\+\\+",
    "chromium",
    "chromium-browser",
    "streamlit",
)

PROTECTED_PROCESS_PATTERNS = (
    "vncserver",
    "tigervncserver",
    "Xtigervnc",
    "Xvnc",
    "xstartup",
    "openbox",
)


@dataclass(frozen=True, slots=True)
class ProcessInfo:
    pid: int
    command_line: str
    display: str | None


def find_matching_processes(pattern: str) -> tuple[ProcessInfo, ...]:
    result = subprocess.run(
        ["pgrep", "-f", pattern],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )

    matches: list[ProcessInfo] = []
    for pid_text in result.stdout.splitlines():
        if not pid_text.strip().isdigit():
            continue

        pid = int(pid_text)
        command_line = _process_command_line(pid)
        if not command_line:
            continue

        matches.append(
            ProcessInfo(
                pid=pid,
                command_line=command_line,
                display=_process_display(pid),
            )
        )

    return tuple(matches)


def is_process_running(pattern: str) -> bool:
    return bool(find_matching_processes(pattern))


def terminate_process(
    process: subprocess.Popen[bytes] | subprocess.Popen[str],
    *,
    timeout_seconds: float = 5.0,
) -> None:
    if process.poll() is not None:
        return

    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait(timeout=timeout_seconds)
    except ProcessLookupError:
        pass


def close_display_apps(
    display: str,
    patterns: Iterable[str] = DEFAULT_DISPLAY_APP_PATTERNS,
    *,
    delay_seconds: float = 0.0,
) -> None:
    for pattern in patterns:
        for process in find_matching_processes(pattern):
            if _is_protected_process(process.command_line):
                continue
            if process.display != display:
                continue

            try:
                os.kill(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass

    if delay_seconds > 0:
        time.sleep(delay_seconds)


def close_matching_display_apps(
    display: str,
    patterns: Iterable[str],
    *,
    delay_seconds: float = 0.0,
) -> None:
    close_display_apps(
        display=display,
        patterns=patterns,
        delay_seconds=delay_seconds,
    )


def _process_display(pid: int) -> str | None:
    try:
        data = Path(f"/proc/{pid}/environ").read_bytes()
    except (OSError, PermissionError):
        return None

    for item in data.split(b"\0"):
        if item.startswith(b"DISPLAY="):
            return item.decode(errors="ignore").split("=", 1)[1]

    return None


def _process_command_line(pid: int) -> str:
    try:
        return (
            Path(f"/proc/{pid}/cmdline")
            .read_bytes()
            .replace(b"\0", b" ")
            .decode(errors="ignore")
        )
    except (OSError, PermissionError):
        return ""


def _is_protected_process(command_line: str) -> bool:
    return any(
        pattern in command_line
        for pattern in PROTECTED_PROCESS_PATTERNS
    )
