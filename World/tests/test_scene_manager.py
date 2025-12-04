import pygame
from scene_manager import SceneManager


class DummyScene:
    def __init__(self):
        self.updated = False
        self.drawn = False
        self.event_handled = False

    def update(self, dt):
        self.updated = True

    def draw(self, screen):
        self.drawn = True

    def handle_event(self, event):
        self.event_handled = True


def test_push_and_current():
    manager = SceneManager()
    s1 = DummyScene()
    manager.push(s1)
    assert manager.current() is s1


def test_pop_removes_scene():
    manager = SceneManager()
    s1 = DummyScene()
    manager.push(s1)
    manager.pop()
    assert manager.current() is None


def test_replace():
    manager = SceneManager()
    s1 = DummyScene()
    s2 = DummyScene()
    manager.push(s1)
    manager.replace(s2)
    assert manager.current() is s2


def test_update_dispatch():
    manager = SceneManager()
    s1 = DummyScene()
    manager.push(s1)
    manager.update(0.016)
    assert s1.updated


def test_draw_dispatch():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    manager = SceneManager()
    s1 = DummyScene()
    manager.push(s1)
    screen = pygame.display.get_surface()
    manager.draw(screen)
    assert s1.drawn


def test_event_dispatch():
    pygame.display.init()
    pygame.display.set_mode((1, 1))
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_x)
    manager = SceneManager()
    s1 = DummyScene()
    manager.push(s1)
    manager.handle_event(event)
    assert s1.event_handled
