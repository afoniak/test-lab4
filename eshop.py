from typing import Dict
class Product:

    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
        """Ініціалізація продукту з валідацією."""
        if not name or price is None or available_amount is None:
            raise ValueError("Product attributes cannot be None")
        if not isinstance(name, str):
            raise TypeError("Product name must be a string")
        if not isinstance(price, (int, float)) or not isinstance(available_amount, int):
            raise TypeError("Price must be a number and available_amount must be an integer")
        if price < 0 or available_amount < 0:
            raise ValueError("Price and available amount cannot be negative")

        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount):
        """Перевірка, чи доступна запитувана кількість."""
        return isinstance(requested_amount, int) and requested_amount > 0 and self.available_amount >= requested_amount

    def buy(self, requested_amount):
        """Списати товар зі складу."""
        if not self.is_available(requested_amount):
            raise ValueError(f"Cannot buy {requested_amount} items, only {self.available_amount} available")
        self.available_amount -= requested_amount

    def __eq__(self, other):
        """Порівняння продуктів за назвою."""
        return isinstance(other, Product) and self.name == other.name

    def __ne__(self, other):
        """Нерівність продуктів."""
        return not self.__eq__(other)

    def __hash__(self):
        """Підтримка використання у множинах і словниках."""
        return hash(self.name)

    def __str__(self):
        """Текстове представлення продукту."""
        return self.name


class ShoppingCart:

    products: Dict[Product, int]

    def __init__(self):
        """Створити порожній кошик."""
        self.products = {}

    def contains_product(self, product):
        """Перевірити наявність товару у кошику."""
        return product in self.products

    def calculate_total(self):
        """Обчислити повну вартість товарів у кошику."""
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int):
        """Додати товар у кошик з перевіркою доступності."""
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Cannot add zero or negative quantity to cart")
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        """Видалити товар із кошика."""
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        """Оформити замовлення — списати всі товари з наявності."""
        if not self.products:
            raise ValueError("Cannot submit order with empty cart")
        for product, count in self.products.items():
            product.buy(count)
        self.products = {}


class Order:

    def __init__(self, cart: ShoppingCart):
        """Ініціалізація замовлення з перевіркою непорожнього кошика."""
        if not cart.products:
            raise ValueError("Cannot place an order with an empty cart")
        self.cart = cart

    def place_order(self):
        """Оформити замовлення — списати товари з кошика."""
        if not self.cart.products:
            raise ValueError("Order cannot be placed: cart is empty")
        self.cart.submit_cart_order()
