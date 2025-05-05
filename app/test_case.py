"""Юніт-тести для класів Product, ShoppingCart та Order."""

import unittest
from unittest.mock import MagicMock
from eshop import Product, ShoppingCart, Order


class TestProduct(unittest.TestCase):
    """Тести для класу Product та ShoppingCart."""

    def setUp(self):
        """Підготовка тестового продукту та кошика перед кожним тестом."""
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
        """Перевірка створення продукту з None — очікується помилка."""
        with self.assertRaises(ValueError):
            Product(name=None, price=None, available_amount=None)

    def test_product_creation_with_negative_price(self):
        """Перевірка створення продукту з від'ємною ціною — очікується помилка."""
        with self.assertRaises(ValueError):
            Product(name="Test", price=-10, available_amount=5)

    def test_product_availability_exact(self):
        """Перевірка доступності продукту у точній кількості."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertTrue(product.is_available(10))

    def test_product_availability_exceeds(self):
        """Перевірка відмови при надмірному запиті кількості."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertFalse(product.is_available(15))

    def test_add_available_amount(self):
        """Успішне додавання продукту до кошика у допустимій кількості."""
        self.cart.add_product(self.product, 11)
        self.assertTrue(self.cart.contains_product(self.product))

    def test_add_non_available_amount(self):
        """Спроба додати занадто велику кількість продукту — очікується помилка."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 22)

    def test_remove_product_from_cart(self):
        """Перевірка видалення продукту з кошика."""
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product))

    def test_calculate_total(self):
        """Перевірка обчислення загальної суми товарів у кошику."""
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.calculate_total(), 246.9)

    def test_add_product_with_zero_quantity(self):
        """Спроба додати продукт з нульовою кількістю — очікується помилка."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)

    def test_add_product_with_string_quantity(self):
        """Спроба додати продукт з нечисловою кількістю — очікується помилка."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, "two")

    def test_submit_cart_order_reduces_stock(self):
        """Оформлення замовлення має зменшити кількість товару на складі."""
        self.cart.add_product(self.product, 3)
        self.cart.submit_cart_order()
        self.assertEqual(self.product.available_amount, 18)

    def test_order_from_empty_cart(self):
        """Створення замовлення з порожнього кошика — очікується помилка."""
        with self.assertRaises(ValueError):
            Order(self.cart)


if __name__ == '__main__':
    unittest.main()
