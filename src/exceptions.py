class NotDefinedError(Exception):
    def __init__(self, class_, message: str):
        self.class_ = class_.__class__.__name__
        super().__init__(f"{self.class_}.{message}")


class SamariumError(Exception):
    blank = ""
    prefix = ""

    def __init__(self, message: str):
        super().__init__(f"{self.prefix}{message}" or self.blank)


class SamariumImportError(SamariumError):
    blank = "Import error"
    prefix = "Invalid module: "


class SamariumSyntaxError(SamariumError):
    blank = "Invalid syntax"
    prefix = "Unsupported character: "


class SamariumTypeError(SamariumError):
    blank = "Invalid type"
    prefix = "Unsupported type: "
