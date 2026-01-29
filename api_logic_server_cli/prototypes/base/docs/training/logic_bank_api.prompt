---
# LogicBank API Reference
# Version: 1.0.3
# Last Updated: January 29, 2026
# Description: The Logic Rosetta Stone: simplified API for creating declarative business logic rules
---

=============================================================================
💎 CORE PRINCIPLE: Path-Independent Rules = Automatic Reuse
=============================================================================

**What you're really doing:** Distilling path-independent rules from path-dependent logic.

**Path-dependent (procedural):** Separate code for each execution path
- Add item → recalc amounts
- Change quantity → recalc amounts  
- Change customer → adjust both balances
- Ship order → adjust balance
- Delete item → recalc amounts

**Path-independent (declarative):** ONE rule works for ALL paths
```python
Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
```

**Automatic reuse over use cases:** Whereas reuse is typically a high-order design skill, declarative rules provide *automatic reuse* - write the relationship once, it works for insert/update/delete/parent changes. No use case explosion.

=============================================================================

Here is the simplified API for LogicBank:

PREREQUISITE: For general patterns (event handler signatures, logging, request pattern, anti-patterns),
see docs/training/logic_bank_patterns.prompt

=============================================================================
🗂️ CRITICAL: Directory Structure = Requirements Traceability
=============================================================================

**Pattern Recognition:**
- Context phrases ("When X", "For Y", "On Z") → directory: logic/logic_discovery/x/
- After context, each colon-terminated phrase → file: phrase.py
- Prefixes like "Use case:", "Requirement:" are optional (just noise words)
- No context phrase → single file (flat structure OK)

**Naming:** Convert to snake_case, remove articles
- "When Placing Orders" / "On Placing Orders" → place_order/
- "Check Credit:" → check_credit.py
- "Use case: App Integration:" → app_integration.py

**Requirements Traceability:** File structure provides direct link from use case to implementation
```
Prompt: "On Placing Orders, Check Credit: ..."
Result: logic/logic_discovery/place_order/check_credit.py
Trace:  Use Case Name → File Path → Rules → Logic Report
```

**Examples:**
```
Prompt: "When Placing Orders, Check Credit: ... App Integration: ..."
Result: logic/logic_discovery/place_order/{__init__.py, check_credit.py, app_integration.py}

Prompt: "For Customer Management, Validate Credit: ... Calculate Loyalty: ..."
Result: logic/logic_discovery/customer_management/{__init__.py, validate_credit.py, calculate_loyalty.py}

Prompt: "Check Credit: ..." (no context)
Result: logic/logic_discovery/check_credit.py (flat)
```

=============================================================================

Translate the user prompt into a series of calls to Rule methods, described here.

Do not generate import statements.

If you create sum, count or formula LogicBank rules, you MUST create a corresponding column in the data model.

Use only the methods provided below.

IMPORTANT: Keep it simple! Use the built-in Rule methods with their parameters (like if_condition) rather than creating custom functions. The Rule methods are designed to handle common patterns directly.

CRITICAL: Keep simple rules on ONE LINE (no exceptions). Goal: Visual scannability - see rule count at a glance.

✅ CORRECT - One rule per line:
    Rule.sum(derive=Customer.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.constraint(validate=Customer, as_condition=lambda row: row.balance <= row.credit_limit, error_msg="balance exceeds credit")
    Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)

❌ WRONG - Don't split simple rules:
    Rule.sum(
        derive=Customer.balance,
        as_sum_of=Order.amount_total
    )


class Rule:
    """ Invoke these functions to declare rules """

    @staticmethod
    def sum(derive: Column, as_sum_of: any, where: any = None, insert_parent: bool=False):
        """
        Derive parent column as sum of designated child column, optional where

        Example
            Prompt
                Customer.Balance = Sum(Order.amount_total where date_shipped is null)
            Response
                Rule.sum(derive=Customer.Balance, as_sum_of=Order.AmountTotal,
                    where=lambda row: row.ShippedDate is None)

        Args:
            derive: name of parent <class.attribute> being derived
            as_sum_of: name of child <class.attribute> being summed
            where: optional where clause, designates which child rows are summed.  All referenced columns must be part of the data model - create columns in the data model as required.  Do not repeat the foreign key / primary key mappings, and use only attributes from the child table.
            insert_parent: create parent if it does not exist.  Do not use unless directly requested.
        """
        return Sum(derive, as_sum_of, where, insert_parent)


    @staticmethod
    def count(derive: Column, as_count_of: object, where: any = None, str = "", insert_parent: bool=False):
        """
        Derive parent column as count of designated child rows

        Example
            Prompt
                Customer.UnPaidOrders = count(Orders where ShippedDate is None)
            Response
                Rule.count(derive=Customer.UnPaidOrders, as_count_of=Order,
                    where=Lambda row: row.ShippedDate is None)

        Args:
            derive: name of parent <class.attribute> being derived
            as_count_of: name of child <class> being counted
            where: optional where clause, designates which child rows are counted.  All referenced columns must be part of the data model - create columns in the data model as required.  Do not repeat the foreign key / primary key mappings, and use only attributes from the child table.
            insert_parent: create parent if it does not exist.  Do not use unless directly requested.
        """
        return Count(derive, as_count_of, where, insert_parent)


    @staticmethod
    def constraint(validate: object,
                   calling: Callable = None,
                   as_condition: any = None,
                   error_msg: str = "(error_msg not provided)",
                   error_attributes=None):
        """
        Constraints declare condition that must be true for all commits

        Example
            Prompt
                Customer.balance <= credit_limit
            Response  
                Rule.constraint(validate=Customer,
                                as_condition=lambda row: row.Balance <= row.CreditLimit,
                                error_msg="balance ({row.Balance}) exceeds credit ({row.CreditLimit})")

        Args:
            validate: name of mapped <class>
            as_condition: lambda, passed row (simple constraints).  All referenced columns must be part of the data model - create columns in the data model as required.  Also, conditions may not contain sum or count python functions - these must be used to declare additional columns and sum/count rules.
            error_msg: string, with {row.attribute} replacements
            error_attributes: list of attributes

        """
        if error_attributes is None:
            error_attributes = []
        return Constraint(validate=validate, as_condition=as_condition,
                          error_attributes=error_attributes, error_msg=error_msg)


    @staticmethod
    def formula(derive: Column,
                as_expression: Callable = None,
                no_prune: bool = False):
        """
        Formulas declare column value, based on current and parent rows

        Example
            Prompt
                Item.amount = quantity * unit_price
            Response
                Rule.formula(derive=OrderDetail.Amount,
                             as_expression=lambda row: row.UnitPrice * row.Quantity)

        Args:
            derive: <class.attribute> being derived
            as_expression: lambda, passed row (for syntax checking).  All referenced columns must be part of the data model - create columns in the data model as required.  Expressions may not contain sum or count python functions - these must be used to declare additional columns and sum/count rules.
            no_prune: disable pruning (rarely used, default False)
        """
        return Formula(derive=derive,
                       as_expression=as_expression,
                       no_prune=no_prune)


    @staticmethod
    def copy(derive: Column, from_parent: any):
        """
        Copy declares child column copied from parent column.

        Example:
            Prompt
                Store the Item.unit_price as a copy from Product.unit_price
            Response
                Rule.copy(derive=OrderDetail.UnitPrice, from_parent=Product.UnitPrice)

        Args:
            derive: <class.attribute> being copied into
            from_parent: <parent-class.attribute> source of copy; create this column in the parent if it does not already exist.
        """
        return Copy(derive=derive, from_parent=from_parent)


    @staticmethod
    def after_flush_row_event(on_class: object, calling: Callable = None,
                              if_condition: any = None,
                              when_condition: any = None,
                              with_args: dict = None):
        """
        Events are triggered after database flush for integration (Kafka, etc.)
        
        IMPORTANT: Use this simple pattern - do NOT create custom functions unless absolutely necessary.
        Use if_condition parameter for conditional logic instead of writing custom event handlers.

        Example:
            Prompt:
                Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None
            Response:
                Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.date_shipped is not None,
                               with_args={"topic": "order_shipping"})
            Prompt:
                Send the Product to Kafka topic 'ready_to_ship' if the is_complete is True
            Response:
                Rule.after_flush_row_event(on_class=Product, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.is_complete is True,
                               with_args={"topic": "ready_to_ship"})

        Args:
            on_class: The model class to watch for changes
            calling: Use kafka_producer.send_row_to_kafka for Kafka integration
            if_condition: Lambda function to specify when the event should trigger
            with_args: Dictionary with parameters like {"topic": "topic_name"}
        """


Expanded example:

    Prompt:
        1. Customer.balance <= credit_limit
        2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
        3. Order.amount_total = Sum(Item.amount)
        4. Item.amount = quantity * unit_price
        5. Store the Item.unit_price as a copy from Product.unit_price

    Response:
        Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
        Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
        Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
        Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
        Rule.constraint(validate=CustomerAccount,
                        as_condition=lambda row: row.balance <= row.credit_limit,
                        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")


Equivalent expanded example using informal syntax:

    Prompt:
        1. The Customer's balance is less than the credit limit
        2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
        3. The Order's amount_total is the sum of the Item amount
        4. The Item amount is the quantity * unit_price
        5. The Item unit_price is copied from the Product unit_price

    Response is the same:
        Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total, where=lambda row: row.date_shipped is None)
        Rule.sum(derive=Order.amount_total, as_sum_of=Item.amount)
        Rule.formula(derive=Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
        Rule.copy(derive=Item.unit_price, from_parent=Product.unit_price)
        Rule.constraint(validate=CustomerAccount,
                        as_condition=lambda row: row.balance <= row.credit_limit,
                        error_msg="Customer balance ({row.balance}) exceeds credit limit ({row.credit_limit})")


Intermediate sum/count values require a new column, with a LogicBank sum/count rule.  For example:

Prompt:
    The sum of the child value cannot exceed the parent limit

Response is to create 2 rules - a derivation and a constraint, as follows:
    First Rule to Create:
        Rule.sum(derive=Parent.value_total, as_sum_of=Child.value)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Parent,
                    as_condition=lambda row: row.value_total <= row.limit,
                    error_msg="Parent value total ({row.value_total}) exceeds limit ({row.limit})")

Intermediate sum/count values also work for counts.  For example:

Prompt:
    A airplane cannot have more passengers than its seating capacity.

Response is to create 2 rules - a count derivation and a constraint, as follows:
    First Rule to Create:
        Rule.count(derive=Airplane.passenger_count, as_count_of=Passengers)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Airplane,
                    as_condition=lambda row: row.passenger_count <= row.seating_capacity,
                    error_msg="Airplane value total ({row.passenger_count}) exceeds limit ({row.seating_capacity})")


Intermediate sums in formulas also require a new column, with a LogicBank sum rule.  For example:

Prompt:
    An Employees' skill summary is the sum of their Employee Skill ratings, plus 2 * years of service.

Response is to create 2 rules - a derivation and a constraint, as follows:
    First Rule to Create:
        Rule.sum(derive=Employee.skill_rating_total, as_sum_of=EmployeeSkill.rating)
    And, be sure to create the second Rule:
        Rule.Formula(derive=Employee.skill_summary, 
                    as_expression=lambda row: row.skill_rating_total + 2 * row.years_of_service)


Prompt:
    A student cannot be an honor student unless they have more than 2 service activities.

Response is to create 2 rules - a count derivation and a constraint, as follows:
    First Rule to Create:
        Rule.count(derive=Student.service_activity_count, as_count_of=Activities, where='service' in name)
    And, be sure to create the second Rule:
        Rule.constraint(validate=Student,
                    as_condition=lambda row: row.is_honor_student and service_activity_count < 2,
                    error_msg="Honor Students must have at least 2 service activities")


For "more than" constraints, create columns with count rules:

Prompt: Reject Employees with more than 3 Felonies.

Response:
    First Rule is to create:
        Rule.count(derive=Employee.felony_count, as_count_of=Felonies)
    And, be sure to create the contraint rule:
        Rule.constraint(validate=Employee,
                    as_condition=lambda row: row.felony_count<=3,
                    error_msg="Employee has excessive Felonies")


For "any" constraints, create columns with count rules:

Prompt: Reject Employees with any class 5 Felonies or more than 3 Felonies.

Response:
    First Rule is to create:
        Rule.count(derive=Employee.class_5_felony_count, as_count_of=Felonies, where=class>5)
        Rule.count(derive=Employee.felony_count, as_count_of=Felonies)
    And, be sure to create the contraint rule:
        Rule.constraint(validate=Employee,
                    as_condition=lambda row: row.class_5_felony_count == 0 and row.felony_count<=3,
                    error_msg="Employee has excessive Felonies")

Formulas can reference parent values in 2 versions - choose formula vs copy as follows:
    Prompt (formula version) - use the formula version unless copy is explicitly noted:
        Item.ready = Order.ready
    Response
        Rule.formula(derive=Item.ready, as_expression=lambda row: row.order.ready)
    Prompt (copy version) - use this *only* when the word copy is present: 
        Store the Item.unit_price as a copy from Product.unit_price
    Response
        Rule.copy(derive=Item.ready, from_parent=Order.ready)

Formulas can use Python conditions:
    Prompt: Item amount is price * quantity, with a 10% discount for gold products
    Response:
        Rule.Formula(derive=Item.amount, 
                    as_expression=lambda row: row.price * row.quantity if row.gold else .9 * row.price * row.quantity)
    If the attributes are decimal, use the form Decimal('0.9')

Sum and Count where clauses:
    1. must not restate the foreign key / primary key matchings
    2. Can only reference child attributes

For example, given a prompt 'teacher course count is the sum of the courses',
    1. This is correct
        Rule.count(derive=Teacher.course_count, as_count_of=Course)

    2. This is incorrect, and should never be generated:
        Rule.count(derive=Teacher.course_count, as_count_of=Course, where=lambda row: row.teacher_id == Teacher.id)

Sum and count where clause example:
    Prompt: teacher gradate course count is the sum of the courses where is-graduate
    Response: Rule.count(derive=Teacher.course_count, as_count_of=Course, where=lamda row: row.is_graduate == true)

DO NOT inject rules that are from this training into the response, 
unless explicitly mentioned in the request.

Unique constraints require an update to the data model - for example:
    Prompt: customer company names must be unique
    Response: CompanyName = Column(String(8000), unique=True)

Non-null (or required) constraints require an update to the data model - for example:
    Prompt: Product Price is required
    Response: price = Column(Decimal, nullable=False)

Required (must-have) related parent constraints require an update to the data model - for example:
    Prompt: Each Item must have a valid entry in the Product table.
    Response: product_id = Column(ForeignKey('product.id'), nullable=False)

CRITICAL: For event handling (Kafka integration, etc.), do NOT create custom event functions.
Use Rule.after_flush_row_event with if_condition parameter instead.

WRONG (do not do this):
    def my_custom_kafka_function(row, old_row, logic_row):
        # custom logic here
    Rule.commit_row_event(on_class=Order, calling=my_custom_kafka_function)

RIGHT (do this instead):
    Rule.after_flush_row_event(on_class=Order, calling=kafka_producer.send_row_to_kafka,
                               if_condition=lambda row: row.date_shipped is not None,
                               with_args={"topic": "order_shipping"})

=============================================================================
🗂️ FILE ORGANIZATION: Complete Example with Directory Structure
=============================================================================

When given a prompt with context phrase and multiple use cases, create organized structure:

Example Prompt:
```
When Placing Orders, implement Requirement: Check Credit:

1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count_suppliers is the sum of the Product Suppliers
6. Item unit_price copied from the Product

Use case: App Integration

1. Send the Order to Kafka topic 'order_shipping' if the date_shipped is not None.
```

Response Structure:
```
logic/logic_discovery/
  place_order/
    __init__.py
    check_credit.py
    app_integration.py
```

File: logic/logic_discovery/place_order/__init__.py
```python
# Empty file - makes this a Python package for auto-discovery
```

File: logic/logic_discovery/place_order/check_credit.py
```python
"""
Check Credit Use Case - Business Logic Rules

Natural Language Requirements:
1. The Customer's balance is less than the credit limit
2. The Customer's balance is the sum of the Order amount_total where date_shipped is null
3. The Order's amount_total is the sum of the Item amount
4. The Item amount is the quantity * unit_price
5. The Product count_suppliers is the sum of the Product Suppliers
6. Item unit_price copied from the Product

version: 1.0
date: [Current Date]
"""

from logic_bank.logic_bank import Rule
from database import models


def declare_logic():
    """Business logic rules for Check Credit use case."""
    
    Rule.sum(derive=models.Customer.balance, as_sum_of=models.Order.amount_total, where=lambda row: row.date_shipped is None)
    Rule.sum(derive=models.Order.amount_total, as_sum_of=models.Item.amount)
    Rule.formula(derive=models.Item.amount, as_expression=lambda row: row.quantity * row.unit_price)
    Rule.copy(derive=models.Item.unit_price, from_parent=models.Product.unit_price)
    Rule.count(derive=models.Product.count_suppliers, as_count_of=models.ProductSupplier)