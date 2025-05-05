import uuid
import random
from datetime import datetime, timedelta, timezone

import boto3
import pytest

from app.eshop import Product, ShoppingCart, Order, Shipment
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE


@pytest.mark.parametrize("order_id, shipping_id", [
    ("order_1", "shipping_1"),
    ("order_i2hur2937r9", "shipping_1!!!!"),
    (8662354, 123456),
    (str(uuid.uuid4()), str(uuid.uuid4()))
])
def test_place_order_with_mocked_repo(mocker, order_id, shipping_id):
    """Перевірка створення замовлення з моками."""
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    shipping_service = ShippingService(mock_repo, mock_publisher)

    mock_repo.create_shipping.return_value = shipping_id

    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service, order_id)
    due_date = datetime.now(timezone.utc) + timedelta(seconds=3)
    actual_shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=due_date
    )

    assert actual_shipping_id == shipping_id
    mock_repo.create_shipping.assert_called_with(
        ShippingService.list_available_shipping_type()[0],
        ["Product"],
        order_id,
        shipping_service.SHIPPING_CREATED,
        due_date
    )
    mock_publisher.send_new_shipping.assert_called_with(shipping_id)


def test_place_order_with_unavailable_shipping_type_fails(dynamo_resource):
    """Перевірка помилки при невідомому типі доставки."""
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )
    order = Order(cart, shipping_service)

    with pytest.raises(ValueError) as excinfo:
        _ = order.place_order(
            "Новий тип доставки",
            due_date=datetime.now(timezone.utc) + timedelta(seconds=3)
        )
    assert "Shipping type is not available" in str(excinfo.value)


def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    """Перевірка, що замовлення потрапляє в чергу SQS."""
    shipping_service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(Product(
        available_amount=10,
        name='Product',
        price=random.random() * 10000),
        amount=9
    )

    order = Order(cart, shipping_service)
    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        due_date=datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]
    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])
    assert len(messages) == 1
    assert shipping_id == messages[0]["Body"]


def test_process_batch_with_no_shippings(dynamo_resource):
    """Перевірка обробки порожньої партії доставок."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    result = service.process_shipping_batch()
    assert len(result) == 0


def test_create_order_with_invalid_due_date(dynamo_resource):
    """Перевірка помилки при минулій даті доставки."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=5, name="TestProduct", price=200.0), amount=1)

    order = Order(cart, service)
    past_due_date = datetime.now(timezone.utc) - timedelta(days=1)

    with pytest.raises(ValueError):
        order.place_order(service.list_available_shipping_type()[0], past_due_date)


def test_shipment_retrieval(dynamo_resource):
    """Перевірка статусу доставки."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=5, name="TestProduct", price=200.0), amount=1)

    order = Order(cart, service)
    due_date = datetime.now(timezone.utc) + timedelta(days=1)
    shipping_id = order.place_order(service.list_available_shipping_type()[0], due_date)

    shipment = Shipment(shipping_id, service)
    assert shipment.check_shipping_status() == service.SHIPPING_IN_PROGRESS


def test_invalid_shipping_type_raises_error(dynamo_resource):
    """Перевірка помилки при невалідному типі доставки."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=5, name="InvalidProduct", price=50.0), amount=1)

    order = Order(cart, service)
    due_date = datetime.now(timezone.utc) + timedelta(minutes=5)

    with pytest.raises(ValueError):
        order.place_order("InvalidType", due_date)


def test_order_with_empty_cart(dynamo_resource):
    """Помилка при створенні замовлення з порожнього кошика."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    order = Order(cart, service)

    with pytest.raises(ValueError, match="Cart is empty. Cannot place an order."):
        order.place_order(service.list_available_shipping_type()[0],
                          datetime.now(timezone.utc) + timedelta(minutes=10))


def test_large_order_processing(dynamo_resource):
    """Обробка замовлення з великою кількістю товарів."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    for i in range(100):
        cart.add_product(Product(available_amount=200, name=f"Product_{i}", price=20.0), amount=1)

    order = Order(cart, service)
    due_date = datetime.now(timezone.utc) + timedelta(minutes=20)
    shipping_id = order.place_order(service.list_available_shipping_type()[0], due_date)

    assert shipping_id is not None


def test_multiple_orders_in_parallel(dynamo_resource):
    """Паралельна обробка кількох замовлень."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    cart1 = ShoppingCart()
    cart1.add_product(Product(available_amount=50, name="Product1", price=20.0), amount=1)

    cart2 = ShoppingCart()
    cart2.add_product(Product(available_amount=50, name="Product2", price=25.0), amount=1)

    order1 = Order(cart1, service)
    order2 = Order(cart2, service)

    due_date = datetime.now(timezone.utc) + timedelta(minutes=5)

    shipping_id1 = order1.place_order(service.list_available_shipping_type()[0], due_date)
    shipping_id2 = order2.place_order(service.list_available_shipping_type()[0], due_date)

    assert shipping_id1 != shipping_id2


def test_order_with_failed_shipping(dynamo_resource):
    """Імітація провалу доставки."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=3, name="FailedProduct", price=25.0), amount=1)
    order = Order(cart, service)

    due_date = datetime.now(timezone.utc) + timedelta(minutes=10)
    shipping_id = order.place_order(service.list_available_shipping_type()[0], due_date)

    service.fail_shipping(shipping_id)
    status = service.check_status(shipping_id)
    assert status == service.SHIPPING_FAILED


def test_order_with_future_due_date(dynamo_resource):
    """Перевірка статусу замовлення з майбутньою датою."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=7, name="FutureProduct", price=40.0), amount=2)
    order = Order(cart, service)
    due_date = datetime.now(timezone.utc) + timedelta(days=1)
    shipping_id = order.place_order(service.list_available_shipping_type()[0], due_date)
    status = service.check_status(shipping_id)
    assert status == service.SHIPPING_IN_PROGRESS


def test_create_shipping_without_due_date(dynamo_resource):
    """Створення доставки без дати завершення."""
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()
    cart.add_product(Product(available_amount=15, name="NoDueProduct", price=55.0), amount=1)
    order = Order(cart, service)
    shipping_id = order.place_order(service.list_available_shipping_type()[0])
    assert shipping_id is not None
