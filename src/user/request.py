from ninja import Schema


class UserLoginRequestBody(Schema):
    email: str
