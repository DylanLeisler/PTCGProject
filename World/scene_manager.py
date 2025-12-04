class SceneManager:
    def __init__(self):
        self.scenes = []

    def push(self, scene):
        self.scenes.append(scene)

    def pop(self):
        if self.scenes:
            self.scenes.pop()

    def replace(self, scene):
        if self.scenes:
            self.scenes.pop()
        self.scenes.append(scene)

    def current(self):
        return self.scenes[-1] if self.scenes else None

    def update(self, dt):
        scene = self.current()
        if scene:
            scene.update(dt)

    def draw(self, screen):
        scene = self.current()
        if scene:
            scene.draw(screen)

    def handle_event(self, event):
        scene = self.current()
        if scene:
            scene.handle_event(event)
