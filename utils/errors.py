class IncorrectCommandName(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotFound(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
