class NotAuthorizedException(Exception):
    message = "Not Authorized"


class UserNotFoundException(Exception):
    message = "User Not Found"


class UserPointsNotEnoughException(Exception):
    message = "User Points Not Enough"


class UserVersionConflictException(Exception):
    message = "User Version Conflict"
