### Section 2 - 상품 노출
1. 상품(Product) 모델링
- boolean 보다 enum
```python
class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    
class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.PositiveIntegerField()
    # is_active = models.BooleanField(default=False)
    status = models.CharField(max_length=8)  # active | inactive | paused

    class Meta:
        app_label = "product"
        db_table = "product"
        indexes = [
            models.Index(fields=["status", "price"]),
        ]
```
2. Index란?
- 검색 속도를 향상시키기 위해 사용되는 자료구조
- 특정 열(또는 열 조합)에 대한 정렬된 데이터를 유지하고, **빠른 데이터 검색** 및 **정렬**에 활용 
- 좋은 index 설계를 위해서는 데이터가 조회되는 쿼리 패턴을 분석해야 한다.
4. 카테고리(Category) 모델링
- self join
```python
class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name="children")
    
    class Meta:
        app_label = "product"
        db_table = "category"
```
- select_related()
  - N:1 관계에서 사용
  - JOIN 쿼리
  - eager loading -> N+1 문제 해결
- prefetch_related()
  - 1:N 관계에서 사용
  - 추가 쿼리(batch 쿼리)
  - eager loading -> N+1 문제 해결
  - n depth 쿼리
