### Section 1 - Django Ninja 알아보기
1. 프로젝트 세팅
```shell
# python 가상환경 설정
$ pyenv virtualenv 3.11.8 goodpang
$ pyenv local goodpang

# package 설치
$ pip install -r ../requirements-dev.txt

# ruff(linter & formatter)
$ pre-commit install

# django 프로젝트 시작
$ django-admin startproject shared . 

# postgresql(docker) 시작
$ docker-compose -f ../docker-compose.db.local.yml up --build -d
``` 
2. DB 설정 & User 모델 추가
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "goodpang",
        "USER": "goodpang",
        "PASSWORD": "goodpang",
        "HOST": "127.0.0.1",
        "PORT": "5433",
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

class ServiceUser(models.Model):
    email = models.EmailField()
    
    class Meta:
        app_label = "user"
        db_table = "service_user"
        constraints = [
            models.UniqueConstraint(fields=["email"], name="unique_email"),
        ]
```
3. Health Check API 만들기
```python
base_api = NinjaAPI(title="Goodpang", version="0.0.0")

@base_api.get("")
def health_check_handler(request):
    return {"ping": "pong"}

urlpatterns = [
    path("", base_api.urls),
    path("admin/", admin.site.urls),
]
```
4. Authentication(JWT)
```python
class NotAuthorizedException(Exception):
    message = "Not Authorized" 

class UserNotFoundException(Exception):
    message = "User Not Found"

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
            {"user_id": user_id, "exp": self._unix_timestamp(seconds_in_future=24 * 60 * 60)}, self.JWT_SECRET_KEY, algorithm=self.JWT_ALGORITHM
        )

    def verify_token(self, jwt_token: str) -> int:
        try:
            payload: JWTPayload = jwt.decode(jwt_token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM])
            user_id: int = payload["user_id"]
            exp: int = payload["exp"]
        except Exception:  # noqa
            raise NotAuthorizedException
        
        if exp < self._unix_timestamp(seconds_in_future=0):
            raise NotAuthorizedException
        return user_id
    
authentication_service = AuthenticationService()

class BearerAuth(HttpBearer):
    def authenticate(self, request, token) -> user_id:
        user_id: int = authentication_service.verify_token(jwt_token=token)
        if not (user := ServiceUser.objects.get(id=user_id)):
            raise UserNotFoundException
        request.user = user
        return token

bearer_auth = BearerAuth()
    
@base_api.get("/auth-test", auth=bearer_auth)
def auth-test(request):
    return {
        "token": request.auth,
        "user": request.user,
    }
```
5. Exception Handler
```python
@base_api.exception_handler(NotAuthorizedException)
def not_authorized_exception(request, exc):
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )
```
6. 응답 형식 정의
```python
T = TypeVar("T")

def response(results: dict | list | Schema) -> dict:
    return {"results": results}

def error_response(msg: str) -> dict:
    return {"results": {"message": msg}}

class ObjectResponse(Schema, Generic[T]):
    results: T

class ErrorResponse(Schema):
    message: str

class OkResponse(Schema):
    detail: str = "ok"
```
