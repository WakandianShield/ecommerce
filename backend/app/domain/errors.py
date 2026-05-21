class DomainError(Exception):
    pass


class NotFoundError(DomainError):
    pass


class ValidationError(DomainError):
    pass


class AuthError(DomainError):
    pass
