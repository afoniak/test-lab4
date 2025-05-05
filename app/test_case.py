import unittest
from unittest.mock import MagicMock
from app.eshop import Product, ShoppingCart, Order


class TestProductAndCart(unittest.TestCase):
    """Тести для класів Product та ShoppingCart."""

    def setUp(self):
        """Ініціалізація тестового продукту та кошика."""
        self.product = Product(name='Test', price=123.45, available_amount=21)
        self.cart = ShoppingCart()

    def tearDown(self):
        """Очищення кошика після кожного тесту."""
        self.cart.remove_product(self.product)

    def test_mock_add_product(self):
        """Перевірка виклику is_available при додаванні продукту."""
        self.product.is_available = MagicMock()
        self.cart.add_product(self.product, 12345)
        self.product.is_available.assert_called_with(12345)

    def test_product_creation_with_none(self):
        """Продукт з None-значеннями має викликати помилку."""
        with self.assertRaises(ValueError):
            _ = Product(name=None, price=None, available_amount=None)

    def test_product_creation_with_negative_price(self):
        """Створення продукту з від'ємною ціною викликає помилку."""
        with self.assertRaises(ValueError):
            _ = Product(name="Test", price=-10, available_amount=5)

    def test_product_availability_exact(self):
        """Продукт доступний рівно у вказаній кількості."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertTrue(product.is_available(10))

    def test_product_availability_exceeds(self):
        """Недостатня кількість продукту повертає False."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertFalse(product.is_available(15))

    def test_add_available_amount(self):
        """Додавання продукту в наявній кількості успішне."""
        self.cart.add_product(self.product, 11)
        self.assertTrue(self.cart.contains_product(self.product))

    def test_add_non_available_amount(self):
        """Спроба додати надмірну кількість викликає помилку."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 22)

    def test_remove_product_from_cart(self):
        """Видалення продукту з кошика."""
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product))

    def test_calculate_total(self):
        """Обчислення повної вартості в кошику."""
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.calculate_total(), 246.9)

    def test_add_product_with_zero_quantity(self):
        """Нульова кількість викликає помилку."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)

    def test_add_product_with_string_quantity(self):
        """Символьна кількість викликає помилку."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, "two")

    def test_submit_cart_order_reduces_stock(self):
        """Після оформлення замовлення зменшується склад."""
        self.cart.add_product(self.product, 3)
        self.cart.submit_cart_order()
        self.assertEqual(self.product.available_amount, 18)


class TestOrder(unittest.TestCase):
    """Тести для класу Order."""

    def test_order_from_empty_cart(self):
        """Замовлення з порожнього кошика викликає помилку."""
        cart = ShoppingCart()
        with self.assertRaises(ValueError):
            _ = Order(cart)
