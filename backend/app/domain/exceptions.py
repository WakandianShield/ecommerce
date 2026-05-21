class DomainException(Exception):
    pass


class ProfileNotFound(DomainException):
    pass


class ProfileAlreadyExists(DomainException):
    pass


class InvalidCredentials(DomainException):
    pass


class ProductNotFound(DomainException):
    pass


class OrderNotFound(DomainException):
    pass


class Unauthorized(DomainException):
    pass


class InsufficientStock(DomainException):
    pass
