from behave import given, when, then
from eshop import Product

@given('A product with name {name}, price {price} and availability {availability}')
def create_product(context, name, price, availability):
    try:
        price = float(price) if price.lower() != "none" else None
        availability = int(availability) if availability.lower() != "none" else None
        context.product = Product(name=name if name.lower() != "none" else None, price=price, available_amount=availability)
        context.creation_success = True
    except Exception:
        context.creation_success = False

@then('Product should be created successfully')
def check_product_created(context):
    assert context.creation_success is True, "Product creation failed!"

@then('Product creation should fail')
def check_product_creation_failed(context):
    assert context.creation_success is False, "Product creation should have failed!"

@when('I check if I can buy {amount} units')
def check_availability(context, amount):
    context.check_result = context.product.is_available(int(amount))

@then('The result should be True')
def check_availability_true(context):
    assert context.check_result is True, "Expected True but got False"
