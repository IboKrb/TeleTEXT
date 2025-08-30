# game/scene_manager.py
class SceneManager:
    def __init__(self, start_scene):
        self.stack = [start_scene]

    def current(self):
        return self.stack[-1]

    def handle_event(self, event):
        self.current().handle_event(event)

    def update(self, dt):
        self.current().update(dt)

    def draw(self, screen):
        self.current().draw(screen)

    def push(self, scene):
        self.stack.append(scene)

    def pop(self):
        self.stack.pop()

    def replace(self, scene):
        self.stack[-1] = scene
