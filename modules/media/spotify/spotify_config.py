import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_CONFIG_PATH = Path.home() / ".config" / "carui" / "spotify_config.json"


@dataclass(frozen=True, slots=True)
class SpotifyConfig:
    client_id: str
    redirect_uri: str = "http://127.0.0.1:8888/callback"


def load_spotify_config(path: Path = DEFAULT_CONFIG_PATH) -> SpotifyConfig:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    client_id = str(data["client_id"])
    redirect_uri = str(data.get("redirect_uri", "http://127.0.0.1:8888/callback"))

    return SpotifyConfig(client_id=client_id, redirect_uri=redirect_uri)
