from typing import List

from django.http import HttpRequest
from ninja import Router

from product.models import Product, ProductStatus, Category
from product.reponse import ProductListResponse, CategoryListResponse
from shared.response import ObjectResponse, response

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
        products = Product.objects.filter(name__contains=query)[:100]
    elif category_id:
        category: Category | None = Category.objects.filter(id=category_id).first()
        if not category:
            products = []
        else:
            category_ids: List[int] = [category.id] + list(
                category.children.values_list("id", flat=True)
            )
            products = Product.objects.filter(
                category_id__in=category_ids, status=ProductStatus.ACTIVE
            ).values("id", "name", "price")
    else:
        products = Product.objects.filter(status=ProductStatus.ACTIVE).values(
            "id", "name", "price"
        )

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
            categories=Category.objects.filter(parent=None).prefetch_related("children")
        )
    )
