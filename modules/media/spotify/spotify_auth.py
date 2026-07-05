import base64
import hashlib
import json
import secrets
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from modules.media.spotify.spotify_config import SpotifyConfig
from modules.media.spotify.spotify_token_store import SpotifyTokenStore, SpotifyTokens


AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = (
    "user-read-playback-state",
    "user-read-currently-playing",
    "user-modify-playback-state",
)


class SpotifyAuthError(RuntimeError):
    pass


class SpotifyAuth:
    def __init__(
        self,
        config: SpotifyConfig,
        token_store: SpotifyTokenStore,
    ) -> None:
        self._config = config
        self._token_store = token_store

    def get_access_token(self) -> str:
        tokens = self._token_store.load()

        if tokens is None:
            tokens = self.login()

        if tokens.is_expired():
            tokens = self.refresh(tokens.refresh_token)

        return tokens.access_token

    def login(self) -> SpotifyTokens:
        verifier = self._make_code_verifier()
        challenge = self._make_code_challenge(verifier)

        callback_result: dict[str, str] = {}

        redirect = urllib.parse.urlparse(self._config.redirect_uri)
        server = HTTPServer(
            (redirect.hostname or "127.0.0.1", redirect.port or 8888),
            self._make_callback_handler(callback_result),
        )

        params = {
            "client_id": self._config.client_id,
            "response_type": "code",
            "redirect_uri": self._config.redirect_uri,
            "scope": " ".join(SCOPES),
            "code_challenge_method": "S256",
            "code_challenge": challenge,
        }

        auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

        print("Opening Spotify authorization URL...")
        print(auth_url)
        webbrowser.open(auth_url)

        server.handle_request()
        server.server_close()

        if "error" in callback_result:
            raise SpotifyAuthError(callback_result["error"])

        code = callback_result.get("code")
        if code is None:
            raise SpotifyAuthError("Spotify callback did not include an authorization code")

        tokens = self._exchange_code_for_tokens(code, verifier)
        self._token_store.save(tokens)
        return tokens

    def refresh(self, refresh_token: str) -> SpotifyTokens:
        body = urllib.parse.urlencode(
            {
                "client_id": self._config.client_id,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            TOKEN_URL,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        new_refresh_token = str(data.get("refresh_token", refresh_token))

        tokens = SpotifyTokens(
            access_token=str(data["access_token"]),
            refresh_token=new_refresh_token,
            expires_at=time.time() + int(data["expires_in"]),
        )

        self._token_store.save(tokens)
        return tokens

    def _exchange_code_for_tokens(self, code: str, verifier: str) -> SpotifyTokens:
        body = urllib.parse.urlencode(
            {
                "client_id": self._config.client_id,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self._config.redirect_uri,
                "code_verifier": verifier,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            TOKEN_URL,
            data=body,
            method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        with urllib.request.urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))

        return SpotifyTokens(
            access_token=str(data["access_token"]),
            refresh_token=str(data["refresh_token"]),
            expires_at=time.time() + int(data["expires_in"]),
        )

    @staticmethod
    def _make_code_verifier() -> str:
        return secrets.token_urlsafe(64)[:128]

    @staticmethod
    def _make_code_challenge(verifier: str) -> str:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    @staticmethod
    def _make_callback_handler(result: dict[str, str]):
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)

                if "error" in params:
                    result["error"] = params["error"][0]
                elif "code" in params:
                    result["code"] = params["code"][0]

                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<html><body><h2>Spotify login complete.</h2>"
                    b"<p>You can close this window.</p></body></html>"
                )

            def log_message(self, format: str, *args) -> None:
                return

        return CallbackHandler
