# game/scenes/pause_menu.py
import pygame
from game.scenes.base_scene import Scene
from ui import Button, Slider, FONT, FONT_BIG, WHITE, BLACK

class PauseMenu(Scene):
    def __init__(self, game):
        super().__init__(game)
        # quadratisches Popup mittig
        side = int(min(self.game.width, self.game.height) * 0.55)
        x = (self.game.width - side) // 2
        y = (self.game.height - side) // 2
        self.rect = pygame.Rect(x, y, side, side)

        pad = 24
        inner = pygame.Rect(self.rect.x + pad, self.rect.y + pad,
                            self.rect.width - 2*pad, self.rect.height - 2*pad)

        self.buttons = []
        self.sliders = []

        title_h = FONT_BIG.get_height() + 12
        content_top = inner.y + title_h
        content_bot = inner.bottom

        btn_h = 56
        label_h = FONT.get_height()
        slider_h = 40
        label_space = 6

        total_controls_h = (
            btn_h + (label_h + label_space + slider_h) + (label_h + label_space + slider_h) + btn_h
        )
        avail_h = content_bot - content_top
        gap = max(12, (avail_h - total_controls_h) // 5)
        y_ptr = content_top + gap

        # Fortfahren
        cont_rect = pygame.Rect(inner.x, y_ptr, inner.width, btn_h)
        self.buttons.append(Button(cont_rect, "Fortfahren", self.on_continue, font=FONT_BIG))
        y_ptr += btn_h + gap

        # SFX
        self.sfx_label_y = y_ptr
        y_ptr += label_h + label_space
        sfx_slider_rect = pygame.Rect(inner.x, y_ptr, inner.width - 48, slider_h)
        self.sliders.append(Slider(sfx_slider_rect, 0, 10, self.game.sfx_volume,
                                   on_change=self.on_sfx_change))
        y_ptr += slider_h + gap

        # Musik
        self.music_label_y = y_ptr
        y_ptr += label_h + label_space
        music_slider_rect = pygame.Rect(inner.x, y_ptr, inner.width - 48, slider_h)
        self.sliders.append(Slider(music_slider_rect, 0, 10, self.game.music_volume,
                                   on_change=self.on_music_change))
        y_ptr += slider_h + gap

        # Spiel beenden
        quit_rect = pygame.Rect(inner.x, y_ptr, inner.width, btn_h)
        self.buttons.append(Button(quit_rect, "Spiel beenden", self.game.quit, font=FONT_BIG))

    def on_continue(self):
        self.game.scene_manager.pop()  # zurück zur PlayScene

    def on_sfx_change(self, v: int):
        self.game.sfx_volume = v
        self.game.audio.set_sfx_volume_0_10(v)

    def on_music_change(self, v: int):
        self.game.music_volume = v
        self.game.audio.set_music_volume_0_10(v)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.on_continue()
            return
        for b in self.buttons: b.handle_event(event)
        for s in self.sliders: s.handle_event(event)

    def draw(self, screen):
        # dunkles Overlay
        overlay = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        # Popup
        pygame.draw.rect(screen, WHITE, self.rect, border_radius=20)
        pygame.draw.rect(screen, BLACK, self.rect, 3, border_radius=20)

        title = FONT_BIG.render("Menü", True, BLACK)
        screen.blit(title, title.get_rect(midtop=(self.rect.centerx, self.rect.y + 14)))

        pad = 24
        screen.blit(FONT.render("SFX Lautstärke", True, BLACK), (self.rect.x + pad, self.sfx_label_y))
        screen.blit(FONT.render("Musik Lautstärke", True, BLACK), (self.rect.x + pad, self.music_label_y))

        for s in self.sliders: s.draw(screen)
        for b in self.buttons: b.draw(screen)
