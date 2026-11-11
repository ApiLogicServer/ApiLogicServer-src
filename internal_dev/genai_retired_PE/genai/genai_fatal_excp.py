class GenAIException(BaseException):
    """Raise when unable to create db_models (missing Base, reserved word)"""

    def __init__(self, message):
        self.message = message