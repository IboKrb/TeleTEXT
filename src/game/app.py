# game/app.py
import pygame
from systems import config
from game.scene_manager import SceneManager
from game.scenes.start_scene import StartScene
from models.setup import Setup             # vorerst aus deinem bestehenden Setup
from audio import Audio               # dein vorhandener Audio-Manager
from systems.assets import Assets
import os

print("[PATHS]")
print("ASSETS_DIR:", config.ASSETS_DIR)
print("AUDIO_DIR :", config.AUDIO_DIR, "exists:", os.path.isdir(config.AUDIO_DIR))
print("ROOMS_DIR :", config.ROOMS_DIR, "exists:", os.path.isdir(config.ROOMS_DIR))
print("PEOPLE_DIR:", config.PEOPLE_DIR, "exists:", os.path.isdir(config.PEOPLE_DIR))


class Game:
    def __init__(self):
        # Window / Fullscreen
        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.width, self.height = self.screen.get_size()
        else:
            self.screen = pygame.display.set_mode(config.WINDOW_SIZE)
            self.width, self.height = config.WINDOW_SIZE
        pygame.display.set_caption("TeleTEXT")

        # Systems
        self.music_volume = 5
        self.sfx_volume = 5

        self.audio = Audio(
            audio_dir=config.AUDIO_DIR,
            menu_track="menu",
            game_track="game",
            default_music_volume=self.music_volume,
            default_sfx_volume=self.sfx_volume,
            logger=lambda m: print(m)  # kann in StartScene/PlayScene auch in TextLog gehen
        )
        self.assets = Assets(logger=lambda m: print(m))

        # Datenfabrik
        self.setup = Setup()

        # Scenes
        self.scene_manager = SceneManager(StartScene(self))

        # Loop
        self.clock = pygame.time.Clock()
        self.running = True

    def quit(self):
        try:
            self.audio.stop_music(300)
        except Exception:
            pass
        self.running = False

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.scene_manager.handle_event(event)
            self.scene_manager.update(dt)
            self.scene_manager.draw(self.screen)
            pygame.display.flip()
