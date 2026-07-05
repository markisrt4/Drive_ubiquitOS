import time

from modules.media.spotify.mock_spotify_controller import MockSpotifyController


def main() -> None:
    spotify = MockSpotifyController()

    for index in range(10):
        state = spotify.current_state()

        print(
            f"{state.status_message} | "
            f"{state.track_name} - {state.artist_name} | "
            f"{state.progress_percent:.1f}% | "
            f"Volume={state.volume_percent}%"
        )

        if index == 3:
            spotify.next_track()

        if index == 6:
            spotify.play_pause()

        time.sleep(1)


if __name__ == "__main__":
    main()
