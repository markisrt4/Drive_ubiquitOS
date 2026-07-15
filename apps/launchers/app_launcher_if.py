from __future__ import annotations

from collections.abc import Callable
from typing import Protocol, TypeAlias, runtime_checkable


StatusCallback: TypeAlias = Callable[[str], None] | None


@runtime_checkable
class AppLauncherIf(Protocol):
    """Thread-compatible interface for launching external applications."""

    def launch(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> None: ...

    def stop(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> None: ...

    def toggle(
        self,
        remote_display: str,
        set_status: StatusCallback = None,
    ) -> bool: ...

    def is_running(self) -> bool: ...
