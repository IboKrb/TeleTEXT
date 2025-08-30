# game/scenes/start_scene.py
import pygame
from game.scenes.base_scene import Scene
from systems import config
from ui import Button, FONT_BIG, MAGENTA, WHITE  # aus deiner bestehenden ui.py

class StartScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        # Musik
        self.game.audio.play_menu_music()

        # UI
        sw, sh = self.game.width, self.game.height
        btn_w, btn_h, gap = 360, 80, 20
        x = (sw - btn_w) // 2
        y = int(sh * 0.55)

        self.buttons = [
            Button(pygame.Rect(x, y, btn_w, btn_h), "Spiel starten", self.on_start, font=FONT_BIG),
            Button(pygame.Rect(x, y + btn_h + gap, btn_w, btn_h), "Beenden", self.game.quit, font=FONT_BIG),
        ]

        # Happy-Faces vorbereiten
        self.game.assets.load_happy_images(max_height=max(60, int(sh * 0.30)))

    def on_start(self):
        from game.scenes.play_scene import PlayScene
        self.game.scene_manager.replace(PlayScene(self.game))
        self.game.audio.play_game_music()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.on_start()
        for b in self.buttons:
            b.handle_event(event)

    def draw(self, screen):
        screen.fill(WHITE)
        # Titel oben links
        title = FONT_BIG.render(config.TITLE_TEXT, True, MAGENTA)
        screen.blit(title, (16, 16))

        # Happy-Faces unten rechts in Reihe
        imgs = self.game.assets.happy_images
        if imgs:
            gap = 12
            bottom_pad, right_pad = 16, 16
            total_w = sum(i.get_width() for i in imgs) + gap * (len(imgs) - 1)
            row_h = max(i.get_height() for i in imgs)
            x = self.game.width - right_pad - total_w
            y = self.game.height - bottom_pad - row_h
            for i in imgs:
                screen.blit(i, (x, y))
                x += i.get_width() + gap

        # Buttons
        for b in self.buttons:
            b.draw(screen)
