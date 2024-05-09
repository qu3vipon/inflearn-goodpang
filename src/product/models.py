from enum import StrEnum

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"


class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=8)  # active | inactive | paused
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    tags = models.CharField(max_length=128, blank=True)
    search_vector = SearchVectorField(null=True)

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
            GinIndex(fields=["search_vector"]),
        ]


class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="children"
    )

    class Meta:
        app_label = "product"
        db_table = "category"


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(models.Model):
    user = models.ForeignKey(
        "user.ServiceUser", on_delete=models.CASCADE, related_name="orders"
    )
    total_price = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=8, default=OrderStatus.PENDING
    )  # pending | paid | cancelled
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "product"
        db_table = "order"
        indexes = [
            models.Index(fields=["user", "status"]),
        ]


class OrderLine(models.Model):
    product = models.ForeignKey("Product", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()
    discount_ratio = models.FloatField(default=1)

    class Meta:
        app_label = "product"
        db_table = "order_line"
