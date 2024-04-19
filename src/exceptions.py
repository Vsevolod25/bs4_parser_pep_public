class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class LatestVersionsMissingException(Exception):
    """Вызывается, когда парсер не может найти список последних версий."""
    pass
