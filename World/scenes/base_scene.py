class BaseScene:
    def update(self, dt: float) -> None:
        raise NotImplementedError

    def draw(self, screen) -> None:
        raise NotImplementedError

    def handle_event(self, event) -> None:
        raise NotImplementedError
