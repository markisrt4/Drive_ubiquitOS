# Application Launchers

The `apps.launchers` package starts, stops, and monitors external applications
used by higher-level UIs.

## Responsibilities

Launchers may:

- start an owned subprocess;
- set the X11 display environment;
- wait for an external service to become ready;
- open a browser kiosk;
- stop owned subprocesses;
- perform display-scoped fallback cleanup.

Launchers must not contain panel or Tk widget logic.

## Interface

Every launcher implements:

```python
launch(remote_display, set_status=None)
stop(remote_display, set_status=None)
toggle(remote_display, set_status=None) -> bool
is_running() -> bool
```

`toggle()` returns `True` when the application is running after the operation
and `False` when it has been stopped.

## Implementations

- `BrowserKioskLauncher`: Chromium or Chrome kiosk window.
- `StreamlitLauncher`: Streamlit server plus kiosk browser.
- `WeatherDashLauncher`: configured Streamlit launcher for
  `apps/weatherDash/main.py`.
- `SDRPPLauncher`: SDR++ plus RigCTL readiness checking.
- `ADSBLauncher`: readsb service plus tar1090 kiosk browser.
- `AppLauncherStub`: deterministic test implementation.

## Process ownership

A launcher first terminates the exact subprocess it created. A display-scoped
pattern search is used only as fallback cleanup for processes that survived a
previous application run.

Avoid global `pkill -f` cleanup because it can terminate unrelated user
processes.

## Runtime dependencies

Browser kiosk support requires one of:

```text
chromium-browser
chromium
google-chrome
```

SDR++ fullscreen requests require:

```text
wmctrl
```

Streamlit launchers require the Python package:

```bash
python3 -m pip install streamlit
```

ADS-B launch requires a systemd-managed `readsb` service and a reachable
tar1090 installation.

## Testing

Use `AppLauncherStub` when launcher behavior itself is irrelevant to a
consumer test.

Process launchers should be tested with mocked `subprocess`, `shutil.which`,
and socket calls rather than starting real desktop applications in unit tests.
