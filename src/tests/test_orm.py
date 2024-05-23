import pytest
from django.db.models import Window, Count, Q, Avg, F, Case, When, Value
from django.db.models.functions import RowNumber, Round

from product.models import Category, Product
from user.models import ServiceUser, UserPoints

"""
# aggregate()
- 집계 함수 => 하나의 scalar 값 반환
"""


@pytest.mark.django_db
def test_aggregate_product_price():
    # given
    Product.objects.create(name="티셔츠", price=1000)
    Product.objects.create(name="반바지", price=1000)
    Product.objects.create(name="청바지", price=1200)

    # when
    ret = Product.objects.aggregate(
        avg_price=Round(Avg("price"), precision=2),
        count=Count("id"),
    )

    # then
    assert ret == {"avg_price": 1066.67, "count": 3}


"""
# values()
- 반환되는 컬럼 지정
- 예) Product(id, name, price, status, created_at)
  - Product.objects.values("id", "name").filter(id=1) => [{"id": 1, "name": "p1"}]

# annotate()
- 객체 단위의 추가 컬럼 데이터
"""


@pytest.mark.django_db
def test_annotate_category_name():
    # given
    c1 = Category.objects.create(name="상의")
    c2 = Category.objects.create(name="하의")

    Product.objects.create(name="티셔츠", price=1, category=c1)
    Product.objects.create(name="반바지", price=1, category=c2)
    Product.objects.create(name="청바지", price=1, category=c2)

    # when
    ret = list(
        Product.objects.annotate(category_name=F("category__name"))
        .values("name", "category_name")
        .order_by("id")
    )

    # then
    assert ret == [
        {"name": "티셔츠", "category_name": "상의"},
        {"name": "반바지", "category_name": "하의"},
        {"name": "청바지", "category_name": "하의"},
    ]


"""
# annotate() + values() => GROUP BY X
# values() + annotate() => GROUP BY `values`
"""


@pytest.mark.django_db
def test_group_by_category_name():
    # given
    c1 = Category.objects.create(name="상의")
    c2 = Category.objects.create(name="하의")

    # 상의 -> 1
    Product.objects.create(name="티셔츠", price=1, category=c1)

    # 하의 -> 2
    Product.objects.create(name="반바지", price=1, category=c2)
    Product.objects.create(name="청바지", price=1, category=c2)

    # when
    ret = list(
        Product.objects.values(category_name=F("category__name"))
        .annotate(count=Count("id"))
        .order_by("category_name", "count")
    )

    # then
    assert ret == [
        {"category_name": "상의", "count": 1},
        {"category_name": "하의", "count": 2},
    ]


@pytest.mark.django_db
def test_annotate_count():
    """카테고리에 속한 active 상품 개수 함께 조회"""

    # given
    c1 = Category.objects.create(name="상의")  # 1
    Category.objects.create(name="유제품")  # 0

    Product.objects.create(name="티셔츠", price=1, status="active", category=c1)
    Product.objects.create(name="셔츠", price=1, status="inactive", category=c1)
    Product.objects.create(name="청바지", price=1, status="active")

    # when
    ret = list(
        Category.objects.annotate(
            product_counts=Count("product", filter=Q(product__status="active"))
        )
        .values("name", "product_counts")
        .order_by("id")
    )

    # then
    assert ret == [
        {"name": "상의", "product_counts": 1},
        {"name": "유제품", "product_counts": 0},
    ]


@pytest.mark.django_db
def test_case_when():
    """가격 별로 상품 분류"""

    # given
    Product.objects.create(name="티셔츠", price=100)
    Product.objects.create(name="셔츠", price=500)
    Product.objects.create(name="청바지", price=1000)

    # when
    ret = list(
        Product.objects.annotate(
            label=Case(
                When(price__gte=1000, then=Value("expensive")),
                When(price__gte=500, then=Value("reasonable")),
                default=Value("cheap"),
            )
        )
        .values("price", "label")
        .order_by("id")
    )

    # then
    assert ret == [
        {"price": 100, "label": "cheap"},
        {"price": 500, "label": "reasonable"},
        {"price": 1000, "label": "expensive"},
    ]


@pytest.mark.django_db
def test_last_points():
    """유저의 최신 포인트 조회"""

    # given
    u1 = ServiceUser.objects.create(email="e1")
    u2 = ServiceUser.objects.create(email="e2")

    UserPoints.objects.create(
        user=u1, version=0, points_change=0, points_sum=0, reason=""
    )
    UserPoints.objects.create(
        user=u1, version=1, points_change=100, points_sum=100, reason=""
    )
    UserPoints.objects.create(
        user=u1, version=2, points_change=100, points_sum=200, reason="v"
    )

    UserPoints.objects.create(
        user=u2, version=0, points_change=0, points_sum=0, reason=""
    )
    UserPoints.objects.create(
        user=u2, version=1, points_change=100, points_sum=100, reason="v"
    )

    # when
    ret = list(
        UserPoints.objects.values("user_id")
        .annotate(
            row_num=Window(
                expression=RowNumber(), partition_by="user_id", order_by="-version"
            )
        )
        .filter(row_num=1)
        .values("user_id", "version", "points_sum")
    )

    # then
    assert ret == [
        {"user_id": u1.id, "version": 2, "points_sum": 200},
        {"user_id": u2.id, "version": 1, "points_sum": 100},
    ]
