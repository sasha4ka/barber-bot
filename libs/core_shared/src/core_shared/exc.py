class SlotAlreadyBookedException(Exception):
    pass


class SlotNotFoundException(Exception):
    pass


class UserNotFound(Exception):
    pass


class JWTAuthenticationError(Exception):
    pass


class PasswordAuthenticationError(Exception):
    pass
