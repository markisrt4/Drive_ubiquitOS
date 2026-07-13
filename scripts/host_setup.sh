#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$PWD}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/venv}"

DISPLAY_NUM="${DISPLAY_NUM:-2}"
GEOMETRY="${GEOMETRY:-1280x720}"
DEPTH="${DEPTH:-24}"
GPS_DEVICE="${GPS_DEVICE:-/dev/ttyACM0}"

RUNTIME_SCRIPT="$PROJECT_DIR/scripts/start_vnc_server.sh"

install_if_available() {
  local pkg="$1"

  if apt-cache show "$pkg" >/dev/null 2>&1; then
    echo "[*] Installing: $pkg"
    sudo apt install -y "$pkg"
  else
    echo "[!] Package not available, skipping: $pkg"
  fi
}

install_first_available() {
  local label="$1"
  shift

  for pkg in "$@"; do
    if apt-cache show "$pkg" >/dev/null 2>&1; then
      echo "[*] Installing $label: $pkg"
      sudo apt install -y "$pkg"
      return 0
    fi
  done

  echo "[!] No available package found for: $label"
  echo "    Tried: $*"
  return 1
}

echo "[*] Updating apt..."
sudo apt update

echo "[*] Installing base packages..."
for pkg in \
  git curl wget ca-certificates \
  lighttpd \
  bluez \
  python3 python3-venv python3-tk python3-pip \
  dbus-x11 xterm x11-apps wmctrl \
  openbox \
  xfce4 xfce4-goodies \
  tigervnc-standalone-server tigervnc-common \
  rtl-sdr \
  gpsd gpsd-clients python3-gps \
  i2c-tools
do
  install_if_available "$pkg"
done

echo "[*] Installing Chromium..."
install_first_available "Chromium browser" \
  chromium \
  chromium-browser

echo "[*] Installing SDR++ if available..."
install_if_available sdrpp

echo "[*] Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "[*] Installing Python packages..."
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip wheel setuptools
python -m pip install \
  streamlit \
  requests \
  geocoder \
  streamlit-autorefresh \
  gps \
  gpsd-py3 \
  pyserial \
  bleak \
  endev \
  RPi.GPIO \
  adafruit-blinka \
  adafruit-circuitpython-seesaw \
  Pillow

deactivate

echo "[*] Granting user permissions..."
sudo usermod -aG input   "$USER"
sudo usermod -aG dialout "$USER"


echo "[*] Setting up VNC..."

mkdir -p "$HOME/.vnc"
mkdir -p "$PROJECT_DIR/scripts"

if [[ ! -f "$HOME/.vnc/passwd" ]]; then
  echo "[*] Setting VNC password..."
  vncpasswd
else
  echo "[*] Existing VNC password found."
fi

echo "[*] Writing ~/.vnc/xstartup..."

cat > "$HOME/.vnc/xstartup" <<'EOF'
#!/bin/sh

unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
unset WAYLAND_DISPLAY

export XDG_SESSION_TYPE=x11
export GDK_BACKEND=x11

xsetroot -solid "#1e1e1e" 2>/dev/null || true

xterm -geometry 100x30+20+20 &

exec /usr/bin/openbox
EOF

chmod +x "$HOME/.vnc/xstartup"

echo "[*] Installing VNC runtime script..."
chmod +x "$RUNTIME_SCRIPT"

echo "[*] Installing VNC systemd service..."
bash "$PROJECT_DIR/scripts/systemd/install_vnc_systemd.sh"

echo "[*] Installing GPS systemd service..."
sudo bash "$PROJECT_DIR/scripts/systemd/install_gpsd_systemd.sh" "$GPS_DEVICE"

echo
echo "[+] Host setup complete."
echo "    Project dir: $PROJECT_DIR"
echo "    Venv:        $VENV_DIR"
echo "    VNC display: :$DISPLAY_NUM"
echo "    VNC port:    $((5900 + DISPLAY_NUM))"
echo
echo "[*] Activate Python venv with:"
echo "    source \"$VENV_DIR/bin/activate\""
echo
echo "[*] VNC service commands:"
echo "    systemctl --user status carui-vnc.service"
echo "    systemctl --user restart carui-vnc.service"
echo "    journalctl --user -u carui-vnc.service -f"
