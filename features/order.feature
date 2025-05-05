Feature: Order
  We want to test that order processing works correctly

  Scenario: Place an order successfully
    Given A shopping cart with products
    When I place an order
    Then Order should be placed successfully

  Scenario: Place an order with empty cart
    Given An empty shopping cart
    When I place an order
    Then Order should not be placed successfully

  Scenario: Place second order after cart was already submitted
    Given A shopping cart with products
    When I place an order
    And I try to place an order again
    Then Order should not be placed successfully

  Scenario: Place order when product is no longer available
    Given A shopping cart with products
    And The product availability becomes zero
    When I place an order
    Then Order should not be placed successfully
