from modules.media.spotify.spotify_auth import SpotifyAuth
from modules.media.spotify.spotify_config import load_spotify_config
from modules.media.spotify.spotify_token_store import SpotifyTokenStore


def main() -> None:
    config = load_spotify_config()
    auth = SpotifyAuth(config, SpotifyTokenStore())

    token = auth.get_access_token()
    print("Spotify auth OK")
    print(f"Access token starts with: {token[:12]}...")


if __name__ == "__main__":
    main()
