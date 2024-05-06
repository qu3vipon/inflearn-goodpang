from ninja import Schema


class UserTokenResponse(Schema):
    token: str
