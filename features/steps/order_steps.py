from behave import given, when, then
from eshop import ShoppingCart, Order, Product

@given('A shopping cart with products')
def cart_with_products(context):
    context.cart = ShoppingCart()
    product = Product(name="Phone", price=500, available_amount=2)
    context.cart.add_product(product, 2)

@given('A completely empty shopping cart')
def empty_cart(context):
    context.cart = ShoppingCart()

@when('I place an order')
def place_order(context):
    try:
        context.order = Order(context.cart)
        context.order.place_order()
        context.order_success = True
    except Exception:
        context.order_success = False

@when("I try to place an order again")
def place_order_again(context):
    try:
        context.order.place_order()
        context.order_success = True
    except Exception:
        context.order_success = False

@given("The product availability becomes zero")
def make_product_unavailable(context):
    for product in context.cart.products.keys():
        product.available_amount = 0

@then('Order should be placed successfully')
def check_order_success(context):
    assert context.order_success is True, "Order placement failed!"

@then('Order should not be placed successfully')
def check_order_failure(context):
    assert context.order_success is False, "Order should not be placed!"
