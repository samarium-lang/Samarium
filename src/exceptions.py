class NotDefinedError(Exception):
    def __init__(self, class_, message: str):
        self.class_ = class_.__class__.__name__
        super().__init__(f"{self.class_}.{message}")


class SamariumError(Exception):
    pass


class SamariumImportError(SamariumError):
    pass


class SamariumSyntaxError(SamariumError):
    pass


class SamariumTypeError(SamariumError):
    pass


class SamariumTokenError(SamariumError):
    pass
