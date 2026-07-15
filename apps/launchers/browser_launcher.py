from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from apps.launchers.app_launcher_if import (
    AppLauncherIf,
    StatusCallback,
)
from apps.launchers.process_manager import (
    close_matching_display_apps,
    is_process_running,
    terminate_process,
)
from common.logging.logging_paths import logging_file_path


class BrowserKioskLauncher(AppLauncherIf):
    """Launch a browser in kiosk mode on a selected X display."""

    def __init__(
        self,
        *,
        url: str,
        process_pattern: str | None = None,
        log_file: str | Path | None = None,
        browser_candidates: tuple[str, ...] = (
            "chromium-browser",
            "chromium",
            "google-chrome",
        ),
    ) -> None:
        self.url = url
        self.process_pattern = process_pattern or url
        self.log_file = Path(
            log_file
            or logging_file_path(
                "drive-ubiquitos",
                "browser.log",
            )
        )
        self.browser_candidates = browser_candidates
        self._process: subprocess.Popen[str] | None = None

    def is_running(self) -> bool:
        if self._process is not None:
            if self._process.poll() is None:
                return True
            self._process = None

        return is_process_running(self.process_pattern)

    def launch(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> None:
        if self.is_running():
            _status(set_status, "Browser already running")
            return

        browser_path = self._find_browser()
        environment = _x11_environment(remote_display)
        command = [
            browser_path,
            "--kiosk",
            "--noerrdialogs",
            "--disable-infobars",
            "--disable-session-crashed-bubble",
            "--disable-restore-session-state",
            self.url,
        ]

        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        log_handle = self.log_file.open("a", encoding="utf-8")
        try:
            self._process = subprocess.Popen(
                command,
                env=environment,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                text=True,
            )
        finally:
            log_handle.close()

        _status(set_status, f"Browser launched on {remote_display}")

    def stop(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> None:
        if self._process is not None:
            terminate_process(self._process)
            self._process = None

        close_matching_display_apps(
            display=remote_display,
            patterns=(self.process_pattern,),
        )
        _status(set_status, "Browser stopped")

    def toggle(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> bool:
        if self.is_running():
            self.stop(remote_display, set_status)
            return False

        self.launch(remote_display, set_status)
        return True

    def _find_browser(self) -> str:
        for candidate in self.browser_candidates:
            browser = shutil.which(candidate)
            if browser:
                return browser

        names = ", ".join(self.browser_candidates)
        raise RuntimeError(
            f"No supported browser found in PATH. Tried: {names}"
        )


def _x11_environment(display: str) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(
        {
            "DISPLAY": display,
            "XDG_SESSION_TYPE": "x11",
            "GDK_BACKEND": "x11",
        }
    )
    return environment


def _status(callback: StatusCallback, message: str) -> None:
    if callback is not None:
        callback(message)
