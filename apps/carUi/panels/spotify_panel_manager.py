from modules.media.spotify.spotify_auth import SpotifyAuth
from modules.media.spotify.spotify_config import load_spotify_config
from modules.media.spotify.spotify_token_store import SpotifyTokenStore
from modules.media.spotify.spotify_web_api_controller import SpotifyWebApiController

from apps.carUi.panels.spotify_panel import SpotifyPanel


class SpotifyPanelManager:
    def __init__(self, app) -> None:
        self._app = app

        config = load_spotify_config()
        auth = SpotifyAuth(config, SpotifyTokenStore())
        self._controller = SpotifyWebApiController(auth)

        self._panel: SpotifyPanel | None = None

    def show(self) -> None:
        self._app.top_bar.set_title("Spotify")
        self._app.top_bar.set_back_command(self._go_back)
        self._app.top_bar.show_back_button()

        self._clear_content()

        self._panel = SpotifyPanel(
            parent=self._app.content_frame,
            controller=self._controller,
            on_back=self._go_back,
            compact_ui=self._app.compact_ui,
        )
        self._panel.pack(fill="both", expand=True)
        self._panel.start()

        self._app.status_var.set("Spotify remote")

    def _go_back(self) -> None:
        if self._panel is not None:
            self._panel.stop()
            self._panel = None

        self._app.show_media_menu()

    def _clear_content(self) -> None:
        if self._app.content_frame is None:
            return

        for child in self._app.content_frame.winfo_children():
            child.destroy()
