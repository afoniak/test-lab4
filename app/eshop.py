from typing import Dict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import uuid
from services import ShippingService


class Product:

    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
        """Ініціалізація нового товару."""
        if not name or price is None or available_amount is None:
            raise ValueError("Invalid product attributes")
        if price < 0 or available_amount < 0:
            raise ValueError("Negative price or amount not allowed")

        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount):
        """Перевірити, чи доступна вказана кількість товару."""
        return self.available_amount >= requested_amount

    def buy(self, requested_amount):
        """Списати товар після купівлі."""
        self.available_amount -= requested_amount

    def __eq__(self, other):
        """Порівняння продуктів за назвою."""
        return self.name == other.name

    def __ne__(self, other):
        """Нерівність продуктів."""
        return self.name != other.name

    def __hash__(self):
        """Підтримка використання у словниках."""
        return hash(self.name)

    def __str__(self):
        """Текстове представлення продукту."""
        return self.name


class ShoppingCart:

    products: Dict[Product, int]

    def __init__(self):
        """Ініціалізація порожнього кошика."""
        self.products = {}

    def contains_product(self, product):
        """Перевірити, чи є товар у кошику."""
        return product in self.products

    def calculate_total(self):
        """Обчислити загальну вартість товарів у кошику."""
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int):
        """Додати товар до кошика, якщо його достатньо на складі."""
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Amount must be a positive integer")
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        """Видалити товар з кошика."""
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        """Оформити замовлення — списати товари та повернути їх ID."""
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))
        self.products.clear()
        return product_ids


@dataclass
class Order:

    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = str(uuid.uuid4())

    def place_order(self, shipping_type, due_date: datetime = None):
        """Оформити замовлення з вказаним типом доставки та дедлайном."""
        if not self.cart.products:
            raise ValueError("Cart is empty. Cannot place an order.")

        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)

        if due_date <= datetime.now(timezone.utc):
            raise ValueError("Shipping due datetime must be greater than datetime now")

        product_ids = self.cart.submit_cart_order()

        return self.shipping_service.create_shipping(
            shipping_type, product_ids, self.order_id, due_date
        )


@dataclass
class Shipment:
    """Клас для перевірки статусу доставки."""

    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        """Отримати статус поточної доставки."""
        return self.shipping_service.check_status(self.shipping_id)
