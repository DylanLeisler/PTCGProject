class EngineError(Exception):
    pass

class SelectorError(EngineError):
    pass

class ExpressionError(EngineError):
    pass

class PrimitiveError(EngineError):
    pass

class InterpreterError(EngineError):
    pass
