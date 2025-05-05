Feature:Shopping cart
  We want to test that shopping cart functionality works correctly

  Scenario: Successful add product to cart
    Given The product has availability of 123
    And An empty shopping cart
    When I add product to the cart in amount 123
    Then Product is added to the cart successfully

  Scenario: Failed add product to cart
    Given The product has availability of 123
    And An empty shopping cart
    When I add product to the cart in amount 124
    Then Product is not added to cart successfully

  Scenario: Add negative quantity of product to cart
    Given The product has availability of 5
    And An empty shopping cart
    When I add product to the cart in amount -1
    Then Product is not added to cart successfully

  Scenario: Add non-integer quantity of product to cart
    Given The product has availability of 5
    And An empty shopping cart
    When I add product to the cart in amount "two"
    Then Product is not added to cart successfully
