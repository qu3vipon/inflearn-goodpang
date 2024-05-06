from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI

from user.exceptions import NotAuthorizedException, UserNotFoundException
from user.urls import router as user_router
from product.urls import router as product_router

base_api = NinjaAPI(title="Goodpang", version="0.0.0")

base_api.add_router("users", user_router)
base_api.add_router("products", product_router)


@base_api.get("")
def health_check_handler(request):
    return {"ping": "pong"}


@base_api.exception_handler(NotAuthorizedException)
def not_authorized_exception(request, exc):
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=401,
    )


@base_api.exception_handler(UserNotFoundException)
def user_not_found_exception(request, exc):
    return base_api.create_response(
        request,
        {"results": {"message": exc.message}},
        status=404,
    )


urlpatterns = [
    path("", base_api.urls),
    path("admin/", admin.site.urls),
]
