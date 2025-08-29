# pygame_game.py
import os
import pygame
from typing import List, Tuple, Optional

# Import Setup (nur Datenaufbau), plus eure Modelle
from setup import Setup
from person import Person
from aufgabe import Aufgabe
from raum import Raum

################################################################################
# Einfache UI-Helper
################################################################################

pygame.init()
pygame.font.init()

FONT = pygame.font.SysFont("arial", 20)
FONT_SMALL = pygame.font.SysFont("arial", 16)
FONT_BIG = pygame.font.SysFont("arial", 28)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (25, 35, 60)
ACCENT = (240, 240, 120)
MAGENTA = (225, 0, 117)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback,
                 tooltip: Optional[str] = None,
                 font: Optional[pygame.font.Font] = None):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.tooltip = tooltip
        self.hover = False
        self.font = font or FONT

    def draw(self, surface: pygame.Surface):
        color = LIGHT_GRAY if self.hover else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        text_surf = self.font.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and callable(self.callback):
                self.callback()

class Slider:
    def __init__(self, rect: pygame.Rect, min_val=0, max_val=10, value=5, on_change=None):
        self.rect = rect
        self.min_val = min_val
        self.max_val = max_val
        self.value = int(value)
        self.on_change = on_change
        self.dragging = False
        self.pad = 12  # Innenabstand für die Schiene

    def _val_to_x(self):
        track_w = self.rect.width - 2 * self.pad
        ratio = (self.value - self.min_val) / max(1, (self.max_val - self.min_val))
        return int(self.rect.x + self.pad + ratio * track_w)

    def _x_to_val(self, x):
        track_w = self.rect.width - 2 * self.pad
        ratio = (x - (self.rect.x + self.pad)) / max(1, track_w)
        v = self.min_val + ratio * (self.max_val - self.min_val)
        v = int(round(max(self.min_val, min(self.max_val, v))))
        return v

    def set_value(self, v):
        v = int(max(self.min_val, min(self.max_val, v)))
        if v != self.value:
            self.value = v
            if callable(self.on_change):
                self.on_change(self.value)

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.set_value(self._x_to_val(event.pos[0]))
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_value(self._x_to_val(event.pos[0]))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

    def draw(self, surface: pygame.Surface):
        # Hintergrund
        pygame.draw.rect(surface, (245, 245, 245), self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        # Schiene
        y = self.rect.centery
        x1 = self.rect.x + self.pad
        x2 = self.rect.right - self.pad
        pygame.draw.line(surface, GRAY, (x1, y), (x2, y), 4)

        # Knopf
        knob_x = self._val_to_x()
        knob_rect = pygame.Rect(0, 0, 18, 26)
        knob_rect.center = (knob_x, y)
        pygame.draw.rect(surface, LIGHT_GRAY, knob_rect, border_radius=6)
        pygame.draw.rect(surface, BLACK, knob_rect, 2, border_radius=6)

        # Wert (kleine Zahl rechts)
        val_surf = FONT_SMALL.render(str(self.value), True, BLACK)
        surface.blit(val_surf, (self.rect.right + 8, self.rect.centery - val_surf.get_height() // 2))

class Panel:
    def __init__(self, rect: pygame.Rect, title: str = ""):
        self.rect = rect
        self.title = title

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (235, 235, 240), self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        if self.title:
            title_surf = FONT_BIG.render(self.title, True, BLACK)
            surface.blit(title_surf, (self.rect.x + 12, self.rect.y + 8))

    def content_rect(self, pad: int = 12) -> pygame.Rect:
        title_h = (FONT_BIG.get_height() + 12) if self.title else 0
        return pygame.Rect(
            self.rect.x + pad,
            self.rect.y + pad + title_h,
            self.rect.width - 2*pad,
            self.rect.height - 2*pad - title_h
        )

class TextLog:
    """Scrollbarer Text-Log mit anpassbarem Rahmen."""
    def __init__(
        self,
        rect: pygame.Rect,
        max_lines: int = 10,
        title: str = "Log",
        bg_color: Tuple[int,int,int] = (245, 245, 250),
        border_color: Tuple[int,int,int] = (0, 0, 0),
        border_width: int = 2,
        radius: int = 12,
        text_color: Tuple[int,int,int] = (0, 0, 0),
        pad: int = 10,
        title_color: Tuple[int,int,int] = (0, 0, 0)
    ):
        self.rect = rect
        self.lines: List[str] = []
        self.max_lines = max_lines
        self.scroll_offset = 0
        self.title = title
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width
        self.radius = radius
        self.text_color = text_color
        self.pad = pad
        self.title_color = title_color

    def add(self, line: str):
        # Einfache Zeilenumbrüche
        max_chars = 80
        while len(line) > max_chars:
            self.lines.append(line[:max_chars])
            line = line[max_chars:]
        self.lines.append(line)
        if len(self.lines) > 1000:
            self.lines = self.lines[-1000:]

        # Beim neuen Eintrag automatisch ans Ende scrollen
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL:
            # Nach oben: y > 0 => ältere Zeilen sichtbar machen
            self.scroll_offset -= event.y
            self.scroll_offset = max(0, min(self.scroll_offset, max(0, len(self.lines) - self.max_lines)))

    def draw(self, surface: pygame.Surface):
        # Hintergrund + Rahmen
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, self.border_color, self.rect, self.border_width, border_radius=self.radius)

        x = self.rect.x + self.pad
        y = self.rect.y + self.pad

        # Optionaler Titel oben links
        if self.title:
            title_surf = FONT_SMALL.render(self.title, True, self.title_color)
            surface.blit(title_surf, (x, y))
            y += title_surf.get_height() + 6

        # Sichtbaren Bereich bestimmen (mit Scroll)
        start = max(0, len(self.lines) - self.max_lines - self.scroll_offset)
        end = start + self.max_lines
        visible = self.lines[start:end]

        for line in visible:
            ts = FONT_SMALL.render(line, True, self.text_color)
            surface.blit(ts, (x, y))
            y += ts.get_height() + 4

################################################################################
# Pygame-Frontend, das die bestehende Spiel-Logik nutzt
################################################################################

# Räume-Hintergründe (z. B. ../assets/Rooms/flur.png)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets/Rooms")

# Audio
AUDIO_DIR  = os.path.join(os.path.dirname(__file__), "../assets/Audio")
MENU_MUSIC = os.path.join(AUDIO_DIR, "menu.mp3")
GAME_MUSIC = os.path.join(AUDIO_DIR, "game.mp3")

# Mixer sicher starten
try:
    pygame.mixer.init()
except Exception as e:
    print("[Audio] Mixer konnte nicht initialisiert werden:", e)
################################################################################
# Personen-Portraits laden
################################################################################


ASSETS_ROOTS = [
    os.path.join(os.path.dirname(__file__), "../assets"),
]

def find_happy_portrait_paths() -> List[str]:
    """Findet je Person (Ordner) ein Bild, dessen Dateiname 'happy' enthält."""
    exts = (".png", ".jpg", ".jpeg", ".webp")
    paths = []
    for root in ASSETS_ROOTS:
        people_dir = os.path.join(root, "People")
        if not os.path.isdir(people_dir):
            continue
        for dirpath, _, filenames in os.walk(people_dir):
            for fn in filenames:
                if "happy" in fn.lower() and fn.lower().endswith(exts):
                    paths.append(os.path.join(dirpath, fn))
    # pro Personen-Ordner nur das erste Happy nehmen
    by_person = {}
    for p in paths:
        person_folder = os.path.basename(os.path.dirname(p))
        by_person.setdefault(person_folder, p)
    return list(by_person.values())

def scale_surface_to_height(img: pygame.Surface, target_h: int) -> pygame.Surface:
    w, h = img.get_width(), img.get_height()
    if h <= 0:
        return img
    s = target_h / h
    return pygame.transform.smoothscale(img, (max(1, int(w * s)), max(1, int(h * s))))

def load_happy_images(max_height: int) -> List[pygame.Surface]:
    """Lädt alle Happy-Portraits und skaliert sie auf eine Zielhöhe."""
    imgs = []
    for path in find_happy_portrait_paths():
        try:
            img = pygame.image.load(path).convert_alpha()
            imgs.append(scale_surface_to_height(img, max_height))
        except Exception:
            continue
    return imgs

def load_person_portrait(person_name: str, target_size: Tuple[int, int]) -> Optional[pygame.Surface]:
    folder_name = person_name
    basefile = person_name[:1].lower() + person_name[1:] + "Neutral"
    candidates = []
    for root in ASSETS_ROOTS:
        base_dir = os.path.join(root, "People", folder_name)
        for ext in (".png", ".jpg", ".jpeg", ".webp"):
            candidates.append(os.path.join(base_dir, basefile + ext))
    for path in candidates:
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                img = scale_to_fit(img, target_size)
                return img
            except Exception:
                continue
    return None

def scale_to_fit(surface: pygame.Surface, target: Tuple[int, int]) -> pygame.Surface:
    tw, th = target
    sw, sh = surface.get_width(), surface.get_height()
    if sw == 0 or sh == 0:
        return pygame.transform.smoothscale(surface, target)
    scale = min(tw / sw, th / sh)
    nw, nh = max(1, int(sw * scale)), max(1, int(sh * scale))
    return pygame.transform.smoothscale(surface, (nw, nh))

def load_room_background(raum: Raum, target_size: Tuple[int, int]) -> pygame.Surface:
    filename = f"{raum.name.lower().replace(' ', '_')}.png"
    path = os.path.join(ASSETS_DIR, filename)
    surf = pygame.Surface(target_size)
    if os.path.exists(path):
        try:
            img = pygame.image.load(path).convert()
            img = pygame.transform.smoothscale(img, target_size)
            return img
        except Exception:
            pass
    surf.fill(DARK_BLUE)
    title = FONT_BIG.render(raum.name, True, ACCENT)
    surf.blit(title, title.get_rect(center=(target_size[0] // 2, 30)))
    return surf

def preload_room_backgrounds(raeume, target_size):
    """Einmalig beim Start alle Raum-Hintergründe laden & skalieren."""
    cache = {}
    for raum in raeume.values():
        filename = f"{raum.name.lower().replace(' ', '_')}.png"
        path = os.path.join(ASSETS_DIR, filename)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                img = pygame.transform.smoothscale(img, target_size)
                cache[raum.name] = img
            except Exception:
                surf = pygame.Surface(target_size)
                surf.fill(DARK_BLUE)
                title = FONT_BIG.render(raum.name, True, ACCENT)
                surf.blit(title, title.get_rect(center=(target_size[0] // 2, 30)))
                cache[raum.name] = surf
        else:
            surf = pygame.Surface(target_size)
            surf.fill(DARK_BLUE)
            title = FONT_BIG.render(raum.name, True, ACCENT)
            surf.blit(title, title.get_rect(center=(target_size[0] // 2, 30)))
            cache[raum.name] = surf
    return cache

class GameApp:

    def draw_menu_overlay(self):
        if not self.menu_open or self.menu_rect is None:
            return

        # Halbtransparentes Overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        # Popup (weiß, abgerundete Ecken)
        pygame.draw.rect(self.screen, WHITE, self.menu_rect, border_radius=20)
        pygame.draw.rect(self.screen, BLACK, self.menu_rect, 3, border_radius=20)

        # Titel "Menü" oben
        title = FONT_BIG.render("Menü", True, BLACK)
        self.screen.blit(title, title.get_rect(midtop=(self.menu_rect.centerx, self.menu_rect.y + 14)))

        # Labels (links ausgerichtet, Y aus build_menu_ui)
        pad = 24
        for text, y in getattr(self, "_menu_labels", []):
            ts = FONT.render(text, True, BLACK)
            self.screen.blit(ts, (self.menu_rect.x + pad, y))

        # Sliders
        for s in self.menu_sliders:
            s.draw(self.screen)

        # Buttons
        for b in self.menu_buttons:
            b.draw(self.screen)


    def get_room_area(self) -> pygame.Rect:
        # gleiche Fläche wie beim Zeichnen des Hintergrunds
        return pygame.Rect(20, 20, self.width - 360, self.height - 200)
    
    def build_dialog_buttons(self):
        self.dialog_buttons.clear()

        room_area = self.get_room_area()
        # Unterkante, die nicht vom Log verdeckt wird
        safe_bottom = self.log.rect.y - 12
    # Verdoppelt:
        btn_h = 76      
        btn_w = 320     
        gap   = 24      
        # Eine Zeile Buttons direkt über dem Log, aber noch innerhalb des Raum-Bereichs
        y = max(room_area.y + 8, safe_bottom - btn_h - 8)
        x = room_area.x + 30

        options = [
            ("Ja",       lambda: self.choose_dialog("ja")),
            ("Nein",     lambda: self.choose_dialog("nein")),
            ("Smalltalk",lambda: self.choose_dialog("smalltalk")),
            ("Gespräch beenden", self.end_conversation),
        ]
        for text, cb in options:
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.dialog_buttons.append(Button(rect, text, cb, font=FONT_BIG))
            x += btn_w + gap


    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        Fullscreen= self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        Fullscreen=self.width, self.height = self.screen.get_size()
        pygame.display.set_caption("Team-Adventure (Pygame)")

        setup = Setup()
        self.personen = setup.personen_erzeugen()
        self.raeume = setup.raum_erzeugen(self.personen)
        self.aktueller_raum: Raum = self.raeume["flur"]

        self.panel_people = Panel(pygame.Rect(self.width - 330, 20, 310, 280), "Personen hier")
        self.panel_nav    = Panel(pygame.Rect(self.width - 330, 320, 310, 300), "Raum wechseln")
        self.panel_tasks  = Panel(pygame.Rect(self.width - 330, 650, 310, 140), "Aufgaben")

        self.log = TextLog(
            pygame.Rect(20, self.height - 200, self.width - 360, 180),
            max_lines=6,
            bg_color=(20, 22, 28),
            border_color=(255, 255, 255),
            border_width=2,
            radius=16,
            text_color=(230, 230, 230),
            title_color=(200, 200, 255)
        )

        self.person_buttons: List[Button] = []
        self.nav_buttons: List[Button] = []
        self.task_buttons: List[Button] = []
        self.dialog_buttons: List[Button] = []
        self.active_person: Optional[Person] = None
        self.active_portrait: Optional[pygame.Surface] = None

        # Preload Hintergründe (einmalig)
        self.room_backgrounds = preload_room_backgrounds(
            self.raeume, (self.width - 360, self.height - 200)
        )
        self.room_bg = self.room_backgrounds[self.aktueller_raum.name]

        self.rebuild_room_ui(full=False)
        self.log.add("Willkommen zum Team-Adventure! (Pygame)")
        self.log.add(f"Du befindest dich im {self.aktueller_raum.name}.")

        self.clock = pygame.time.Clock()
        self.running = True
        self.menu_open = False
        self.menu_rect = None
        self.menu_buttons: List[Button] = []
        self.menu_sliders: List[Slider] = []
        self.music_volume = 5  # 0..10
        self.sfx_volume = 5    # 0..10 (Platzhalter)

          # --- NEU: Spielzustand & Start-UI ---
        self.state = "START"              # "START" oder "PLAYING"
        self.start_buttons: List[Button] = []
        self.build_start_ui()             # Buttons für Startbildschirm
        # nach self.width/self.height gesetzt wurden:
        happy_row_target_h = max(60, int(self.height * 0.30))  # ~18% der Höhe
        self.start_happy_images = load_happy_images(happy_row_target_h)

        self.play_music(MENU_MUSIC, volume=0.6, fade_ms=600)  # Menü-Musik starten

          # Startscreen-Buttons (falls vorhanden) oben drauf zeichnen
        if hasattr(self, "start_buttons"):
            for b in self.start_buttons:
                b.draw(self.screen)
        try:
            pygame.mixer.music.set_volume(self.music_volume / 10.0)
        except Exception:
            pass

    def toggle_menu(self):
        if self.state != "PLAYING":
            return
        self.menu_open = not self.menu_open
        if self.menu_open:
            self.build_menu_ui()

    def close_menu(self):
        self.menu_open = False

    def quit_game(self):
        self.running = False

    def on_music_volume_change(self, v: int):
        self.music_volume = v
        try:
            pygame.mixer.music.set_volume(self.music_volume / 10.0)
        except Exception:
            pass

    def build_menu_ui(self):
        # Quadratisches Pop-Up mittig
        side = int(min(self.width, self.height) * 0.55)
        x = (self.width - side) // 2
        y = (self.height - side) // 2
        self.menu_rect = pygame.Rect(x, y, side, side)

        pad = 24
        inner = pygame.Rect(
            self.menu_rect.x + pad, self.menu_rect.y + pad,
            self.menu_rect.width - 2 * pad, self.menu_rect.height - 2 * pad
        )

        self.menu_buttons.clear()
        self.menu_sliders.clear()

        # --- Titelblock-Höhe (Menü-Titel) ---
        title_h = FONT_BIG.get_height() + 12  # Platz für "Menü"
        content_top = inner.y + title_h
        content_bot = inner.bottom

        # --- Steuerhöhen ---
        btn_h = 56
        label_h = FONT.get_height()
        slider_h = 40
        label_space = 6  # Abstand zwischen Label und Slider

        # Gesamthöhe der 4 Gruppen (Button, (Label+Slider), (Label+Slider), Button)
        total_controls_h = (
            btn_h +
            (label_h + label_space + slider_h) +
            (label_h + label_space + slider_h) +
            btn_h
        )

        avail_h = content_bot - content_top
        # Gleichmäßige Lücken: 5 Gaps (oben, zw. 1/2, zw. 2/3, zw. 3/4, unten)
        gap = max(12, (avail_h - total_controls_h) // 5)

        # ---------- Platzierung ----------
        y_ptr = content_top + gap

        # Fortfahren (unter Titel)
        cont_rect = pygame.Rect(inner.x, y_ptr, inner.width, btn_h)
        self.menu_buttons.append(Button(cont_rect, "Fortfahren", self.close_menu, font=FONT_BIG))
        y_ptr += btn_h + gap

        # SFX: Label + Slider (Platzhalter)
        sfx_label_y = y_ptr
        y_ptr += label_h + label_space
        sfx_slider_rect = pygame.Rect(inner.x, y_ptr, inner.width - 48, slider_h)
        self.menu_sliders.append(
            Slider(sfx_slider_rect, 0, 10, self.sfx_volume, on_change=lambda v: setattr(self, "sfx_volume", v))
        )
        y_ptr += slider_h + gap

        # Musik: Label + Slider (steuert Mixer)
        music_label_y = y_ptr
        y_ptr += label_h + label_space
        music_slider_rect = pygame.Rect(inner.x, y_ptr, inner.width - 48, slider_h)
        self.menu_sliders.append(
            Slider(music_slider_rect, 0, 10, self.music_volume, on_change=self.on_music_volume_change)
        )
        y_ptr += slider_h + gap

        # Spiel beenden (unten)
        quit_rect = pygame.Rect(inner.x, y_ptr, inner.width, btn_h)
        self.menu_buttons.append(Button(quit_rect, "Spiel beenden", self.quit_game, font=FONT_BIG))
        y_ptr += btn_h
        # Unterer Gap ergibt sich automatisch, weil wir mit den Gaps kalkuliert haben.

        # Labels merken für draw()
        self._menu_labels = [
            ("SFX Lautstärke", sfx_label_y),
            ("Musik Lautstärke", music_label_y),
        ]


    def draw_start_screen(self):
        # 1) Weißer Hintergrund
        self.screen.fill(WHITE)

        # 2) Titel oben links in Magenta
        title_text = "TeleTEXT - Ein Team Adventure"
        title_font = pygame.font.SysFont("arial", 42)  # gern anpassen
        title_surf = title_font.render(title_text, True, MAGENTA)
        pad = 16
        self.screen.blit(title_surf, (pad, pad))

        # 3) Reihe unten rechts: alle Happy-Portraits
        imgs = getattr(self, "start_happy_images", [])
        if imgs:
            gap = 12
            bottom_pad = 16
            right_pad = 16

            # Falls die Gesamtbreite zu groß ist, proportional kleiner zeichnen
            total_w = sum(i.get_width() for i in imgs) + gap * (len(imgs) - 1)
            avail_w = self.width - 2 * pad
            scaled = imgs
            if total_w > avail_w and total_w > 0:
                factor = avail_w / total_w
                scaled = [
                    pygame.transform.smoothscale(
                        i,
                        (max(1, int(i.get_width() * factor)), max(1, int(i.get_height() * factor)))
                    )
                    for i in imgs
                ]

            row_h = max(i.get_height() for i in scaled)
            row_w = sum(i.get_width() for i in scaled) + gap * (len(scaled) - 1)

            # unten rechts ausrichten
            x = self.width - right_pad - row_w
            y = self.height - bottom_pad - row_h

            for i in scaled:
                self.screen.blit(i, (x, y))
                x += i.get_width() + gap

        # Startscreen-Buttons (falls vorhanden) oben drauf
        for b in getattr(self, "start_buttons", []):
            b.draw(self.screen)

    

    def draw_buttons_in_panel(self, panel: Panel, buttons: List[Button]):
        """Zeichnet Buttons geclippt in die Panel-Innenfläche."""
        inner = panel.content_rect()
        prev = self.screen.get_clip()
        self.screen.set_clip(inner)
        for b in buttons:
            b.draw(self.screen)
        self.screen.set_clip(prev)

    def rebuild_room_ui(self, full=False):
        if full:
            self.room_bg = load_room_background(self.aktueller_raum, (self.width - 360, self.height - 200))

        # Personen
        self.person_buttons.clear()
        people_inner = self.panel_people.content_rect()
        x, y, w = people_inner.x, people_inner.y, people_inner.width
        for p in self.aktueller_raum.personen:
            rect = pygame.Rect(x, y, w, 40)
            self.person_buttons.append(Button(rect, f"{p.name} ({p.rolle})",
                                              lambda pers=p: self.on_person_clicked(pers)))
            y += 46

        # Navigation
        self.nav_buttons.clear()
        nav_inner = self.panel_nav.content_rect()
        x, y, w = nav_inner.x, nav_inner.y, nav_inner.width
        for vr in self.aktueller_raum.verbindungen:
            rect = pygame.Rect(x, y, w, 40)
            self.nav_buttons.append(Button(rect, vr.name,
                                           lambda ziel=vr: self.on_change_room(ziel.name)))
            y += 46

        # Aufgaben
        self.build_task_buttons()

        # Dialog-UI reset
        self.dialog_buttons.clear()
        self.active_person = None
        self.active_portrait = None

    def build_task_buttons(self):
        self.task_buttons.clear()
        task_inner = self.panel_tasks.content_rect()
        x, y, w = task_inner.x, task_inner.y, task_inner.width
        if not self.aktueller_raum.aufgaben:
            rect = pygame.Rect(x, y, w, 36)
            self.task_buttons.append(Button(rect, "Keine Aufgaben hier", lambda: None))
            return
        for aufgabe in self.aktueller_raum.aufgaben:
            label = f"[{aufgabe.id}] {aufgabe.name}"
            rect = pygame.Rect(x, y, w, 36)
            self.task_buttons.append(Button(rect, label,
                                            lambda a_id=aufgabe.id: self.on_execute_task(a_id)))
            y += 42

    def start_game(self):
        self.state = "PLAYING"
        self.play_music(GAME_MUSIC, volume=0.5, fade_ms=600)
        # Optional: direkt Dialog-Buttons ausblenden, falls offen
        self.dialog_buttons.clear()

    def quit_game(self):
        self.running = False

    def play_music(self, path: str, volume: float = 0.6, fade_ms: int = 400):
        if not os.path.exists(path):
            self.log.add(f"[Audio] Datei fehlt: {os.path.basename(path)}")
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1, fade_ms=fade_ms)  # loopend
        except Exception as e:
            self.log.add(f"[Audio] Fehler beim Abspielen: {e}")

    def on_person_clicked(self, person: Person):
        self.active_person = person

        # >>> dynamische Zielgröße fürs Portrait (groß)
        room_area = self.get_room_area()
        target_w = int(room_area.width * 0.35)   # ~35% der Raum-Breite
        target_h = int(room_area.height * 0.90)  # ~90% der Raum-Höhe
        self.active_portrait = load_person_portrait(person.name, (target_w, target_h))
        # <<<

        if self.active_portrait:
            self.log.add(f"[Portrait] {person.name} geladen.")
        else:
            self.log.add(f"[Portrait] Für {person.name} nicht gefunden.")
        self.log.add(f'{person.name}: "Hallo! Möchtest du etwas für mich erledigen?"')

        # Nur HIER die Dialog-Buttons bauen (oben, nicht vom Log verdeckt)
        self.build_dialog_buttons()

    def build_start_ui(self):
        self.start_buttons.clear()
        sw, sh = self.width, self.height
        btn_w, btn_h, gap = 360, 80, 20
        x = (sw - btn_w) // 2
        y = int(sh * 0.55)

        start_btn = Button(pygame.Rect(x, y, btn_w, btn_h), "Spiel starten",
                        self.start_game, font=FONT_BIG)
        quit_btn  = Button(pygame.Rect(x, y + btn_h + gap, btn_w, btn_h), "Beenden",
                        self.quit_game, font=FONT_BIG)
        self.start_buttons.extend([start_btn, quit_btn])

    def choose_dialog(self, answer: str):
        p = self.active_person
        if p is None:
            return
        ans = answer.lower()

        if ans == "ja":
            self.log.add('Du: "Ja."')
            self.log.add(f'{p.name}: "Super! Ich habe eine Aufgabe für dich."')
            self.create_task_from_person(p)
            p.relationship += 2
            self.log.add(f"(Beziehung zu {p.name} +2 → {p.relationship})")
            self.build_task_buttons()

        elif ans == "smalltalk":
            self.log.add('Du: "Smalltalk."')
            if p.rede_lust > 3:
                self.log.add(f'{p.name}: "Oh, ich rede so gerne... Übrigens, wusstest du schon, dass ..."')
            else:
                self.log.add(f'{p.name}: "Hm, na gut."')
            p.relationship += 1
            self.log.add(f"(Beziehung zu {p.name} +1 → {p.relationship})")

        elif ans == "nein":
            self.log.add('Du: "Nein."')
            self.log.add(f'{p.name}: "Schade, vielleicht später!"')

        else:
            self.log.add(f'{p.name}: "Okay."')

        # WICHTIG: NICHT self.dialog_buttons.clear() und NICHT active_* = None
        # Person bleibt sichtbar, bis "Gespräch beenden" gedrückt wird.
    def end_conversation(self):
        if self.active_person:
            self.log.add(f'{self.active_person.name}: "Bis später!"')
        self.dialog_buttons.clear()
        self.active_person = None
        self.active_portrait = None

    def create_task_from_person(self, person: Person):
        if person.name == "Holger":
            neue_aufgabe = Aufgabe(10, "Brief abgeben", "Gehe zur Post und gib den Brief ab.")
            self.raeume["post"].aufgaben.append(neue_aufgabe)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{neue_aufgabe.id}] {neue_aufgabe.name}")
        elif person.name == "Flo":
            neue_aufgabe = Aufgabe(11, "Dokument drucken", "Drucke ein Dokument im Druckerraum.")
            self.raeume["druckerraum"].aufgaben.append(neue_aufgabe)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{neue_aufgabe.id}] {neue_aufgabe.name}")
        elif person.name == "Kirsten":
            neue_aufgabe = Aufgabe(12, "Technik kontrollieren", "Überprüfe die Technik im Technikraum.")
            self.raeume["technikraum"].aufgaben.append(neue_aufgabe)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{neue_aufgabe.id}] {neue_aufgabe.name}")
        else:
            self.log.add(f"{person.name} hat aktuell keine Aufgabe für dich.")

    def raum_wechseln(self, neuer_raum: str):
        for raum in self.aktueller_raum.verbindungen:
            if raum.name.lower() == neuer_raum:
                self.aktueller_raum = raum
                self.log.add(f"Du bist jetzt im {self.aktueller_raum.name}.")
                return
        self.log.add("Du kannst nicht dorthin gehen.")

    def aufgabe_ausfuehren(self, aufgabe_id: int):
        for aufgabe in list(self.aktueller_raum.aufgaben):
            if aufgabe.id == aufgabe_id:
                self.log.add(f"Aufgabe '{aufgabe.name}' ausgeführt!")
                self.aktueller_raum.aufgaben.remove(aufgabe)
                return
        self.log.add("Ungültige Aufgaben-ID.")

    def on_change_room(self, zielraum_name: str):
        self.raum_wechseln(zielraum_name.lower())
        self.rebuild_room_ui(full=False)
        self.room_bg = self.room_backgrounds[self.aktueller_raum.name]
        self.active_portrait = None

    def on_execute_task(self, aufgabe_id: int):
        found = False
        for a in list(self.aktueller_raum.aufgaben):
            if a.id == aufgabe_id:
                found = True
                self.log.add(f"Aufgabe '{a.name}' ausgeführt!")
                self.aktueller_raum.aufgaben.remove(a)
                break
        if not found:
            self.log.add("Ungültige Aufgaben-ID oder Aufgabe nicht in diesem Raum.")
        self.build_task_buttons()

    # In class GameApp:
    #def get_room_area(self) -> pygame.Rect:
    #    return pygame.Rect(20, 20, self.width - 360, self.height - 200)

    def draw(self):
        if self.state == "START":
            self.draw_start_screen()
            pygame.display.flip()
            return

        # --- normaler Spiel-Draw darunter ---
        self.screen.fill((15, 15, 20))

        room_area = self.get_room_area()
        pygame.draw.rect(self.screen, BLACK, room_area, 2, border_radius=16)
        self.screen.blit(self.room_bg, room_area)

        self.panel_people.draw(self.screen)
        self.panel_nav.draw(self.screen)
        self.panel_tasks.draw(self.screen)

        self.draw_buttons_in_panel(self.panel_people, self.person_buttons)
        self.draw_buttons_in_panel(self.panel_nav, self.nav_buttons)
        self.draw_buttons_in_panel(self.panel_tasks, self.task_buttons)

        if self.active_portrait:
            img = self.active_portrait
            img_rect = img.get_rect()
            margin_right = 24
            margin_bottom = 16
            img_rect.right = room_area.right - margin_right
            img_rect.bottom = room_area.bottom - margin_bottom

            prev_clip = self.screen.get_clip()
            self.screen.set_clip(room_area)
            self.screen.blit(img, img_rect)
            self.screen.set_clip(prev_clip)

            if self.active_person:
                name_ts = FONT_BIG.render(self.active_person.name, True, WHITE)
                self.screen.blit(name_ts, (img_rect.x + 12, img_rect.y + 8))

        for b in self.dialog_buttons:
            b.draw(self.screen)

        self.log.draw(self.screen)
        self.draw_menu_overlay()
        pygame.display.flip()
        
      


    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                # --- Startbildschirm ---
                if self.state == "START":
                    if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.start_game()  # falls du die Funktion hast
                    for b in getattr(self, "start_buttons", []):
                        b.handle_event(event)
                    continue

                # --- Spiel ---
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.toggle_menu()
                    continue  # damit in diesem Tick nichts "durchfällt"

                if self.menu_open:
                    # Events nur ans Menü weiterreichen
                    for b in self.menu_buttons:
                        b.handle_event(event)
                    for s in self.menu_sliders:
                        s.handle_event(event)
                    continue

                # Normale Spiel-Events
                self.log.handle_event(event)
                for b in (self.person_buttons + self.nav_buttons + self.task_buttons + self.dialog_buttons):
                    b.handle_event(event)

            self.draw()
            self.clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    app = GameApp()
    app.run()
