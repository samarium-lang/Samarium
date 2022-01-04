class NotDefinedError(Exception):
    def __init__(self, class_, message: str):
        super().__init__(f"{class_.__class__.__name__}.{message}")


class SamariumError(Exception):
    pass


class SamariumImportError(SamariumError):
    pass


class SamariumSyntaxError(SamariumError):
    pass


class SamariumTypeError(SamariumError):
    pass
