from typing import List, Dict

from django.http import HttpRequest
from ninja import Router

from product.exceptions import (
    OrderInvalidProductException,
    OrderNotFoundException,
    OrderAlreadyPaidException,
)
from product.models import (
    Product,
    Category,
    Order,
)
from product.reponse import (
    ProductListResponse,
    CategoryListResponse,
    OrderDetailResponse,
)
from product.request import OrderRequestBody
from product.service.category import category_service
from product.service.order import order_service
from product.service.product import product_service, ProductValues
from shared.response import (
    ObjectResponse,
    response,
    error_response,
    ErrorResponse,
    OkResponse,
)
from user.authentication import bearer_auth, AuthRequest
from user.exceptions import UserPointsNotEnoughException, UserVersionConflictException

router = Router(tags=["Products"])


@router.get(
    "",
    response={
        200: ObjectResponse[ProductListResponse],
    },
)
def product_list_handler(
    request: HttpRequest, category_id: int | None = None, query: str | None = None
):
    if query:
        products: List[ProductValues] = product_service.search_by_query(query=query)
    elif category_id:
        category: Category | None = category_service.get_category_by_id(
            category_id=category_id
        )
        if not category:
            products = []
        else:
            category_ids: List[int] = [category.id] + list(
                category.children.values_list("id", flat=True)
            )
            products = product_service.filter_by_category_ids(category_ids=category_ids)
    else:
        products = product_service.all_products()

    return 200, response(ProductListResponse(products=products))


@router.get(
    "/categories",
    response={
        200: ObjectResponse[CategoryListResponse],
    },
)
def categories_list_handler(request: HttpRequest):
    return 200, response(
        CategoryListResponse.build(
            categories=category_service.get_parent_categories_with_children()
        )
    )


@router.post(
    "/orders",
    response={
        201: ObjectResponse[OrderDetailResponse],
        400: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def order_products_handler(request: AuthRequest, body: OrderRequestBody):
    product_id_to_quantity: Dict[int, int] = body.product_id_to_quantity
    products: List[Product] = product_service.filter_by_ids(
        product_ids=product_id_to_quantity
    )
    if len(products) != len(product_id_to_quantity):
        return 400, error_response(msg=OrderInvalidProductException.message)

    order: Order = order_service.create_order(
        user=request.user,
        products=products,
        product_id_to_quantity=product_id_to_quantity,
    )
    return 201, response({"id": order.id, "total_price": order.total_price})


@router.post(
    "/orders/{order_id}/confirm",
    response={
        200: ObjectResponse[OkResponse],
        400: ObjectResponse[ErrorResponse],
        404: ObjectResponse[ErrorResponse],
        409: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def confirm_order_payment_handler(request: AuthRequest, order_id: int):
    if not (order := Order.objects.filter(id=order_id, user=request.user).first()):
        return 404, error_response(msg=OrderNotFoundException.message)

    try:
        order_service.confirm_order(user_id=request.user.id, order=order)
    except OrderAlreadyPaidException as e:
        return 400, error_response(msg=e.message)
    except UserPointsNotEnoughException as e:
        return 409, error_response(msg=e.message)
    except UserVersionConflictException as e:
        return 409, error_response(msg=e.message)

    return 200, response(OkResponse())


@router.post(
    "/orders/{order_id}/confirm-v2",
    response={
        200: ObjectResponse[OkResponse],
        400: ObjectResponse[ErrorResponse],
        404: ObjectResponse[ErrorResponse],
        409: ObjectResponse[ErrorResponse],
    },
    auth=bearer_auth,
)
def confirm_order_payment_handler_v2(request: AuthRequest, order_id: int):
    if not (order := Order.objects.filter(id=order_id, user=request.user).first()):
        return 404, error_response(msg=OrderNotFoundException.message)

    try:
        order_service.confirm_order_v2(user_id=request.user.id, order=order)
    except OrderAlreadyPaidException as e:
        return 400, error_response(msg=e.message)
    except UserPointsNotEnoughException as e:
        return 409, error_response(msg=e.message)
    except UserVersionConflictException as e:
        return 409, error_response(msg=e.message)

    return 200, response(OkResponse())
