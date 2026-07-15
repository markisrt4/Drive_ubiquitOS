from __future__ import annotations

from controllers.spotify import SpotifyWebApiController
from protocols.spotify import (
    SpotifyAuth,
    SpotifyTokenStore,
    SpotifyWebApiClient,
    load_spotify_config,
)


def create_spotify_controller() -> SpotifyWebApiController:
    """Assemble the Spotify controller used by the Car UI."""

    config = load_spotify_config()
    token_store = SpotifyTokenStore()
    auth = SpotifyAuth(
        config=config,
        token_store=token_store,
    )
    client = SpotifyWebApiClient(auth)

    return SpotifyWebApiController(client)
