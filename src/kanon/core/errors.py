class KanonError(Exception):
    pass

class KanonValueError(ValueError, KanonError):
    pass

class KanonRuntimeError(RuntimeError, KanonError):
    pass

class KanonKeyError(KeyError, KanonError):
    pass
