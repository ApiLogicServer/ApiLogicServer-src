from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from .models import Customer, Order, Item, Product


class OrderRejected(Exception):
    """Raised when an order cannot be placed (e.g. exceeds credit limit)."""


def place_order(db: Session, customer_id: int, notes: str, line_items: list[dict]) -> Order:
    """
    line_items: list of {"product_id": int, "quantity": int}

    Business rules (hand-written, no rules engine):
      1. For each line item, look up the product's price and multiply by quantity
         to get the item's amount.
      2. Sum item amounts to get the order's total.
      3. Add the order total to the customer's balance.
      4. Reject the order if that would push the balance over the credit limit.
    """
    customer = db.query(Customer).filter(Customer.id == customer_id).with_for_update(read=False).first()
    if customer is None:
        raise OrderRejected(f"Customer {customer_id} not found")

    if not line_items:
        raise OrderRejected("Order must have at least one line item")

    order = Order(customer_id=customer_id, notes=notes, CreatedOn=date.today())

    order_total = Decimal("0")
    items = []
    for line in line_items:
        product = db.query(Product).filter(Product.id == line["product_id"]).first()
        if product is None:
            raise OrderRejected(f"Product {line['product_id']} not found")

        quantity = int(line["quantity"])
        if quantity <= 0:
            raise OrderRejected("Quantity must be greater than zero")

        unit_price = product.unit_price
        amount = unit_price * quantity
        order_total += amount

        items.append(
            Item(
                product_id=product.id,
                quantity=quantity,
                unit_price=unit_price,
                amount=amount,
            )
        )

    new_balance = (customer.balance or Decimal("0")) + order_total
    if new_balance > customer.credit_limit:
        raise OrderRejected(
            f"Order rejected: order total {order_total} would bring "
            f"{customer.name}'s balance to {new_balance}, exceeding their "
            f"credit limit of {customer.credit_limit}"
        )

    order.amount_total = order_total
    order.items = items
    customer.balance = new_balance

    db.add(order)
    db.commit()
    db.refresh(order)
    return order
