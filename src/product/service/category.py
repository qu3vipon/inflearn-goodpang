from typing import List

from product.models import Category


class CategoryService:
    @staticmethod
    def get_category_by_id(category_id: int) -> Category | None:
        return Category.objects.filter(id=category_id).first()

    @staticmethod
    def get_parent_categories_with_children() -> List[Category]:
        return Category.objects.filter(parent=None).prefetch_related("children")


category_service = CategoryService()
