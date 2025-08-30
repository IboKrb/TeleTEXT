# game/scenes/play_scene.py
import pygame
from typing import List
from game.scenes.base_scene import Scene
from game.scenes.pause_menu import PauseMenu
from systems import config
from ui import Button, Panel, TextLog, FONT_BIG, WHITE, BLACK

class PlayScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        # Daten (über Setup)
        setup = self.game.setup
        self.personen = setup.personen_erzeugen()
        self.raeume = setup.raum_erzeugen(self.personen)
        self.aktueller_raum = self.raeume["flur"]

        # UI-Panels rechts
        self.panel_people = Panel(pygame.Rect(self.game.width - 330, 20, 310, 280), "Personen hier")
        self.panel_nav    = Panel(pygame.Rect(self.game.width - 330, 320, 310, 300), "Raum wechseln")
        self.panel_tasks  = Panel(pygame.Rect(self.game.width - 330, 650, 310, 140), "Aufgaben")

        # Log unten
        self.log = TextLog(pygame.Rect(20, self.game.height - 200, self.game.width - 360, 180),
                           max_lines=6, bg_color=(20,22,28), border_color=(255,255,255),
                           border_width=2, radius=16, text_color=(230,230,230))

        # Buttons
        self.person_buttons: List[Button] = []
        self.nav_buttons: List[Button] = []
        self.task_buttons: List[Button] = []
        self.dialog_buttons: List[Button] = []

        # Portrait-State
        self.active_person = None
        self.active_portrait = None

        # Raumhintergründe vorladen
        room_area = self.get_room_area()
        fallback_title = FONT_BIG.render(self.aktueller_raum.name, True, (240,240,120))
        self.game.assets.preload_rooms(self.raeume, (room_area.width, room_area.height),
                                       fallback_color=(25,35,60), fallback_title_surf=fallback_title)
        self.room_bg = self.game.assets.get_room_bg(self.aktueller_raum.name)

        # Initial UI
        self.rebuild_room_ui(full=False)
        self.log.add("Willkommen zum Team-Adventure! (Pygame)")
        self.log.add(f"Du befindest dich im {self.aktueller_raum.name}.")

    # ------- Helpers -------
    def get_room_area(self) -> pygame.Rect:
        l, t, right_panel_w, bottom_h = config.ROOM_AREA_MARGIN
        return pygame.Rect(l, t, self.game.width - right_panel_w - l, self.game.height - bottom_h - t)

    def draw_buttons_in_panel(self, panel: Panel, buttons: list):
        inner = panel.content_rect()
        prev = self.game.screen.get_clip()
        self.game.screen.set_clip(inner)
        for b in buttons: b.draw(self.game.screen)
        self.game.screen.set_clip(prev)

    def rebuild_room_ui(self, full=False):
        if full:
            self.room_bg = self.game.assets.get_room_bg(self.aktueller_raum.name)

        self.person_buttons.clear()
        people_inner = self.panel_people.content_rect()
        x, y, w = people_inner.x, people_inner.y, people_inner.width
        for p in self.aktueller_raum.personen:
            rect = pygame.Rect(x, y, w, 40)
            self.person_buttons.append(Button(rect, f"{p.name} ({p.rolle})",
                                              lambda pers=p: self.on_person_clicked(pers)))
            y += 46

        self.nav_buttons.clear()
        nav_inner = self.panel_nav.content_rect()
        x, y, w = nav_inner.x, nav_inner.y, nav_inner.width
        for vr in self.aktueller_raum.verbindungen:
            rect = pygame.Rect(x, y, w, 40)
            self.nav_buttons.append(Button(rect, vr.name, lambda ziel=vr: self.on_change_room(ziel.name)))
            y += 46

        self.build_task_buttons()
        self.dialog_buttons.clear()
        self.active_person = None
        self.active_portrait = None

    def build_task_buttons(self):
        self.task_buttons.clear()
        task_inner = self.panel_tasks.content_rect()
        x, y, w = task_inner.x, task_inner.y, task_inner.width
        if not self.aktueller_raum.aufgaben:
            self.task_buttons.append(Button(pygame.Rect(x, y, w, 36), "Keine Aufgaben hier", lambda: None))
            return
        for a in self.aktueller_raum.aufgaben:
            self.task_buttons.append(Button(pygame.Rect(x, y, w, 36), f"[{a.id}] {a.name}",
                                            lambda a_id=a.id: self.on_execute_task(a_id)))
            y += 42

    def build_dialog_buttons(self):
        self.dialog_buttons.clear()
        room_area = self.get_room_area()
        safe_bottom = self.log.rect.y - 12
        btn_h, btn_w, gap = 76, 320, 24
        y = max(room_area.y + 8, safe_bottom - btn_h - 8)
        x = room_area.x + 30
        options = [("Ja", lambda: self.choose_dialog("ja")),
                   ("Nein", lambda: self.choose_dialog("nein")),
                   ("Smalltalk", lambda: self.choose_dialog("smalltalk")),
                   ("Gespräch beenden", self.end_conversation)]
        for text, cb in options:
            self.dialog_buttons.append(Button(pygame.Rect(x, y, btn_w, btn_h), text, cb, font=FONT_BIG))
            x += btn_w + gap

    # ------- Events -------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.scene_manager.push(PauseMenu(self.game))
            return

        self.log.handle_event(event)
        for b in (self.person_buttons + self.nav_buttons + self.task_buttons + self.dialog_buttons):
            b.handle_event(event)

    def update(self, dt): pass

    def draw(self, screen):
        screen.fill((15, 15, 20))
        room_area = self.get_room_area()
        pygame.draw.rect(screen, BLACK, room_area, 2, border_radius=16)
        screen.blit(self.room_bg, room_area)

        self.panel_people.draw(screen)
        self.panel_nav.draw(screen)
        self.panel_tasks.draw(screen)

        self.draw_buttons_in_panel(self.panel_people, self.person_buttons)
        self.draw_buttons_in_panel(self.panel_nav, self.nav_buttons)
        self.draw_buttons_in_panel(self.panel_tasks, self.task_buttons)

        if self.active_portrait:
            img = self.active_portrait
            img_rect = img.get_rect()
            img_rect.right = room_area.right - 24
            img_rect.bottom = room_area.bottom - 16
            prev = screen.get_clip()
            screen.set_clip(room_area)
            screen.blit(img, img_rect)
            screen.set_clip(prev)
            if self.active_person:
                name_ts = FONT_BIG.render(self.active_person.name, True, WHITE)
                screen.blit(name_ts, (img_rect.x + 12, img_rect.y + 8))

        for b in self.dialog_buttons: b.draw(screen)
        self.log.draw(screen)

    # ------- Game Actions -------
    def on_person_clicked(self, person):
        self.active_person = person
        room_area = self.get_room_area()
        target_w = int(room_area.width * 0.35)
        target_h = int(room_area.height * 0.90)
        self.active_portrait = self.game.assets.load_person_portrait(person.name, (target_w, target_h))
        if self.active_portrait:
            self.log.add(f"[Portrait] {person.name} geladen.")
        else:
            self.log.add(f"[Portrait] Für {person.name} nicht gefunden.")
        self.log.add(f'{person.name}: "Hallo! Möchtest du etwas für mich erledigen?"')
        self.build_dialog_buttons()

    def choose_dialog(self, answer: str):
        p = self.active_person
        if not p: return
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

    def end_conversation(self):
        if self.active_person:
            self.log.add(f'{self.active_person.name}: "Bis später!"')
        self.dialog_buttons.clear()
        self.active_person = None
        self.active_portrait = None

    def create_task_from_person(self, person):
        from aufgabe import Aufgabe  # vorerst so lassen
        if person.name == "Holger":
            a = Aufgabe(10, "Brief abgeben", "Gehe zur Post und gib den Brief ab.")
            self.raeume["post"].aufgaben.append(a)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{a.id}] {a.name}")
        elif person.name == "Flo":
            a = Aufgabe(11, "Dokument drucken", "Drucke ein Dokument im Druckerraum.")
            self.raeume["druckerraum"].aufgaben.append(a)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{a.id}] {a.name}")
        elif person.name == "Kirsten":
            a = Aufgabe(12, "Technik kontrollieren", "Überprüfe die Technik im Technikraum.")
            self.raeume["technikraum"].aufgaben.append(a)
            self.log.add(f"{person.name} gibt dir die Aufgabe: [{a.id}] {a.name}")
        else:
            self.log.add(f"{person.name} hat aktuell keine Aufgabe für dich.")

    def on_change_room(self, zielraum_name: str):
        for raum in self.aktueller_raum.verbindungen:
            if raum.name.lower() == zielraum_name.lower():
                self.aktueller_raum = raum
                self.room_bg = self.game.assets.get_room_bg(self.aktueller_raum.name)
                self.log.add(f"Du bist jetzt im {self.aktueller_raum.name}.")
                self.rebuild_room_ui(full=False)
                return
        self.log.add("Du kannst nicht dorthin gehen.")

    def on_execute_task(self, aufgabe_id: int):
        for a in list(self.aktueller_raum.aufgaben):
            if a.id == aufgabe_id:
                self.log.add(f"Aufgabe '{a.name}' ausgeführt!")
                self.aktueller_raum.aufgaben.remove(a)
                self.build_task_buttons()
                return
        self.log.add("Ungültige Aufgaben-ID.")
