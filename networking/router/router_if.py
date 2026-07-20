"""Router control interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .router_status import RouterStatus


class RouterIf(ABC):
    """Interface implemented by router management backends."""

    @abstractmethod
    def start_router(self) -> None:
        """Start the router connection."""

    @abstractmethod
    def stop_router(self) -> None:
        """Stop the router connection."""

    @abstractmethod
    def restart_router(self) -> None:
        """Restart the router connection."""

    @abstractmethod
    def get_status(self) -> RouterStatus:
        """Return the current router status."""

    def is_running(self) -> bool:
        """Return whether the router connection is active."""

        return self.get_status().running
