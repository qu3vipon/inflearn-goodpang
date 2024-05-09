from typing import List, Dict

from ninja import Schema


class OrderLineRequest(Schema):
    product_id: int
    quantity: int


class OrderRequestBody(Schema):
    order_lines: List[OrderLineRequest]

    @property
    def product_id_to_quantity(self) -> Dict[int, int]:
        return {
            order_line.product_id: order_line.quantity
            for order_line in self.order_lines
        }


class OrderPaymentConfirmRequestBody(Schema):
    payment_key: str  # pg 고유 key
