import pytest
from schema import Schema

from product.models import Product, ProductStatus, OrderLine, Order, OrderStatus
from user.authentication import authentication_service
from user.models import ServiceUser, UserPointsHistory, UserPoints


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
        {"results": {"products": [{"id": int, "name": "청바지", "price": 1}]}}
    ).validate(response.json())


@pytest.mark.django_db
def test_order_products(api_client):
    # given
    user = ServiceUser.objects.create(email="goodpang@example.com")
    token = authentication_service.encode_token(user_id=user.id)

    p1 = Product.objects.create(name="청바지", price=1000, status=ProductStatus.ACTIVE)
    p2 = Product.objects.create(name="티셔츠", price=500, status=ProductStatus.ACTIVE)

    # when
    response = api_client.post(
        "/products/orders",
        data={
            "order_lines": [
                {"product_id": p1.id, "quantity": 2},
                {"product_id": p2.id, "quantity": 3},
            ]
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # then
    assert response.status_code == 201
    assert Schema(
        {
            "results": {
                "id": int,
                "total_price": int((p1.price * 2 * 0.9) + (p2.price * 3 * 0.9)),
            }
        }
    ).validate(response.json())

    order_id = response.json()["results"]["id"]
    assert OrderLine.objects.filter(order_id=order_id).count() == 2


@pytest.mark.django_db
def test_confirm_order(api_client):
    # given
    user = ServiceUser.objects.create(email="goodpang@example.com", points=1000)
    token = authentication_service.encode_token(user_id=user.id)

    order = Order.objects.create(
        user=user, total_price=1000, status=OrderStatus.PENDING
    )

    # when
    response = api_client.post(
        f"/products/orders/{order.id}/confirm",
        headers={"Authorization": f"Bearer {token}"},
    )

    # then
    assert response.status_code == 200
    assert Schema({"results": {"detail": "ok"}}).validate(response.json())

    assert Order.objects.get(id=order.id).status == OrderStatus.PAID
    assert ServiceUser.objects.get(id=user.id).order_count == 1
    assert ServiceUser.objects.get(id=user.id).points == 0
    assert UserPointsHistory.objects.filter(user=user, points_change=-1000).exists()


@pytest.mark.django_db
def test_confirm_order_v2(api_client):
    # given
    user = ServiceUser.objects.create(email="goodpang@example.com")
    token = authentication_service.encode_token(user_id=user.id)

    UserPoints.objects.create(
        user=user, points_change=1000, points_sum=1000, reason="charge"
    )

    order = Order.objects.create(
        user=user, total_price=1000, status=OrderStatus.PENDING
    )

    # when
    response = api_client.post(
        f"/products/orders/{order.id}/confirm-v2",
        headers={"Authorization": f"Bearer {token}"},
    )

    # then
    assert response.status_code == 200
    assert Schema({"results": {"detail": "ok"}}).validate(response.json())

    assert Order.objects.get(id=order.id).status == OrderStatus.PAID
    assert ServiceUser.objects.get(id=user.id).order_count == 1

    last_points = (
        UserPoints.objects.filter(user_id=user.id).order_by("-version").first()
    )

    assert last_points.points_change == -1000
    assert last_points.points_sum == 0
