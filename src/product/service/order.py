from typing import List, Dict

from django.db import transaction
from django.db.models import F

from product.exceptions import OrderAlreadyPaidException
from product.models import Product, Order, OrderLine, OrderStatus
from user.exceptions import UserPointsNotEnoughException, UserVersionConflictException
from user.models import ServiceUser, UserPointsHistory, UserPoints


class OrderService:
    @staticmethod
    @transaction.atomic
    def create_order(
        user: ServiceUser,
        products: List[Product],
        product_id_to_quantity: Dict[int, int],
    ) -> Order:
        total_price: int = 0
        order = Order.objects.create(user=user)

        order_lines_to_create: List[OrderLine] = []
        for product in products:
            price: int = product.price
            discount_ratio: float = 0.9
            quantity: int = product_id_to_quantity[product.id]

            order_lines_to_create.append(
                OrderLine(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price,
                    discount_ratio=discount_ratio,
                )
            )

            total_price += price * quantity * discount_ratio

        order.total_price = int(total_price)
        order.save()
        OrderLine.objects.bulk_create(objs=order_lines_to_create)
        return order

    @staticmethod
    @transaction.atomic
    def confirm_order(user_id: int, order: Order) -> None:
        success: int = Order.objects.filter(
            id=order.id, status=OrderStatus.PENDING
        ).update(status=OrderStatus.PAID)
        if not success:
            raise OrderAlreadyPaidException

        user = ServiceUser.objects.get(id=user_id)
        if user.points < order.total_price:
            raise UserPointsNotEnoughException

        success: int = ServiceUser.objects.filter(
            id=user_id, version=user.version
        ).update(
            points=F("points") - order.total_price,
            order_count=F("order_count") + 1,
            version=user.version + 1,
        )

        if not success:
            raise UserVersionConflictException

        UserPointsHistory.objects.create(
            user=user,
            points_change=-order.total_price,
            reason=f"orders:{order.id}:confirm",
        )

    @staticmethod
    @transaction.atomic
    def confirm_order_v2(user_id: int, order: Order) -> None:
        success: int = Order.objects.filter(
            id=order.id, status=OrderStatus.PENDING
        ).update(status=OrderStatus.PAID)
        if not success:
            raise OrderAlreadyPaidException

        last_points = (
            UserPoints.objects.filter(user_id=user_id).order_by("-version").first()
        )
        if last_points.points_sum < order.total_price:
            raise UserPointsNotEnoughException

        UserPoints.objects.create(
            user_id=user_id,
            version=last_points.version + 1,
            points_change=-order.total_price,
            points_sum=last_points.points_sum - order.total_price,
            reason=f"orders:{order.id}:confirm",
        )

        if not success:
            raise UserVersionConflictException

        ServiceUser.objects.filter(id=user_id).update(order_count=F("order_count") + 1)


order_service = OrderService()
