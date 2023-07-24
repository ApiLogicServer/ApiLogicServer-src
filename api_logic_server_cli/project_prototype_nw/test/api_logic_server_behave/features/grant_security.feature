Feature: Test Grant Security

    Scenario: Test Grant Security u1 
        Given Login user u1
        When Get Category u1
        Then u1 Category count is 1

    Scenario: Test Grant Security u2
        Given Login user u2
        When Get Category u1
        Then u2 Category count > 1

    Scenario: Test Grant Security full
        Given Login user full 
        When Get Category full
        Then full Category count > 1

    Scenario: Test Grant Security ro
        Given Login user ro 
        When Get category ro
        Then User ro count > 1
        Then Delete ro Category
        Then Insert ro Category
        Then Update ro Category