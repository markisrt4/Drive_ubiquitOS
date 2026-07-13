from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from protocols.oauth import OAuthClientConfig


DEFAULT_CONFIG_PATH = (
    Path.home()
    / ".config"
    / "spotify"
    / "config.json"
)

DEFAULT_REDIRECT_URI = "http://127.0.0.1:8888/callback"

SPOTIFY_AUTHORIZATION_URL = (
    "https://accounts.spotify.com/authorize"
)

SPOTIFY_TOKEN_URL = (
    "https://accounts.spotify.com/api/token"
)

SPOTIFY_SCOPES = (
    "user-read-playback-state",
    "user-read-currently-playing",
    "user-modify-playback-state",
)


@dataclass(frozen=True, slots=True)
class SpotifyConfig:
    """
    Spotify OAuth and API configuration.
    """

    client_id: str
    redirect_uri: str = DEFAULT_REDIRECT_URI

    def __post_init__(self) -> None:
        if not self.client_id:
            raise ValueError("client_id cannot be empty")

        if not self.redirect_uri:
            raise ValueError("redirect_uri cannot be empty")

    def create_oauth_config(self) -> OAuthClientConfig:
        """
        Create the generic OAuth configuration used by Spotify.
        """
        return OAuthClientConfig(
            client_id=self.client_id,
            authorization_url=SPOTIFY_AUTHORIZATION_URL,
            token_url=SPOTIFY_TOKEN_URL,
            redirect_uri=self.redirect_uri,
            scopes=SPOTIFY_SCOPES,
        )


def load_spotify_config(
    path: Path = DEFAULT_CONFIG_PATH,
) -> SpotifyConfig:
    """
    Load Spotify configuration from a JSON file.
    """
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return SpotifyConfig(
        client_id=str(data["client_id"]),
        redirect_uri=str(
            data.get(
                "redirect_uri",
                DEFAULT_REDIRECT_URI,
            )
        ),
    )
