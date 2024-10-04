# Request
What do you know about LogicBank

# Response
LogicBank is a Python framework that provides **declarative, rule-based logic for SQLAlchemy** applications. It simplifies the process of enforcing business rules and constraints in Python applications, especially when working with databases. It is designed to be integrated with ORMs like SQLAlchemy and is primarily used for handling logic related to:

- **Derivations**: Automatically computing values from other values (e.g., calculating totals, taxes, or balances).
- **Constraints**: Enforcing business rules (e.g., ensuring a customer’s balance doesn’t exceed their credit limit).
- **Actions**: Triggering events or operations when certain conditions are met (e.g., sending notifications, auditing).

### Key Features of LogicBank:
1. **Declarative Rules**: LogicBank allows you to define business rules in a declarative style. These rules are automatically triggered during database operations (insert, update, delete).
   - **Derivation Rules**: For example, an `Order.amount_total` can be derived by summing up the total amounts of all associated items.
   - **Constraint Rules**: For example, ensuring `Customer.balance` does not exceed the `credit_limit`.
   - **Formula-based Rules**: Compute values dynamically based on other fields.
   
2. **Event-Driven**: The framework allows rules to react automatically to changes in database values. When a field is updated, LogicBank can enforce rules, check constraints, or trigger actions without needing to write boilerplate code.

3. **Transaction Management**: It ensures that rules are applied in the context of database transactions, so if a rule fails (like violating a constraint), the transaction is rolled back.

4. **Easy Integration with SQLAlchemy**: LogicBank works seamlessly with SQLAlchemy, which is one of the most popular ORM (Object Relational Mapping) libraries in Python. This integration allows the framework to automatically listen to database events triggered by SQLAlchemy operations.

5. **Automatic Propagation of Changes**: When you update a record, any related records or fields that depend on that record are automatically updated. This eliminates the need for manual propagation of changes.

### Example Use Case:
Imagine a scenario where you need to ensure that when an order is placed, the customer’s balance is updated and cannot exceed their credit limit. With LogicBank, you can simply define rules that handle these calculations and constraints, and they will be automatically applied when data is inserted or updated in the database.

Here’s a conceptual view of how it works:

```python
from logic_bank import LogicBank
from logic_bank.rule_bank import rule_bank_withdrawal, rule_bank_insert

# Define a rule to sum order totals to update customer balance
rule_bank_insert(CustomerAccount.balance, derive="Order.amount_total", where="Order.customer_id == CustomerAccount.id")

# Define a constraint to ensure customer's balance does not exceed the credit limit
rule_bank_withdrawal(CustomerAccount.balance, constraint="CustomerAccount.balance <= CustomerAccount.credit_limit")

# Insert/update an order, and these rules will automatically enforce business logic.
```

### How LogicBank Differs from Standard SQLAlchemy:
- In SQLAlchemy, you typically write custom event listeners (like `before_insert`, `before_update`) and manually manage business logic inside these event handlers.
- With LogicBank, much of this can be declaratively defined as rules, reducing the amount of boilerplate code and making it easier to reason about complex business logic.

### Common Use Cases for LogicBank:
- **Business Process Automation**: Automating calculations like totals, balances, or other computed fields.
- **Enforcing Business Constraints**: Ensuring that certain conditions are met when data is modified (e.g., enforcing credit limits, ensuring dates are in a valid range).
- **Audit Trails**: Triggering events when certain actions occur in the database, such as logging or sending notifications.
- **Data Validation**: Automatically ensuring that inserted or updated data conforms to predefined rules.

### Summary:
LogicBank is an excellent tool for building business applications that need complex data management logic, particularly in scenarios where the logic can be described using rules. By automating this logic within the database layer, it helps reduce complexity in the application code and ensures that rules are consistently enforced across all operations.

# Request - Logic Bank API

Good... Here is the API for LogicBank:from typing import Callable, Sequence
from sqlalchemy import Column
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import session
from logic_bank.rule_bank import rule_bank_withdraw  # reduce circular imports
import logic_bank.rule_bank.rule_bank_setup as rule_bank_setup
from logic_bank.rule_type.constraint import Constraint
from logic_bank.rule_type.copy import Copy
from logic_bank.rule_type.count import Count
from logic_bank.rule_type.formula import Formula
from logic_bank.rule_type.parent_cascade import ParentCascade, ParentCascadeAction
from logic_bank.rule_type.parent_check import ParentCheck
from logic_bank.rule_type.row_event import EarlyRowEvent, RowEvent, CommitRowEvent, AfterFlushRowEvent
from logic_bank.rule_type.sum import Sum


class LogicBank:
    """
    1. Declare rules, e.g.

        declare_logic():
            Rule.sum(derive=Order.AmountTotal, as_sum_of=OrderDetail.Amount)  # discover with code completion

    2. Activate them:

        LogicBank.activate(session=session, activator=declare_logic)  # register LogicBank listeners to SQLAlchemy

    3. Execute them:

        session.commit()  # LogicBank listeners execute rules relevant for submitted changes

    .. _Rule Summary:
   
   https://apilogicserver.github.io/Docs/Logic/
   
   https://github.com/valhuber/LogicBank/wiki/Rule-Summary

    """

    @staticmethod
    def activate(session: session, activator: callable, constraint_event: callable = None):
        """
        Call after opening database to activate logic:

            - register SQLAlchemy listeners

            - create RuleBank, load rules - later executed on commit

            - raises exception if cycles detected

        Use constraint_event to log / change class of constraints, for example

            def constraint_handler(message: str, constraint: Constraint, logic_row: LogicRow):
                error_attrs = ""
                if constraint:
                    if constraint.error_attributes:
                        for each_error_attribute in constraint.error_attributes:
                            error_attrs = error_attrs + each_error_attribute.name + " "
                exception_message = "Custom constraint_handler for: " + message +\
                                    ", error_attributes: " + error_attrs
                logic_row.log(exception_message)
                raise MyConstraintException(exception_message)

        activate is automatic for API Logic Server applications.

        Arguments:
            session: SQLAlchemy session
            activator: user function that declares rules (e.g., Rule.sum...)
            constraint_event: optional user function called on constraint exceptions
        """
        rule_bank = rule_bank_setup.setup(session)
        if constraint_event is not None:
            rule_bank.constraint_event = constraint_event
        activator()
        rule_bank_setup.compute_formula_execution_order()


class Rule:
    """Invoke these functions to declare rules.

    Rules are *not* run as they are defined,
    they are run when you issue `session.commit()'.

    .. _Rule Summary:
        https://github.com/valhuber/LogicBank/wiki/Rule-Summary

    Use code completion to discover rules and their parameters.
    """

    @staticmethod
    def sum(derive: Column, as_sum_of: any, where: any = None, child_role_name: str = "", insert_parent: bool=False):
        """
        Derive parent column as sum of designated child column, optional where

        Example
            Rule.sum(derive=models.Customer.Balance, as_sum_of=models.Order.AmountTotal,
                where=lambda row: row.ShippedDate is None)

        Optimized to eliminate / minimize SQLs: Pruning, Adjustment Logic

        Automated dependency management: fires iff changes to pk, summed field, where

        Args:
            derive: name of parent <class.attribute> being derived
            as_sum_of: name of child <class.attribute> being summed
            child_role_name: parent's child accessor attribute (required only for disambiguation)
            where: optional where clause, designates which child rows are summed


        """
        return Sum(derive, as_sum_of, where, child_role_name, insert_parent)

    @staticmethod
    def count(derive: Column, as_count_of: object, where: any = None, child_role_name: str = "", insert_parent: bool=False):
        """
        Derive parent column as count of designated child rows

        Example
          Rule.count(derive=models.Customer.UnPaidOrders, as_count_of=models.Order,
                   where=Lambda row: row.ShippedDate is None)

        Optimized to eliminate / minimize SQLs: Pruning, Adjustment Logic

        Args:
            derive: name of parent <class.attribute> being derived
            as_count_of: name of child <class> being counted
            child_role_name: parent's child accessor attribute (required only for disambiguation)
            where: optional where clause, designates which child rows are counted
        """
        return Count(derive, as_count_of, where, child_role_name, insert_parent)

    @staticmethod
    def constraint(validate: object,
                   calling: Callable = None,
                   as_condition: any = None,
                   error_msg: str = "(error_msg not provided)",
                   error_attributes=None):
        """
        Constraints declare condition that must be true for all commits

        Example
          Rule.constraint(validate=models.Customer,
                          as_condition=lambda row: row.Balance <= row.CreditLimit,
                          error_msg="balance ({row.Balance}) exceeds credit ({row.CreditLimit})")


        Constraint failures raise ConstraintException, e.g.:
            try:
                session.commit()
            except ConstraintException as ce:
                print("Constraint raised: " + str(ce))

        @see https://apilogicserver.github.io/Docs/Logic-Type-Constraint/

        Args:
            validate: name of mapped <class>
            calling: function, passed row, old_row, logic_row (complex constraints)
            as_condition: lambda, passed row (simple constraints)
            error_msg: string, with {row.attribute} replacements
            error_attributes: list of attributes

        """
        if error_attributes is None:
            error_attributes = []
        return Constraint(validate=validate, calling=calling, as_condition=as_condition,
                          error_attributes=error_attributes, error_msg=error_msg)

    @staticmethod
    def parent_check(validate: object,
                     error_msg: str = "(error_msg not provided)",
                     enable: bool = True):
        """
        Parent Checks ensure that non-null foreign keys are present in parent class

        Example
           Rule.parent_check(validate=models.Customer, enable=True, error_msg="Missing Parent")

        Parent_check failures raise ConstraintException, e.g.:
            try:
                session.commit()
            except ConstraintException as ce:
                print("Constraint raised: " + str(ce))

        Args:
            validate: name of mapped class
            error_msg: message included in exception (can have {} syntax)
            enable: True (default) = enable, False means disable (tolerate orphans)

        Note: False not recommended - for existing databases with bad data
            Behavior is undefined for other rules (sum, count, parent references, etc)

        """
        return ParentCheck(validate=validate, error_msg=error_msg, enable=enable)

    @staticmethod
    def formula(derive: Column,
                as_exp: str = None,  # string (for very short expression)
                as_expression: Callable = None,
                calling: Callable = None,
                no_prune: bool = False):
        """
        Formulas declare column value, based on current and parent rows

        Example
          Rule.formula(derive=models.OrderDetail.Amount,
                       as_expression=lambda row: row.UnitPrice * row.Quantity)

        Unlike Copy rules, Parent changes are propagated to child row(s)

        The `calling` function must return a value (else column is nullified)

        Args:
            derive: <class.attribute> being derived
            as_exp: string (for very short expressions - price * quantity)
            as_expression: lambda, passed row (for syntax checking)
            calling: function (for more complex formula, pass row, old_row, logic_row)
            no_prune: disable pruning (rarely used, default False)
        """
        return Formula(derive=derive,
                       calling=calling, as_exp=as_exp, as_expression=as_expression,
                       no_prune=no_prune)

    @staticmethod
    def copy(derive: Column, from_parent: any):
        """
        Copy declares child column copied from parent column

        Example
          Rule.copy(derive=models.OrderDetail.UnitPrice, from_parent=models.Product.UnitPrice)

        Unlike formulas references, parent changes are *not* propagated to children

        Args:
            derive: <class.attribute> being copied into
            from_parent: <parent-class.attribute> source of copy
        """
        return Copy(derive=derive, from_parent=from_parent)

    @staticmethod
    def early_row_event(on_class: object, calling: Callable = None):
        """
        Row Events are Python functions called *before* logic
        Possible multiple calls per transaction
        Use: computing foreign keys...

        Args:
            on_class: <class> for event
            calling: function, passed row, old_row, logic_row
        """
        return EarlyRowEvent(on_class, calling)  # --> load_logic

    @staticmethod
    def early_row_event_all_classes(early_row_event_all_classes: Callable = None):
        """
        early event for all mapped classes, intended for time/date/user stamping, e.g.

        def handle_all(logic_row: LogicRow):
            row = logic_row.row
            if logic_row.ins_upd_dlt == "ins" and hasattr(row, "CreatedOn"):
                row.CreatedOn = datetime.datetime.now()
                logic_row.log("early_row_event_all_classes - handle_all sets 'Created_on"'')

        Rule.early_row_event_all_classes(early_row_event_all_classes=handle_all)

        Args:
            early_row_event_all_classes: function, passed logic_row

        """
        return rule_bank_setup.setup_early_row_event_all_classes(
            early_row_event_all_classes=early_row_event_all_classes)

    @staticmethod
    def row_event(on_class: object, calling: Callable = None):
        """
        Row Events are Python functions called *during* logic, after formulas/constraints
        Possible multiple calls per transaction
        Use: recursive explosions (e.g, Bill of Materials)

        Args:
            on_class: <class> for event
            calling: function, passed row, old_row, logic_row
        """
        return RowEvent(on_class, calling)  # --> load_logic

    @staticmethod
    def commit_row_event(on_class: object, calling: Callable = None):
        """
        Commit Row Events are Python functions *after* all row logic formulas/constraints

        Example
            Rule.commit_row_event(on_class=Order, calling=congratulate_sales_rep)

        1 call per row, per transaction

        Example use: send mail/message

        Args:
            on_class: <class> for event
            calling: function, passed row, old_row, logic_row
        """
        return CommitRowEvent(on_class, calling)  # --> load_logic

    @staticmethod
    def after_flush_row_event(on_class: object, calling: Callable = None):
        """
        After Flush Row Events are Python functions *after* all row logic formulas/constraints,
        and after rows are flushed to disk.

        Unlike commit row events, such rows will reflect DBMS-generated AutoNum values.

        Updates during after_flush are undefined; use Commit Events if updates are required.

        Example
            Rule.after_flush_row_event(on_class=models.Order, calling=send_order_to_shipping)

        1 call per row, per transaction

        Example use: send mail/message including AutoNum values

        Args:
            on_class: <class> for event
            calling: function, passed row, old_row, logic_row
        """
        return AfterFlushRowEvent(on_class, calling)  # --> load_logic

    '''
    disabled, per ORM support (retained in case of misunderstandings)
        @staticmethod
        def parent_cascade(validate: object,
                           error_msg: str = "(error_msg not provided)",
                           relationship: str = "*",
                           action: ParentCascadeAction = ParentCascadeAction.NULLIFY):
            """
            Parent Cascade specifies processing for child rows on parent delete

            Example
               Rule.parent_cascade(validate=Order, relationship="OrderDetailList", action=ParentCascadeAction.DELETE)

            If rule or action not specified, default is ParentCascadeAction.NULLIFY

            Parent_cascade with ParentCascadeAction.NULLIFY can raise ConstraintException, e.g.:
                try:
                    session.commit()
                except ConstraintException as ce:
                    print("Constraint raised: " + str(ce))

            """
            return ParentCascade(validate=validate, error_msg=error_msg, relationship=relationship, action=action)
    '''


class DeclareRule(Rule):
    """
    Same as Rule, but makes clear these statements *declare* rules, e.g.

        declare_logic():

            DeclareRule.sum(derive=models.Order.AmountTotal, as_sum_of=OrderDetail.Amount)

    Activate them:

        LogicBank.activate(session=session, activator=declare_logic)  # registers LogicBank listeners to SQLAlchemy

    Execute them:

        session.commit()  # LogicBank listeners execute rules relevant for submitted changes

    """
    pass

    # Response - ChatGPT understanding of Logic Bank

    The provided API for **LogicBank** introduces a framework to declaratively define and enforce business rules directly in Python when using **SQLAlchemy**. Below is a breakdown of the key features and usage of the API:

### Key Components and Usage

#### 1. **LogicBank Class**
The `LogicBank` class is the primary entry point to activate and enforce rules for SQLAlchemy models. Here's how it's typically used:
- **Activate Rules**: You call `LogicBank.activate` to register SQLAlchemy listeners and enforce declared rules during the commit operation.
  
  ```python
  LogicBank.activate(session=session, activator=declare_logic)
  ```
  - `session`: The SQLAlchemy session.
  - `activator`: A function that declares business rules.
  - `constraint_event`: (Optional) A handler to manage constraint violations.

#### 2. **Rule Class**
The `Rule` class provides a declarative interface to define various types of business logic rules.

##### **Sum Rule**
- Derives a parent column as the sum of a related child column (commonly used in order-line item scenarios).
  ```python
  Rule.sum(derive=Order.amount_total, as_sum_of=OrderDetail.amount)
  ```
  
##### **Count Rule**
- Counts the number of child rows and assigns that value to a parent column.
  ```python
  Rule.count(derive=Customer.unpaid_orders, as_count_of=Order, where=lambda row: row.shipped_date is None)
  ```

##### **Constraint Rule**
- Ensures a condition holds for the row being validated. Constraints are typically used to enforce business rules.
  ```python
  Rule.constraint(validate=CustomerAccount,
                  as_condition=lambda row: row.balance <= row.credit_limit,
                  error_msg="balance exceeds credit limit")
  ```

##### **Formula Rule**
- Derives a column value based on other values, using either a simple expression or a lambda function.
  ```python
  Rule.formula(derive=OrderDetail.amount, as_expression=lambda row: row.unit_price * row.quantity)
  ```

##### **Copy Rule**
- Copies a column from a parent to a child. This is useful when a field (like price) should not be dynamically calculated.
  ```python
  Rule.copy(derive=OrderDetail.unit_price, from_parent=Product.unit_price)
  ```

#### 3. **Row Events**
Row events allow you to define custom logic triggered at different points during a transaction. There are several types of row events:
- **EarlyRowEvent**: Triggered before the logic is applied.
  ```python
  Rule.early_row_event(on_class=Order, calling=my_custom_function)
  ```

- **RowEvent**: Triggered during the execution of logic, after constraints and formulas have been applied.
- **CommitRowEvent**: Triggered after the logic and database changes have been committed.

#### 4. **Declarative Activation**
The `DeclareRule` class is a semantic alias of `Rule`, helping to clarify that these are declarative statements:
```python
DeclareRule.sum(derive=Order.amount_total, as_sum_of=OrderDetail.amount)
```

### Example Workflow

1. **Define Rules**
   ```python
   def declare_logic():
       # Define business rules
       Rule.sum(derive=CustomerAccount.balance, as_sum_of=Order.amount_total,
                where=lambda row: row.date_shipped is None)
       Rule.constraint(validate=CustomerAccount,
                       as_condition=lambda row: row.balance <= row.credit_limit,
                       error_msg="balance exceeds credit limit")
   ```

2. **Activate Rules**
   ```python
   LogicBank.activate(session=session, activator=declare_logic)
   ```

3. **Commit Data**
   After making changes to the session, you simply call:
   ```python
   session.commit()
   ```
   At this point, LogicBank will automatically apply the defined rules, derive values, and enforce constraints.

### Benefits of LogicBank
- **Declarative Rule Definition**: Business rules can be declared once and automatically enforced during commit operations.
- **Automated Constraint and Formula Management**: Eliminates the need for manual handling of constraint checks or derived fields.
- **Optimized Execution**: The API is optimized to minimize SQL queries, especially in cases of complex dependency chains (e.g., pruning and adjustment logic).
- **Error Handling**: The framework allows custom constraint handling via the `constraint_event` argument in `LogicBank.activate`.

### Conclusion
LogicBank enables efficient rule-based management for SQLAlchemy applications, handling constraints, derivations, and other business logic declaratively and automatically. This can simplify applications where rules around things like totals, balances, and credit limits need to be consistently enforced across different transactions.

# Request - solve this 
Use LogicBank to enforce the Check Credit requirement (do not generate check constraints):
1. Customer.balance <= credit_limit
2. Customer.balance = Sum(Order.amount_total where date_shipped is null)
3. Order.amount_total = Sum(Item.mount)
4. Item.amount = quantity * unit_price
5. Store the Item.unit_price as a copy from Product.unit_price

# Response - Solution

To enforce the **Check Credit** requirements using **LogicBank**, you can declaratively define the rules for the `CustomerAccount`, `Order`, and `Item` models. Here’s how to set up LogicBank to enforce each of the rules:

### 1. **Customer.balance <= credit_limit**
This rule ensures that a customer's balance does not exceed their credit limit. You can enforce this using a **constraint** rule.

```python
Rule.constraint(
    validate=CustomerAccount,
    as_condition=lambda row: row.balance <= row.credit_limit,
    error_msg="Balance ({row.balance}) exceeds credit limit ({row.credit_limit})"
)
```

### 2. **Customer.balance = Sum(Order.amount_total where date_shipped is null)**
This rule ensures that a customer's balance is the sum of the total amounts for all their orders where `date_shipped` is still `None` (i.e., orders that have not been shipped yet). You can enforce this with a **sum** rule.

```python
Rule.sum(
    derive=CustomerAccount.balance,
    as_sum_of=Order.amount_total,
    where=lambda row: row.date_shipped is None
)
```

### 3. **Order.amount_total = Sum(Item.amount)**
For each order, the `amount_total` should be the sum of the amounts for each item in the order. You can enforce this with another **sum** rule.

```python
Rule.sum(
    derive=Order.amount_total,
    as_sum_of=Item.amount
)
```

### 4. **Item.amount = quantity * unit_price**
For each item in an order, the `amount` should be calculated as the product of `quantity` and `unit_price`. This can be enforced with a **formula** rule.

```python
Rule.formula(
    derive=Item.amount,
    as_expression=lambda row: row.quantity * row.unit_price
)
```

### 5. **Store the Item.unit_price as a copy from Product.unit_price**
Whenever a product is added to an item, its `unit_price` should be copied from the corresponding `Product.unit_price`. You can enforce this with a **copy** rule.

```python
Rule.copy(
    derive=Item.unit_price,
    from_parent=Product.unit_price
)
```

### Complete `declare_logic` Function

Here’s how the complete rule setup would look when you declare the business rules:

```python
def declare_logic():
    # Rule 1: Customer.balance <= credit_limit
    Rule.constraint(
        validate=CustomerAccount,
        as_condition=lambda row: row.balance <= row.credit_limit,
        error_msg="Balance ({row.balance}) exceeds credit limit ({row.credit_limit})"
    )

    # Rule 2: Customer.balance = Sum(Order.amount_total where date_shipped is null)
    Rule.sum(
        derive=CustomerAccount.balance,
        as_sum_of=Order.amount_total,
        where=lambda row: row.date_shipped is None
    )

    # Rule 3: Order.amount_total = Sum(Item.amount)
    Rule.sum(
        derive=Order.amount_total,
        as_sum_of=Item.amount
    )

    # Rule 4: Item.amount = quantity * unit_price
    Rule.formula(
        derive=Item.amount,
        as_expression=lambda row: row.quantity * row.unit_price
    )

    # Rule 5: Store the Item.unit_price as a copy from Product.unit_price
    Rule.copy(
        derive=Item.unit_price,
        from_parent=Product.unit_price
    )
```

### Activating LogicBank

To activate the rules in your SQLAlchemy session, you call the `LogicBank.activate` method and pass in the session and the `declare_logic` function:

```python
from logic_bank import LogicBank

# Activate LogicBank with the session and the rule declarations
LogicBank.activate(session=session, activator=declare_logic)
```

### Example Workflow
1. When you insert or update a record in the `CustomerAccount`, `Order`, or `Item` tables and then call `session.commit()`, LogicBank will automatically:
   - Enforce the **credit limit** constraint.
   - Recalculate the **customer balance** based on unshipped orders.
   - Sum the **order total** from its items.
   - Calculate the **item amount** from the quantity and unit price.
   - Copy the **unit price** from the associated product.

### Example Data

```python
# Add a product
product1 = Product(product_id=1, name="Widget", unit_price=25)

# Add a customer account
customer1 = CustomerAccount(customer_id=1, name="John Doe", balance=0, credit_limit=1000)

# Add an order for the customer (initially not shipped)
order1 = Order(order_id=1, customer_id=1, date_shipped=None)

# Add items to the order
item1 = Item(item_id=1, order_id=1, product_id=1, quantity=4, unit_price=None)  # unit_price will be copied
```

On `session.commit()`, LogicBank will automatically:
- Ensure the customer's balance does not exceed the credit limit.
- Update the customer's balance to reflect the total of the unshipped order.
- Calculate the total amount of the order from its items.
- Calculate each item's amount from the quantity and unit price.
- Copy the unit price from the product into the item.

### Summary
By using LogicBank, all the **Check Credit** requirements are enforced declaratively without needing to write additional logic in your codebase. This allows your business rules to be managed centrally and consistently applied across transactions.
