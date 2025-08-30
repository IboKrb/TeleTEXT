# systems/config.py
from pathlib import Path

# Dieses File liegt in: <root>/src/systems/config.py
_THIS = Path(__file__).resolve()
PROJECT_ROOT = _THIS.parents[2]          # <- zwei Ebenen hoch: .../src/systems -> .../src -> .../<root>

SRC_DIR    = PROJECT_ROOT / "src"
ASSETS_DIR = PROJECT_ROOT / "assets"
AUDIO_DIR  = ASSETS_DIR / "Audio"
ROOMS_DIR  = ASSETS_DIR / "Rooms"
PEOPLE_DIR = ASSETS_DIR / "People"

# Fenster
FULLSCREEN  = True
WINDOW_SIZE = (1280, 720)

TITLE_TEXT      = "TeleTEXT - Ein Team Adventure"
ROOM_AREA_MARGIN = (20, 20, 360, 200)
