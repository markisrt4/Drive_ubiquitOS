import json
import urllib.error
import urllib.request

from modules.media.spotify.spotify_auth import SpotifyAuth
from modules.media.spotify.spotify_controller import SpotifyController
from modules.media.spotify.spotify_state import SpotifyState


SPOTIFY_API_BASE = "https://api.spotify.com/v1"


class SpotifyWebApiController(SpotifyController):
    def __init__(self, auth: SpotifyAuth) -> None:
        self._auth = auth
        self._last_state = SpotifyState(
            is_available=False,
            status_message="Spotify not loaded",
        )

    def current_state(self) -> SpotifyState:
        try:
            response = self._request_json("GET", "/me/player")

            if response is None:
                self._last_state = SpotifyState(
                    is_available=False,
                    status_message="No active Spotify playback",
                )
                return self._last_state

            item = response.get("item") or {}
            album = item.get("album") or {}
            artists = item.get("artists") or []
            device = response.get("device") or {}

            artist_name = ", ".join(
                str(artist.get("name"))
                for artist in artists
                if artist.get("name") is not None
            )

            self._last_state = SpotifyState(
                is_available=True,
                is_playing=bool(response.get("is_playing")),
                track_name=item.get("name"),
                artist_name=artist_name or None,
                album_name=album.get("name"),
                device_name=device.get("name"),
                volume_percent=device.get("volume_percent"),
                progress_ms=response.get("progress_ms"),
                duration_ms=item.get("duration_ms"),
                status_message="Playing" if response.get("is_playing") else "Paused",
            )
            return self._last_state

        except Exception as ex:
            self._last_state = SpotifyState(
                is_available=False,
                status_message=f"Spotify error: {ex}",
            )
            return self._last_state

    def play_pause(self) -> None:
        state = self.current_state()

        if state.is_playing:
            self._request_no_content("PUT", "/me/player/pause")
        else:
            self._request_no_content("PUT", "/me/player/play")

    def next_track(self) -> None:
        self._request_no_content("POST", "/me/player/next")

    def previous_track(self) -> None:
        self._request_no_content("POST", "/me/player/previous")

    def set_volume_percent(self, volume_percent: int) -> None:
        clamped = max(0, min(100, volume_percent))
        self._request_no_content(
            "PUT",
            f"/me/player/volume?volume_percent={clamped}",
        )

    def _request_json(self, method: str, path: str) -> dict | None:
        request = self._build_request(method, path)

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 204:
                    return None

                body = response.read().decode("utf-8")
                if not body:
                    return None

                return json.loads(body)

        except urllib.error.HTTPError as ex:
            if ex.code == 204:
                return None

            body = ex.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Spotify HTTP {ex.code}: {body}") from ex

    def _request_no_content(self, method: str, path: str) -> None:
        request = self._build_request(method, path)

        try:
            with urllib.request.urlopen(request, timeout=10):
                return

        except urllib.error.HTTPError as ex:
            body = ex.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Spotify HTTP {ex.code}: {body}") from ex

    def _build_request(self, method: str, path: str) -> urllib.request.Request:
        token = self._auth.get_access_token()

        return urllib.request.Request(
            f"{SPOTIFY_API_BASE}{path}",
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    def seek_to_position_ms(self, position_ms: int) -> None:
        position = max(0, position_ms)
        self._request_no_content(
            "PUT",
            f"/me/player/Sseek?position_ms={position}",
        )