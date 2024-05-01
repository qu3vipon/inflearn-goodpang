### Chapter 1
1. 프로젝트 세팅
```shell
# ruff(linter & formatter)
$ pre-commit install

# python 가상환경 설정
$ pyenv virtualenv 3.11.8 goodpang
$ pyenv local goodpang

# package 설치
$ pip install -r requirements-dev.txt

# django 프로젝트 시작
$ django-admin startproject shared . 

# postgresql(docker) 시작
$ docker-compose -f ../docker-compose.db.local.yml up --build -d
```
2. HelloWorld API 만들기
3. Exception Handler 설정 
4. User 모델 추가 & DB 설정
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
```
5. Authentication(JWT) 설정
