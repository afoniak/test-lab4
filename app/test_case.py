import unittest
from eshop import Product, ShoppingCart, Order
from unittest.mock import MagicMock

class TestProduct(unittest.TestCase):
    def setUp(self):
        self.product = Product(name='Test', price=123.45, available_amount=21)
        self.cart = ShoppingCart()

    def tearDown(self):
        self.cart.remove_product(self.product)

    #Product
    def test_mock_add_product(self):
        self.product.is_available = MagicMock()
        self.cart.add_product(self.product, 12345)
        self.product.is_available.assert_called_with(12345)
        self.product.is_available.reset_mock()

    def test_product_creation_with_none(self):
        with self.assertRaises(ValueError):
            Product(name=None, price=None, available_amount=None)

    def test_product_creation_with_negative_price(self):
        with self.assertRaises(ValueError):
            Product(name="Test", price=-10, available_amount=5)

    def test_product_availability_exact(self):
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertTrue(product.is_available(10))

    def test_product_availability_exceeds(self):
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertFalse(product.is_available(15))

    #ShoppingCart
    def test_add_available_amount(self):
        self.cart.add_product(self.product, 11)
        self.assertTrue(self.cart.contains_product(self.product))

    def test_add_non_available_amount(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 22)

    def test_remove_product_from_cart(self):
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product))

    def test_calculate_total(self):
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.calculate_total(), 246.9)

    def test_add_product_with_zero_quantity(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)

    def test_add_product_with_string_quantity(self):
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, "two")

    def test_submit_cart_order_reduces_stock(self):
        self.cart.add_product(self.product, 3)
        self.cart.submit_cart_order()
        self.assertEqual(self.product.available_amount, 18)

    #Order
    def test_order_from_empty_cart(self):
        with self.assertRaises(ValueError):
            Order(self.cart)

if __name__ == '__main__':
    unittest.main()
