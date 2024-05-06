import time
from typing import TypedDict, ClassVar

import jwt
from django.conf import settings
from ninja.security import HttpBearer

from user.exceptions import NotAuthorizedException, UserNotFoundException
from user.models import ServiceUser


class JWTPayload(TypedDict):
    user_id: int
    exp: int


class AuthenticationService:
    JWT_SECRET_KEY: ClassVar[str] = settings.SECRET_KEY
    JWT_ALGORITHM: ClassVar[str] = "HS256"

    @staticmethod
    def _unix_timestamp(seconds_in_future: int) -> int:
        return int(time.time()) + seconds_in_future

    def encode_token(self, user_id: int) -> str:
        return jwt.encode(
            {
                "user_id": user_id,
                "exp": self._unix_timestamp(seconds_in_future=24 * 60 * 60),
            },
            self.JWT_SECRET_KEY,
            algorithm=self.JWT_ALGORITHM,
        )

    def verify_token(self, jwt_token: str) -> int:
        try:
            payload: JWTPayload = jwt.decode(
                jwt_token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM]
            )
            user_id: int = payload["user_id"]
            exp: int = payload["exp"]
        except Exception:  # noqa
            raise NotAuthorizedException

        if exp < self._unix_timestamp(seconds_in_future=0):
            raise NotAuthorizedException
        return user_id


authentication_service = AuthenticationService()


class BearerAuth(HttpBearer):
    def authenticate(self, request, token) -> str:
        user_id: int = authentication_service.verify_token(jwt_token=token)
        if not (user := ServiceUser.objects.filter(id=user_id).first()):
            raise UserNotFoundException
        request.user = user
        return token


bearer_auth = BearerAuth()
