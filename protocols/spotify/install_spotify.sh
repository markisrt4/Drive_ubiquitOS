#!/usr/bin/env bash

set -euo pipefail

CONFIG_DIR="${HOME}/.config/spotify"
CONFIG_FILE="${CONFIG_DIR}/config.json"
TOKEN_FILE="${CONFIG_DIR}/tokens.json"

DEFAULT_REDIRECT_URI="http://127.0.0.1:8888/callback"
AUTH_MODULE="protocols.spotify.component_test.spotify_auth_cli"


print_header() {
    echo
    echo "Spotify Setup"
    echo "============="
    echo
}


require_command() {
    local command_name="$1"

    if ! command -v "${command_name}" >/dev/null 2>&1; then
        echo "Error: required command not found: ${command_name}" >&2
        exit 1
    fi
}


find_project_root() {
    local current_dir

    current_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

    while [[ "${current_dir}" != "/" ]]; do
        if [[ -d "${current_dir}/protocols/spotify" ]]; then
            printf '%s\n' "${current_dir}"
            return 0
        fi

        current_dir="$(dirname "${current_dir}")"
    done

    return 1
}


prompt_client_id() {
    local client_id

    while true; do
        read -r -p "Spotify Client ID: " client_id

        client_id="${client_id//[[:space:]]/}"

        if [[ -n "${client_id}" ]]; then
            printf '%s\n' "${client_id}"
            return
        fi

        echo "The Spotify Client ID cannot be empty."
    done
}


prompt_redirect_uri() {
    local redirect_uri

    read -r -p \
        "Redirect URI [${DEFAULT_REDIRECT_URI}]: " \
        redirect_uri

    if [[ -z "${redirect_uri}" ]]; then
        redirect_uri="${DEFAULT_REDIRECT_URI}"
    fi

    printf '%s\n' "${redirect_uri}"
}


create_config() {
    local client_id="$1"
    local redirect_uri="$2"

    mkdir -p "${CONFIG_DIR}"
    chmod 700 "${CONFIG_DIR}"

    CLIENT_ID="${client_id}" \
    REDIRECT_URI="${redirect_uri}" \
    CONFIG_FILE="${CONFIG_FILE}" \
    python3 <<'PYTHON'
import json
import os
from pathlib import Path

config_file = Path(os.environ["CONFIG_FILE"])

config = {
    "client_id": os.environ["CLIENT_ID"],
    "redirect_uri": os.environ["REDIRECT_URI"],
}

with config_file.open("w", encoding="utf-8") as file:
    json.dump(config, file, indent=2)
    file.write("\n")
PYTHON

    chmod 600 "${CONFIG_FILE}"
}


run_authentication() {
    local project_root="$1"

    echo
    echo "Starting Spotify authorization..."
    echo

    cd "${project_root}"

    python3 -m "${AUTH_MODULE}" \
        --config "${CONFIG_FILE}" \
        --tokens "${TOKEN_FILE}"
}


main() {
    local project_root
    local client_id
    local redirect_uri

    print_header

    require_command python3

    if ! project_root="$(find_project_root)"; then
        echo "Error: unable to locate the project root." >&2
        echo "Expected to find protocols/spotify in a parent directory." >&2
        exit 1
    fi

    echo "Before continuing:"
    echo
    echo "1. Create an application in the Spotify Developer Dashboard."
    echo "2. Add this redirect URI to the application:"
    echo
    echo "   ${DEFAULT_REDIRECT_URI}"
    echo
    echo "3. Copy the application's Client ID."
    echo

    client_id="$(prompt_client_id)"
    redirect_uri="$(prompt_redirect_uri)"

    if [[ -f "${CONFIG_FILE}" ]]; then
        echo
        read -r -p \
            "A Spotify configuration already exists. Replace it? [y/N]: " \
            replace_config

        case "${replace_config}" in
            y|Y|yes|YES)
                ;;
            *)
                echo "Spotify setup cancelled."
                exit 0
                ;;
        esac
    fi

    create_config "${client_id}" "${redirect_uri}"

    echo
    echo "Configuration created:"
    echo "  ${CONFIG_FILE}"

    run_authentication "${project_root}"

    echo
    echo "Spotify setup complete."
    echo
    echo "Configuration:"
    echo "  ${CONFIG_FILE}"
    echo
    echo "Tokens:"
    echo "  ${TOKEN_FILE}"
}


main "$@"
