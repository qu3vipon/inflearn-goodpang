from typing import TypeVar, Generic

from ninja import Schema

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
