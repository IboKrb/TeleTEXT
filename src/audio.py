# audio.py
import os
import pygame
from typing import Dict, Optional, Callable

try:
    from systems.config import AUDIO_DIR as CFG_AUDIO_DIR  # Path oder str
    AUDIO_DIR = str(CFG_AUDIO_DIR)  # in String wandeln, falls Path
except Exception:
    # Fallback: von src/audio.py zwei Ebenen hoch zu <root>/assets/Audio
    AUDIO_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets", "Audio"))

# Standard-Audioordner relativ zu diesem File:
AUDIO_DIR = os.path.join(os.path.dirname(__file__), "./assets/Audio")

def _clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, int(v)))

class Audio:
    """
    Einfacher Audio-Manager:
      - MP3/OGG/WAV mit Fallback
      - Musik: play_menu_music(), play_game_music(), fade_to(...)
      - Lautstärke 0–10 (set_music_volume_0_10, set_sfx_volume_0_10)
      - SFX-Stub (play_sfx / load_sfx)
    """
    def __init__(
        self,
        audio_dir: Optional[str] = None,
        menu_track: str = "menu",
        game_track: str = "game",
        default_music_volume: int = 5,  # 0..10
        default_sfx_volume: int = 5,    # 0..10
        logger: Optional[Callable[[str], None]] = None,
    ):
        self.audio_dir = audio_dir or AUDIO_DIR
        self.logger = logger or (lambda msg: None)

        # Mixer robust initialisieren
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.mixer.get_init():
                # solide Defaults für MP3
                pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
            # genug Kanäle für SFX
            if pygame.mixer.get_num_channels() < 16:
                pygame.mixer.set_num_channels(16)
        except Exception as e:
            self.logger(f"[Audio] Mixer konnte nicht initialisiert werden: {e}")

        self.music_volume = _clamp(default_music_volume, 0, 10)
        self.sfx_volume   = _clamp(default_sfx_volume, 0, 10)

        # bekannte Tracks
        self.tracks: Dict[str, Optional[str]] = {
            "menu": self._resolve(menu_track),
            "game": self._resolve(game_track),
        }

        # SFX-Speicher
        self._sfx: Dict[str, pygame.mixer.Sound] = {}

        # Anfangslautstärken anwenden
        try:
            pygame.mixer.music.set_volume(self.music_volume / 10.0)
        except Exception:
            pass

    # ---------- Pfad-Helfer ----------
    def _resolve(self, name_or_path: str) -> Optional[str]:
        """Nimmt Basename oder Pfad und findet eine existierende Datei (.mp3, .ogg, .wav)."""
        candidates = []
        if os.path.isabs(name_or_path) or os.path.splitext(name_or_path)[1]:
            base, ext = os.path.splitext(name_or_path)
            if ext:
                candidates = [name_or_path]
            else:
                candidates = [base + ".mp3", base + ".ogg", base + ".wav"]
        else:
            base = os.path.join(self.audio_dir, name_or_path)
            base_no_ext, ext = os.path.splitext(base)
            if ext:
                candidates = [base]
            else:
                candidates = [base_no_ext + ".mp3", base_no_ext + ".ogg", base_no_ext + ".wav"]

        for c in candidates:
            if os.path.exists(c):
                return c
        self.logger(f"[Audio] Datei nicht gefunden: {name_or_path}")
        return None

    # ---------- Musik ----------
    def play_music(self, name_or_path: str, loop: bool = True, fade_ms: int = 400, start: float = 0.0):
        path = self._resolve(name_or_path)
        if not path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume / 10.0)
            pygame.mixer.music.play(-1 if loop else 0, start, fade_ms=fade_ms)
            self.logger(f"[Audio] Musik: {os.path.basename(path)}")
        except Exception as e:
            self.logger(f"[Audio] Fehler beim Abspielen: {e}")

    def fade_to(self, name_or_path: str, cross_ms: int = 600):
        """Einfaches Crossfade: aktuelle Musik ausfaden, dann neue mit Fade-in starten."""
        try:
            pygame.mixer.music.fadeout(cross_ms)
        except Exception:
            pass
        self.play_music(name_or_path, loop=True, fade_ms=cross_ms)

    def stop_music(self, fade_ms: int = 400):
        try:
            pygame.mixer.music.fadeout(fade_ms)
        except Exception:
            pass

    def pause_music(self):
        try:
            pygame.mixer.music.pause()
        except Exception:
            pass

    def resume_music(self):
        try:
            pygame.mixer.music.unpause()
        except Exception:
            pass

    def set_music_volume_0_10(self, v: int):
        self.music_volume = _clamp(v, 0, 10)
        try:
            pygame.mixer.music.set_volume(self.music_volume / 10.0)
        except Exception:
            pass

    def get_music_volume_0_10(self) -> int:
        return self.music_volume

    # Komfort:
    def play_menu_music(self):
        if self.tracks["menu"]:
            self.fade_to(self.tracks["menu"])
    def play_game_music(self):
        if self.tracks["game"]:
            self.fade_to(self.tracks["game"])

    # ---------- SFX (einfacher Stub) ----------
    def load_sfx(self, name: str, file_or_basename: str):
        path = self._resolve(file_or_basename)
        if not path:
            return
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume / 10.0)
            self._sfx[name] = snd
        except Exception as e:
            self.logger(f"[Audio] SFX-Load-Fehler {file_or_basename}: {e}")

    def play_sfx(self, name: str):
        snd = self._sfx.get(name)
        if snd:
            try:
                ch = pygame.mixer.find_channel()
                if ch is None:
                    ch = pygame.mixer.Channel(0)
                ch.set_volume(self.sfx_volume / 10.0)
                ch.play(snd)
            except Exception:
                pass

    def set_sfx_volume_0_10(self, v: int):
        self.sfx_volume = _clamp(v, 0, 10)
        # bestehende Sounds bekommen neue Lautstärke, wenn sie das nächste Mal abgespielt werden
