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

class ProductDetailResponse(Schema):
    id: int
    name: str
    price: int

class ProductListResponse(Schema):
    products: List[ProductDetailResponse]

router = Router(tags=["Products"])

@router.get(
    "",
    response={
        200: ObjectResponse[ProductListResponse],
    },
)
def product_list_handler(request: HttpRequest):
    return 200, response(
        ProductListResponse(products=Product.objects.filter(status=ProductStatus.ACTIVE).values("id", "name", "price"))
    )

# tests/test_product_api
@pytest.mark.django_db
def test_get_product_list(api_client):
    # given
    Product.objects.create(name="청바지", price=1, status="active")

    # when
    response = api_client.get("/products")

    # then
    assert response.status_code == 200
    assert len(response.json()["results"]["products"]) == 1
    assert Schema(
        {
            "results": {
                "products": [
                    {"id": int, "name": "청바지", "price": 1}
                ]
            }
        }
    ).validate(response.json())
```
2. Index란?
- 검색 속도를 향상시키기 위해 사용되는 자료구조
- 특정 열(또는 열 조합)에 대한 정렬된 데이터를 유지하고, **빠른 데이터 검색** 및 **정렬**에 활용 
- 좋은 index 설계를 위해서는 데이터가 조회되는 쿼리 패턴을 분석해야 한다.
3. 카테고리(Category) 모델링
- self join
```python
class Category(models.Model):
    name = models.CharField(max_length=32)
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="children")
    
    class Meta:
        app_label = "product"
        db_table = "category"

class Product(models.Model):
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)

# response
class CategoryChildResponse(Schema):
    id: int
    name: str

class CategoryParentResponse(Schema):
    id: int
    name: str
    children: List[CategoryChildResponse]
    
    @classmethod
    def build(cls, category: Category):
        return cls(
            id=category.id,
            name=category.name,
            children=[
                CategoryChildResponse(id=child.id, name=child.name)
                for child in category.children.all()
            ]
        )

class CategoryListResponse(Schema):
    categories: List[CategoryParentResponse]
    
    @classmethod
    def build(cls, categories: List[Category]):
        return cls(
            categories=[
              CategoryParentResponse.build(category=category)
              for category in categories
            ]
        )

# urls
@router.get(
    "/categories",
    response={
        200: ObjectResponse[CategoryListResponse],
    },
)
def categories_list_handler(request: HttpRequest):
    return 200, response(
        CategoryListResponse.build(categories=Category.objects.filter(parent=None))
    )

# query by category_id
def product_list_handler(request: HttpRequest, category_id: int | None = None):
    if category_id:
        category: Category | None = Category.objects.filter(id=category_id).first()
        if not category:
            products = []
        else:
            category_ids: List[int] = [category.id] + list(category.children.values_list("id", flat=True))
            products = Product.objects.filter(
                category_id__in=category_ids, status=ProductStatus.ACTIVE
            ).values("id", "name", "price")
    else:
        products = Product.objects.filter(status=ProductStatus.ACTIVE).values("id", "name", "price")

    return 200, response(ProductListResponse(products=products))
```
- select_related()
  - N:1 관계에서 사용
  - JOIN 쿼리
  - eager loading -> N+1 문제 해결
- prefetch_related()
  - 1:N 관계에서 사용
  - 추가 쿼리(batch 쿼리)
  - eager loading -> N+1 문제 해결
