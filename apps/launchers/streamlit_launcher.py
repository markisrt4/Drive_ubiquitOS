import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional

from apps.launchers.app_launcher_if import AppLauncherIf
from apps.launchers.browser_launcher import BrowserKioskLauncher
from apps.launchers.process_manager import (
    is_process_running,
    kill_process_pattern,
)

from modules.logging.logging_paths import app_logging_file


class StreamlitLauncher(AppLauncherIf):
    def __init__(
        self,
        app_path: Path,
        port: int = 8501,
        log_file:         Optional[str] = None,
        browser_log_file: Optional[str] = None,
    ):
        self.app_path = app_path
        self.port     = port

        self.log_file = (
            log_file
            or app_logging_file(
                "carsdr",
                "carsdr-streamlit.log",
            )
        )

        self.browser = BrowserKioskLauncher(
            url=f"http://127.0.0.1:{port}",
            process_pattern=f"127.0.0.1:{port}",
            log_file=(
                browser_log_file
                or app_logging_file(
                    "carsdr",
                    "carsdr-streamlit-browser.log",
                )
            ),
        )

    @property
    def process_pattern(self) -> str:
        return str(self.app_path)

    def is_running(self) -> bool:
        return is_process_running(self.process_pattern)

    def launch(
        self,
        remote_display: str = ":2",
        set_status: Optional[Callable[[str], None]] = None,
    ) -> None:

        if set_status:
            set_status(
                f"Launching Streamlit app: {self.app_path.name}"
            )

        if not self.is_running():

            log_handle = open(self.log_file, "a")

            subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "streamlit",
                    "run",
                    str(self.app_path),
                    "--server.headless",
                    "true",
                    "--server.port",
                    str(self.port),
                    "--browser.gatherUsageStats",
                    "false",
                ],
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )

        self.browser.launch(
            remote_display=remote_display,
            set_status=set_status,
        )

        if set_status:
            set_status(
                f"Streamlit dashboard launched on {remote_display}"
            )

    def stop(
        self,
        remote_display: str = ":2",
        set_status: Optional[Callable[[str], None]] = None,
    ) -> None:

        kill_process_pattern(str(self.app_path))

        self.browser.stop(set_status=None)

        if set_status:
            set_status("Streamlit dashboard stopped")

    def toggle(
        self,
        remote_display: str = ":2",
        set_status: Optional[Callable[[str], None]] = None,
    ) -> bool:

        if self.is_running() or self.browser.is_running():

            self.stop(
                remote_display=remote_display,
                set_status=set_status,
            )

            return False

        self.launch(
            remote_display=remote_display,
            set_status=set_status,
        )

        return True