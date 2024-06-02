from typing import List, TypedDict

from django.contrib.postgres.search import SearchQuery

from product.models import Product, ProductStatus


class ProductValues(TypedDict):
    id: int
    name: str
    price: int


class ProductService:
    @staticmethod
    def search_by_query(self, query: str) -> List[ProductValues]:
        return Product.objects.filter(
            search_vector=SearchQuery(query), status=ProductStatus.ACTIVE
        ).values("id", "name", "price")

    @staticmethod
    def filter_by_category_ids(category_ids: List[int]) -> List[ProductValues]:
        return Product.objects.filter(
            category_id__in=category_ids, status=ProductStatus.ACTIVE
        ).values("id", "name", "price")

    @staticmethod
    def all_products() -> List[ProductValues]:
        return Product.objects.filter(status=ProductStatus.ACTIVE).values(
            "id", "name", "price"
        )

    @staticmethod
    def filter_by_ids(product_ids: List[int]) -> List[Product]:
        return Product.objects.filter(id__in=product_ids, status=ProductStatus.ACTIVE)


product_service = ProductService()
