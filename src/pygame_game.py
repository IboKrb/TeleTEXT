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

from ui import Button, Panel, Slider, TextLog, FONT, FONT_SMALL, FONT_BIG, DARK_BLUE, ACCENT, WHITE, BLACK, GRAY, LIGHT_GRAY, MAGENTA
from audio import Audio


################################################################################
# Pygame-Frontend, das die bestehende Spiel-Logik nutzt
################################################################################

# Räume-Hintergründe (z. B. ../assets/Rooms/flur.png)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets/Rooms")

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
        # Vollbild (ermittelt Desktopauflösung)
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.width, self.height = self.screen.get_size()

        # Fenster-Modus (statt Fullscreen)
        self.screen = pygame.display.set_mode((self.width, self.height))
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
        self.music_volume = 5
        self.sfx_volume = 5

        # Spielzustand & Start-UI
        self.state = "START"
        self.start_buttons: List[Button] = []
        self.build_start_ui()

        # Happy-Faces Startscreen
        happy_row_target_h = max(60, int(self.height * 0.30))
        self.start_happy_images = load_happy_images(happy_row_target_h)

        # --- Audio-Manager sauber hier erzeugen ---
        self.audio = Audio(
            audio_dir=os.path.join(os.path.dirname(__file__), "../assets/Audio"),
            menu_track="menu",
            game_track="game",
            default_music_volume=self.music_volume,
            default_sfx_volume=self.sfx_volume,
            logger=lambda m: self.log.add(m)
        )
        # Startscreen → Menümusik
        self.audio.play_menu_music()


    def toggle_menu(self):
        if self.state != "PLAYING":
            return
        self.menu_open = not self.menu_open
        if self.menu_open:
            self.build_menu_ui()

    def close_menu(self):
        self.menu_open = False

    def on_music_volume_change(self, v: int):
        self.music_volume = v
        self.audio.set_music_volume_0_10(v)

    def on_sfx_volume_change(self, v: int):
        self.sfx_volume = v
        self.audio.set_sfx_volume_0_10(v)


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
        self.audio.play_game_music()
        self.dialog_buttons.clear()

    def quit_game(self):
        self.audio.stop_music(fade_ms=400)
        self.running = False

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
