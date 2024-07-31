class ParserFindTextException(Exception):
    """Вызывается, когда парсер не может найти текст в теге."""
    pass


class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class ParserFindAllTagsException(ParserFindTagException):
    pass
