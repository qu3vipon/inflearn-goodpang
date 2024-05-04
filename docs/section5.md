### Section 5 - 포인트 시스템
1. 비관적 락(pessmistic locking)
- 데이터베이스 락을 잡고 동시성을 제어하는 방법
- 비교적 구현이 쉽고 안전하게 데이터 정합성이 보장되지만, 락으로 인해 다른 작업이 영향을 받을 수 있고, 데드락(Deadlock)이 발생할 수 있음
  - 데드락: 두 개 이상의 작업이 서로 작업이 끝나기 만을 기다리고 있고 결과적으로 아무것도 완료되지 못하는 상태(=교착상태) 
```python
class ServiceUser(models.Model):
    points = models.PositiveIntegerField(default=0)

class UserPointsNotEnoughException(Exception):
    message = "User Points Not Enough"
    
with transaction.atomic():
    # ...
    user = ServiceUser.objects.select_for_update().get(id=user_id)
    if user.points < total_price:
        raise UserPointsNotEnoughException
    user.points -= total_price
    user.save()
```
2. 낙관적 락(optimistic locking)
- 데이터베이스 락을 잡지 않고, unique index와 추가 컬럼을 통해 동시성을 제어하는 방법
- 락을 잡지 않기 때문에 비관적 락에 비해 성능 저하가 적지만, 어플리케이션의 복잡도가 증가하고, 충돌 발생시 실패한 요청에 대한 처리가 필요함
```python
class ServiceUser(models.Model):
    # ...
    version = models.PositiveIntegerField(default=0)

    constraints = [
        models.UniqueConstraint(fields=["version"], name="unique_version"),
    ]
    
class UserVersionConflictException(Exception):
    message = "User Version Conflict"

with transaction.atomic():
    # ...
    user = ServiceUser.objects.get(id=user_id)
    if user.points < total_price:
        raise UserPointsNotEnoughException
    success: int = ServiceUser.objects.filter(id=user_id, version=user.version).update(
      points=points - total_price,
      version=user.version + 1
    )
    if not success:
        raise UserVersionConflictException
```
3. Unique 제약 응용(timestamp)
- 주문을 사용자 별로 초당 한 번씩만 생성할 수 있게 만들기
```python
class ServiceUser(models.Model):
    # ...
  
    def create_order_code(self) -> str:
        return datetime.utcnow().strftime("%Y%m%d-%H%M%S") + f"-{self.id}"


class Order(models.Model):
    order_code = models.CharField(max_length=32, default="")

    constraints = [
        models.UniqueConstraint(fields=["order_code"], name="unique_order_code"),
    ]
```
4. 포인트 히스토리 관리 1(SCD type4)
- [Slowly Changing Dimension](https://en.wikipedia.org/wiki/Slowly_changing_dimension)
  - 일정하지 않게 변경되는 기록을 관리하기 위한 테이블 모델링 기법 
- type4: 원본과 별도의 히스토리 테이블 추가
  - 장점: JOIN 없이 곧바로 최종 결과 값 확인
  - 단점: 중간 값 계산이 어려움(GROUP BY)
```python
class UserPointsHistory(models.Model):
    user = models.ForeignKey(ServiceUser, on_delete=models.CASCADE, related_name="points")
    points_change = models.IntegerField(default=0)
    reason = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user"
        db_table = "user_points_history"
```
5. 포인트 히스토리 관리 2(SCD type2 + type3)
- type2 + type3: 변경 내역마다 새로운 레코드 추가 + 컬럼 추가하여 기록 관리
  - 장점: 중간 히스토리 파악이 용이 
  - 단점: 최종값 조회시 JOIN 발생
```python
class UserPoints(models.Model):
    user = models.ForeignKey(ServiceUser, on_delete=models.CASCADE, related_name="points")
    version = models.PositiveIntegerField(default=0)
    points_change = models.IntegerField(default=0)
    points_sum = models.PositiveIntegerField(default=0)
    reason = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "user"
        db_table = "user_points"
        constraints = [
            models.UniqueConstraint(fields=["user", "version"], name="unique_user_version"),
        ]

# 최종 포인트 확인
last_points = UserPoints.objects.filter(user_id=user_id).order_by("-version").first()

points = UserPoints.objects.filter(user_id=OuterRef("pk")).order_by("-version").values("points_sum")
user = ServiceUser.objects.annotate(points=Subquery(points[:1])).get(id=user_id)
```
