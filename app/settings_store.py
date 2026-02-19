import json
from pathlib import Path

SETTINGS_PATH = Path.home() / "touchui" / "settings.json"

DEFAULTS = {
    "dashboard_refresh_ms": 1000,
    "retention_days": 7,
    "fullscreen": True,
}

def load_settings():
    if SETTINGS_PATH.exists():
        try:
            data = json.loads(SETTINGS_PATH.read_text())
            out = DEFAULTS.copy()
            out.update(data)
            return out
        except Exception:
            return DEFAULTS.copy()
    return DEFAULTS.copy()

def save_settings(data: dict):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(data, indent=2))