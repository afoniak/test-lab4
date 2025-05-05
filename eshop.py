from typing import Dict


class Product:
    available_amount: int
    name: str
    price: float

    def __init__(self, name, price, available_amount):
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
        return isinstance(requested_amount, int) and requested_amount > 0 and self.available_amount >= requested_amount

    def buy(self, requested_amount):
        if not self.is_available(requested_amount):
            raise ValueError(f"Cannot buy {requested_amount} items, only {self.available_amount} available")
        self.available_amount -= requested_amount

    def __eq__(self, other):
        return isinstance(other, Product) and self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


class ShoppingCart:
    products: Dict[Product, int]

    def __init__(self):
        self.products = dict()

    def contains_product(self, product):
        return product in self.products

    def calculate_total(self):
        return sum([p.price * count for p, count in self.products.items()])

    def add_product(self, product: Product, amount: int):
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError("Cannot add zero or negative quantity to cart")
        if not product.is_available(amount):
            raise ValueError(f"Product {product} has only {product.available_amount} items")
        self.products[product] = amount

    def remove_product(self, product):
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self):
        if not self.products:
            raise ValueError("Cannot submit order with empty cart")
        for product, count in self.products.items():
            product.buy(count)
        self.products = dict()


class Order:
    def __init__(self, cart: ShoppingCart):
        if not cart.products:
            raise ValueError("Cannot place an order with an empty cart")
        self.cart = cart

    def place_order(self):
        if not self.cart.products:
            raise ValueError("Order cannot be placed: cart is empty")
        self.cart.submit_cart_order()
