import json
import time
from dataclasses import dataclass
from pathlib import Path


DEFAULT_TOKEN_PATH = Path.home() / ".config" / "carui" / "spotify_tokens.json"


@dataclass(frozen=True, slots=True)
class SpotifyTokens:
    access_token: str
    refresh_token: str
    expires_at: float

    def is_expired(self, buffer_seconds: int = 60) -> bool:
        return time.time() >= self.expires_at - buffer_seconds


class SpotifyTokenStore:
    def __init__(self, path: Path = DEFAULT_TOKEN_PATH) -> None:
        self._path = path

    def load(self) -> SpotifyTokens | None:
        if not self._path.exists():
            return None

        with self._path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return SpotifyTokens(
            access_token=str(data["access_token"]),
            refresh_token=str(data["refresh_token"]),
            expires_at=float(data["expires_at"]),
        )

    def save(self, tokens: SpotifyTokens) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "expires_at": tokens.expires_at,
        }

        with self._path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
