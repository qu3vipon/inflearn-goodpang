### Section 4 - 상품 구매 
1. 주문(Order) 모델링
```python
class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class Order(models.Model):
    user = models.ForeignKey("user.ServiceUser", on_delete=models.CASCADE, related_name="orders")
    total_price = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=8, default=OrderStatus.PENDING)  # pending | paid | cancelled
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
```
2. PG(Payment Gateway) 연동 이해하기
  - [토스 페이먼츠 문서](https://docs.tosspayments.com/guides/basics/payment#%EA%B2%B0%EC%A0%9C-%EA%B8%B0%EC%B4%88)
  - PG로부터 결제 결과를 확인하는 방법
    1. 결제 승인 요청(사용자 -> 서버 -> PG)
    2. 콜백(callback) 수신(PG -> 서버)
3. 결제 승인 요청시 동시성 문제
  - 동시성 문제: 다수의 프로세스(또는 스레드)에서 공유 자원에 동시에 접근하여 결과를 예측할 수 없는 상태를 만들어는 문제 
  - 결제 완료는 반드시 한 번만 처리되어야 한다고 가정(결제 완료되면 이메일 발송)
  - 동시성 문제가 발생하는 경우
    - 사용자 결제 승인 요청과 콜백 요청이 동시에 발생
    - 동일한 요청이 여러번 발생(예: 사용자가 클릭 여러번)
4. Compare-and-Swap
  - 동시성 처리할 때 사용하는 기술 
  - 동작 방식: 값을 비교(compare)하고, 현재 값이 예상과 일치하면 새로운 값으로 교체(swap)한다
```python
class OrderAlreadyPaidException(Exception):
    message = "Order Already Paid Exception"

with transaction.atomic():
    success: int = Order.objects.filter(id=order_id, status=OrderStatus.PENDING).update(status=OrderStatus.PAID)
    if not success:
        raise OrderAlreadyPaidException
```
4. 저스틴 비버 문제 해결하기
- Denormalized counter
  - 인스타그램: 저스틴 비버와 같은 유명인의 follower 수를 보여줄 때, 많은 부하 발생(GROUP BY 연산)
  - 별도의 couter 컬럼을 추가하여 문제 해결 
```python
class ServiceUser(models.Model):
    # ...
    order_count = models.PositiveIntegerField(default=0)

ServiceUser.objects.filter(id=request.user.id).update(order_count=F("order_count") + 1)
``` 
