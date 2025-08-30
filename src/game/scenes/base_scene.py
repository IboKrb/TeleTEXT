# game/scenes/base_scene.py
class Scene:
    def __init__(self, game):
        self.game = game  # Zugriff auf game.audio, game.assets, game.config, game.ui etc.

    def handle_event(self, event): pass
    def update(self, dt): pass
    def draw(self, screen): pass
