class NotAuthorizedException(Exception):
    message = "Not Authorized"


class UserNotFoundException(Exception):
    message = "User Not Found"
