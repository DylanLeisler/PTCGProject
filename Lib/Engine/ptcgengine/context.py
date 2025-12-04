class EffectContext:
    """Holds temporary scope during effect evaluation."""
    def __init__(self, controller):
        self.controller = controller
        self.vars = {}
