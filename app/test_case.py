import unittest
from unittest.mock import MagicMock
from app.eshop import Product, ShoppingCart, Order


class TestProductAndCart(unittest.TestCase):
    """Test suite for Product and ShoppingCart."""

    def setUp(self):
        """Create a test product and shopping cart."""
        self.product = Product(name='Test', price=123.45, available_amount=21)
        self.cart = ShoppingCart()

    def tearDown(self):
        """Clear the cart after each test."""
        self.cart.remove_product(self.product)

    def test_mock_add_product(self):
        """Test that is_available is called during product addition."""
        self.product.is_available = MagicMock()
        self.cart.add_product(self.product, 12345)
        self.product.is_available.assert_called_with(12345)

    def test_product_creation_with_none(self):
        """Test product creation with None values fails."""
        with self.assertRaises(ValueError):
            _ = Product(name=None, price=None, available_amount=None)

    def test_product_creation_with_negative_price(self):
        """Test product creation with negative price fails."""
        with self.assertRaises(ValueError):
            _ = Product(name="Test", price=-10, available_amount=5)

    def test_product_availability_exact(self):
        """Test availability check for exact amount."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertTrue(product.is_available(10))

    def test_product_availability_exceeds(self):
        """Test availability check when exceeding stock."""
        product = Product(name="Phone", price=500.0, available_amount=10)
        self.assertFalse(product.is_available(15))

    def test_add_available_amount(self):
        """Test adding a valid amount of product to cart."""
        self.cart.add_product(self.product, 11)
        self.assertTrue(self.cart.contains_product(self.product))

    def test_add_non_available_amount(self):
        """Test adding more than available amount raises ValueError."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 22)

    def test_remove_product_from_cart(self):
        """Test product removal from cart."""
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product))

    def test_calculate_total(self):
        """Test total price calculation in cart."""
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.calculate_total(), 246.9)

    def test_add_product_with_zero_quantity(self):
        """Test that zero quantity raises ValueError."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)

    def test_add_product_with_string_quantity(self):
        """Test that non-integer quantity raises ValueError."""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, "two")

    def test_submit_cart_order_reduces_stock(self):
        """Test that submitting cart reduces product stock."""
        self.cart.add_product(self.product, 3)
        self.cart.submit_cart_order()
        self.assertEqual(self.product.available_amount, 18)


class TestOrder(unittest.TestCase):
    """Test suite for Order logic."""

    def test_order_from_empty_cart(self):
        """Test that placing an order with empty cart raises error."""
        cart = ShoppingCart()
        with self.assertRaises(ValueError):
            _ = Order(cart)
