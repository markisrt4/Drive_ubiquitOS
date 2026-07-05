from modules.media.spotify.spotify_auth import SpotifyAuth
from modules.media.spotify.spotify_config import load_spotify_config
from modules.media.spotify.spotify_token_store import SpotifyTokenStore
from modules.media.spotify.spotify_web_api_controller import SpotifyWebApiController


def main() -> None:
    auth = SpotifyAuth(
        config=load_spotify_config(),
        token_store=SpotifyTokenStore(),
    )

    spotify = SpotifyWebApiController(auth)
    state = spotify.current_state()

    print(f"Status: {state.status_message}")
    print(f"Track:  {state.track_name}")
    print(f"Artist: {state.artist_name}")
    print(f"Album:  {state.album_name}")
    print(f"Device: {state.device_name}")
    print(f"Volume: {state.volume_percent}")
    print(f"Playing: {state.is_playing}")


if __name__ == "__main__":
    main()
