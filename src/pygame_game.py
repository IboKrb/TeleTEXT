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

class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback, tooltip: Optional[str] = None):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.tooltip = tooltip
        self.hover = False

    def draw(self, surface: pygame.Surface):
        color = LIGHT_GRAY if self.hover else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        text_surf = FONT.render(self.text, True, BLACK)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.callback):
                    self.callback()

class Panel:
    """Einfaches Rechteck-Panel mit Titel; verwendet für Seitenleisten/Log-Fenster."""
    def __init__(self, rect: pygame.Rect, title: str = ""):
        self.rect = rect
        self.title = title

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (235, 235, 240), self.rect, border_radius=12)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=12)
        if self.title:
            title_surf = FONT_BIG.render(self.title, True, BLACK)
            surface.blit(title_surf, (self.rect.x + 12, self.rect.y + 8))

class TextLog:
    """Scrollbarer Text-Log für Dialoge/Status."""
    def __init__(self, rect: pygame.Rect, max_lines: int = 10):
        self.rect = rect
        self.lines: List[str] = []
        self.max_lines = max_lines
        self.scroll_offset = 0

    def add(self, line: str):
        # Split lange Zeilen grob
        max_chars = 80
        while len(line) > max_chars:
            self.lines.append(line[:max_chars])
            line = line[max_chars:]
        self.lines.append(line)
        # Auf Max-Linien beschränken
        if len(self.lines) > 500:
            self.lines = self.lines[-500:]

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=8)
        # Text einzeichnen
        x = self.rect.x + 10
        y = self.rect.y + 8
        visible = self.lines[-self.max_lines:]
        for line in visible:
            ts = FONT_SMALL.render(line, True, BLACK)
            surface.blit(ts, (x, y))
            y += ts.get_height() + 4

################################################################################
# Pygame-Frontend, das die bestehende Spiel-Logik nutzt
################################################################################

# Räume-Hintergründe (z. B. ../assets/Rooms/flur.png)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../assets/Rooms")

################################################################################
# Personen-Portraits laden
################################################################################

# Wir erlauben ../assets als Root
ASSETS_ROOTS = [
    os.path.join(os.path.dirname(__file__), "../assets"),
]

def load_person_portrait(person_name: str, target_size: Tuple[int, int]) -> Optional[pygame.Surface]:
    """
    Erwartete Struktur (Case-sensitiv je nach OS):
        ../assets/People/<PersonenName>/<nameNeutral>.(png|jpg|jpeg|webp)
    Beispiel:
        ../assets/People/Kirsten/kirstenNeutral.png
    """
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
    """
    Versucht, ein Hintergrundbild aus ../assets/Rooms/<raumname>.png zu laden.
    Fallback: einfärbte Fläche mit Raumtitel.
    """
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

    # Fallback: einfärben + Titel
    surf.fill(DARK_BLUE)
    title = FONT_BIG.render(raum.name, True, ACCENT)
    surf.blit(title, title.get_rect(center=(target_size[0] // 2, 30)))
    return surf

def wrap_text(text: str, font: pygame.font.Font, max_width: int) -> List[str]:
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

class GameApp:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Team-Adventure (Pygame)")

        # Setup-Daten laden (Personen & Räume)
        setup = Setup()
        self.personen = setup.personen_erzeugen()
        self.raeume = setup.raum_erzeugen(self.personen)
        self.aktueller_raum: Raum = self.raeume["flur"]

        # UI-Elemente (Panels)
        self.panel_people = Panel(pygame.Rect(self.width - 330, 20, 310, 280), "Personen hier")
        self.panel_nav = Panel(pygame.Rect(self.width - 330, 320, 310, 220), "Wechseln")
        self.panel_tasks = Panel(pygame.Rect(self.width - 330, 560, 310, 140), "Aufgaben")
        self.log = TextLog(pygame.Rect(20, self.height - 180, self.width - 370, 160), max_lines=8)

        # Buttons dynamisch je nach Raum
        self.person_buttons: List[Button] = []
        self.nav_buttons: List[Button] = []
        self.task_buttons: List[Button] = []

        # Action-Buttons (Dialogoptionen), eingeblendet wenn Person angeklickt
        self.dialog_buttons: List[Button] = []
        self.active_person: Optional[Person] = None
        self.active_portrait: Optional[pygame.Surface] = None

        # Preload Hintergrund
        self.room_bg = load_room_background(self.aktueller_raum, (self.width - 360, self.height - 200))

        self.rebuild_room_ui(full=True)
        self.log.add("Willkommen zum Team-Adventure! (Pygame)")
        self.log.add(f"Du befindest dich im {self.aktueller_raum.name}.")

        self.clock = pygame.time.Clock()
        self.running = True

    def rebuild_room_ui(self, full=False):
        """Erstellt die Buttons neu, basierend auf dem aktuellen Raumzustand."""
        if full:
            self.room_bg = load_room_background(self.aktueller_raum, (self.width - 360, self.height - 200))

        # Personen-Buttons
        self.person_buttons.clear()
        x = self.panel_people.rect.x + 15
        y = self.panel_people.rect.y + 50
        for p in self.aktueller_raum.personen:
            rect = pygame.Rect(x, y, 280, 40)
            self.person_buttons.append(Button(rect, f"{p.name} ({p.rolle})", lambda pers=p: self.on_person_clicked(pers)))
            y += 50

        # Navigations-Buttons (verbindungen)
        self.nav_buttons.clear()
        x = self.panel_nav.rect.x + 15
        y = self.panel_nav.rect.y + 50
        for vr in self.aktueller_raum.verbindungen:
            rect = pygame.Rect(x, y, 280, 40)
            self.nav_buttons.append(Button(rect, vr.name, lambda ziel=vr: self.on_change_room(ziel.name)))
            y += 50

        # Aufgaben-Buttons (im Raum vorhandene Aufgaben ausführen)
        self.build_task_buttons()

        # Dialog-Buttons leeren
        self.dialog_buttons.clear()
        self.active_person = None

    def build_task_buttons(self):
        self.task_buttons.clear()
        x = self.panel_tasks.rect.x + 15
        y = self.panel_tasks.rect.y + 50
        if not self.aktueller_raum.aufgaben:
            rect = pygame.Rect(x, y, 280, 36)
            self.task_buttons.append(Button(rect, "Keine Aufgaben hier", lambda: None))
            return
        for aufgabe in self.aktueller_raum.aufgaben:
            # Jede Aufgabe per Klick ausführen
            label = f"[{aufgabe.id}] {aufgabe.name}"
            rect = pygame.Rect(x, y, 280, 36)
            self.task_buttons.append(Button(rect, label, lambda a_id=aufgabe.id: self.on_execute_task(a_id)))
            y += 42

    def on_person_clicked(self, person: Person):
        """Person ausgewählt → Dialogoptionen zeigen (statt input())."""
        self.active_person = person
        # Portrait laden (z. B. ../assets/People/Kirsten/kirstenNeutral.png)
        self.active_portrait = load_person_portrait(person.name, (420, 420))
        if self.active_portrait:
            self.log.add(f"[Portrait] {person.name} geladen.")
        else:
            self.log.add(f"[Portrait] Für {person.name} nicht gefunden.")
        self.log.add(f"{person.name}: \"Hallo! Möchtest du etwas für mich erledigen?\"")
        self.dialog_buttons.clear()

        # Drei Optionen wie in eurer Terminal-Version
        base_y = self.height - 220
        options = [
            ("Ja", lambda: self.choose_dialog("ja")),
            ("Nein", lambda: self.choose_dialog("nein")),
            ("Smalltalk", lambda: self.choose_dialog("smalltalk")),
        ]
        x = 30
        for text, cb in options:
            rect = pygame.Rect(x, base_y, 160, 38)
            self.dialog_buttons.append(Button(rect, text, cb))
            x += 180

    def choose_dialog(self, answer: str):
        p = self.active_person
        if p is None:
            return
        ans = answer.lower()
        if ans == "ja":
            self.log.add(f"Du: \"Ja.\"")
            self.log.add(f"{p.name}: \"Super! Ich habe eine Aufgabe für dich.\"")
            # Aufgabe erzeugen: aus alter Spiel-Logik übernommen
            self.create_task_from_person(p)
            p.relationship += 2
            self.log.add(f"(Beziehung zu {p.name} +2 → {p.relationship})")
            # Aufgaben-Panel neu bauen
            self.build_task_buttons()
        elif ans == "smalltalk":
            self.log.add("Du: \"Smalltalk.\"")
            if p.rede_lust > 3:
                self.log.add(f"{p.name}: \"Oh, ich rede so gerne... Übrigens, wusstest du schon, dass ...\"")
            else:
                self.log.add(f"{p.name}: \"Hm, na gut.\"")
            p.relationship += 1
            self.log.add(f"(Beziehung zu {p.name} +1 → {p.relationship})")
        elif ans == "nein":
            self.log.add("Du: \"Nein.\"")
            self.log.add(f"{p.name}: \"Schade, vielleicht später!\"")
        else:
            self.log.add(f"{p.name}: \"Okay.\"")

        # Dialog-Buttons schließen
        self.dialog_buttons.clear()
        self.active_person = None
        self.active_portrait = None

    def create_task_from_person(self, person: Person):
        """Erzeugt eine Aufgabe abhängig von der Person und legt sie im passenden Raum ab."""
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
        """Wechselt den Raum, wenn eine Verbindung existiert (neuer_raum: lowercase Name)."""
        for raum in self.aktueller_raum.verbindungen:
            if raum.name.lower() == neuer_raum:
                self.aktueller_raum = raum
                self.log.add(f"Du bist jetzt im {self.aktueller_raum.name}.")
                return
        self.log.add("Du kannst nicht dorthin gehen.")

    def aufgabe_ausfuehren(self, aufgabe_id: int):
        """Führt eine Aufgabe im aktuellen Raum aus und entfernt sie."""
        for aufgabe in list(self.aktueller_raum.aufgaben):
            if aufgabe.id == aufgabe_id:
                self.log.add(f"Aufgabe '{aufgabe.name}' ausgeführt!")
                self.aktueller_raum.aufgaben.remove(aufgabe)
                return
        self.log.add("Ungültige Aufgaben-ID.")

    def on_change_room(self, zielraum_name: str):
        """Raumwechsel via Button."""
        self.raum_wechseln(zielraum_name.lower())
        self.rebuild_room_ui(full=True)
        self.active_portrait = None

    def on_execute_task(self, aufgabe_id: int):
        """Aufgabe im aktuellen Raum ausführen (wie 'aufgabe_ausfuehren')."""
        # Prüfen, ob Aufgabe existiert
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

    def draw(self):
        self.screen.fill((15, 15, 20))

        # Hintergrund / Raumfläche links
        room_area = pygame.Rect(20, 20, self.width - 360, self.height - 200)
        pygame.draw.rect(self.screen, BLACK, room_area, 2, border_radius=16)
        self.screen.blit(self.room_bg, room_area)

        # Portrait im Raum-Bereich anzeigen, falls vorhanden
        if self.active_portrait:
            portrait_frame = pygame.Rect(room_area.x + 600, room_area.y + 120, 320, 420)
            img_rect = self.active_portrait.get_rect(center=portrait_frame.center)
            prev_clip = self.screen.get_clip()
            self.screen.set_clip(portrait_frame)
            self.screen.blit(self.active_portrait, img_rect)
            self.screen.set_clip(prev_clip)
            if self.active_person:
                name_ts = FONT_BIG.render(self.active_person.name, True, WHITE)
                self.screen.blit(name_ts, (portrait_frame.x + 12, portrait_frame.y + 10))

        # Panels
        self.panel_people.draw(self.screen)
        self.panel_nav.draw(self.screen)
        self.panel_tasks.draw(self.screen)

        # Buttons
        for b in self.person_buttons: b.draw(self.screen)
        for b in self.nav_buttons: b.draw(self.screen)
        for b in self.task_buttons: b.draw(self.screen)
        for b in self.dialog_buttons: b.draw(self.screen)

        # Log
        self.log.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Button Events
                for b in (self.person_buttons + self.nav_buttons + self.task_buttons + self.dialog_buttons):
                    b.handle_event(event)

            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    app = GameApp()
    app.run()
