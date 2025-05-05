Feature: Product
  We want to test that product class functionality works correctly

  Scenario: Create product with valid data
    Given A product with name "Laptop", price 1000.50 and availability 5
    Then Product should be created successfully

  Scenario: Create product with None values
    Given A product with name None, price None and availability None
    Then Product creation should fail

  Scenario: Create product with negative price
    Given A product with name "Laptop", price -10.50 and availability 5
    Then Product creation should fail

  Scenario: Check product availability for exact stock
    Given A product with name "Phone", price 500.00 and availability 3
    When I check if I can buy 3 units
    Then The result should be True
