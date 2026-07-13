#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from protocols.spotify import (
    DEFAULT_CONFIG_PATH,
    DEFAULT_TOKEN_PATH,
    SpotifyAuth,
    SpotifyTokenStore,
    load_spotify_config,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Spotify OAuth component test"
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the Spotify configuration file",
    )

    parser.add_argument(
        "--tokens",
        type=Path,
        default=DEFAULT_TOKEN_PATH,
        help="Path to the Spotify token file",
    )

    parser.add_argument(
        "--clear-tokens",
        action="store_true",
        help="Delete stored tokens before authenticating",
    )

    parser.add_argument(
        "--callback-timeout",
        type=float,
        default=120.0,
        help="OAuth callback timeout in seconds",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = load_spotify_config(args.config)

    token_store = SpotifyTokenStore(
        path=args.tokens
    )

    if args.clear_tokens:
        token_store.clear()
        print("Stored Spotify tokens cleared.")

    auth = SpotifyAuth(
        config=config,
        token_store=token_store,
        callback_timeout_seconds=(
            args.callback_timeout
        ),
    )

    token = auth.get_access_token()

    print("Spotify authentication succeeded.")
    print(f"Token file: {token_store.path}")
    print(
        "Access token prefix: "
        f"{token[:12]}..."
    )


if __name__ == "__main__":
    main()
