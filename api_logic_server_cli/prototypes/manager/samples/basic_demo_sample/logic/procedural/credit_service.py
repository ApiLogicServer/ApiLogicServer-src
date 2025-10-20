from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.northwind import Customer, Order, OrderDetail, Product
from typing import Dict, Any, Optional
from decimal import Decimal

class CreditService:
    """Service class for credit checking business logic"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_item_amount(self, quantity: int, unit_price: Decimal) -> Decimal:
        """
        Calculate item amount: quantity * unit_price
        
        Args:
            quantity: Number of units
            unit_price: Price per unit
            
        Returns:
            Total amount for the item
        """
        if quantity is None or unit_price is None:
            return Decimal('0.00')
        return Decimal(str(quantity)) * Decimal(str(unit_price))
    
    def calculate_order_amount_total(self, order_id: int) -> Decimal:
        """
        Calculate order amount_total as sum of all item amounts in the order
        
        Args:
            order_id: Order ID to calculate total for
            
        Returns:
            Total amount for the order
        """
        order_details = self.session.query(OrderDetail, Product)\
            .join(Product, OrderDetail.ProductId == Product.Id)\
            .filter(OrderDetail.OrderId == order_id)\
            .all()
        
        total = Decimal('0.00')
        for order_detail, product in order_details:
            # Use product's current unit price if order detail doesn't have one
            unit_price = order_detail.UnitPrice or product.UnitPrice
            quantity = order_detail.Quantity or 0
            
            item_amount = self.calculate_item_amount(quantity, unit_price)
            
            # Apply discount if any
            if order_detail.Discount:
                discount_factor = Decimal('1.00') - (Decimal(str(order_detail.Discount)) / Decimal('100'))
                item_amount *= discount_factor
            
            total += item_amount
        
        return total
    
    def calculate_customer_balance(self, customer_id: str) -> Decimal:
        """
        Calculate customer balance as sum of Order amount_total where date_shipped is null
        
        Args:
            customer_id: Customer ID to calculate balance for
            
        Returns:
            Current outstanding balance for the customer
        """
        # Get all unshipped orders for the customer
        unshipped_orders = self.session.query(Order)\
            .filter(Order.CustomerId == customer_id)\
            .filter(Order.ShippedDate.is_(None))\
            .all()
        
        total_balance = Decimal('0.00')
        
        for order in unshipped_orders:
            # Calculate the order total if not already calculated
            if order.AmountTotal is not None:
                order_total = Decimal(str(order.AmountTotal))
            else:
                order_total = self.calculate_order_amount_total(order.Id)
                # Update the order with calculated total
                order.AmountTotal = float(order_total)
            
            total_balance += order_total
        
        # Commit any updates to order totals
        self.session.commit()
        
        return total_balance
    
    def check_credit_limit(self, customer_id: str) -> Dict[str, Any]:
        """
        Check if customer's balance is less than credit limit
        
        Args:
            customer_id: Customer ID to check credit for
            
        Returns:
            Dictionary containing credit check results
        """
        customer = self.session.query(Customer).filter(Customer.Id == customer_id).first()
        
        if not customer:
            return {
                'success': False,
                'error': 'Customer not found',
                'customer_id': customer_id
            }
        
        # Calculate current balance
        current_balance = self.calculate_customer_balance(customer_id)
        
        # Get credit limit
        credit_limit = Decimal(str(customer.CreditLimit)) if customer.CreditLimit else Decimal('0.00')
        
        # Check if balance is within credit limit
        credit_available = credit_limit - current_balance
        within_limit = current_balance <= credit_limit
        
        return {
            'success': True,
            'customer_id': customer_id,
            'customer_name': customer.CompanyName,
            'current_balance': float(current_balance),
            'credit_limit': float(credit_limit),
            'credit_available': float(credit_available),
            'within_credit_limit': within_limit,
            'balance_percentage': float((current_balance / credit_limit * 100) if credit_limit > 0 else 0),
            'unshipped_order_count': self.session.query(Order)
                                                .filter(Order.CustomerId == customer_id)
                                                .filter(Order.ShippedDate.is_(None))
                                                .count()
        }
    
    def get_credit_status_summary(self, customer_id: str) -> Dict[str, Any]:
        """
        Get comprehensive credit status including order details
        
        Args:
            customer_id: Customer ID to get status for
            
        Returns:
            Detailed credit status information
        """
        credit_check = self.check_credit_limit(customer_id)
        
        if not credit_check['success']:
            return credit_check
        
        # Get unshipped orders with details
        unshipped_orders = self.session.query(Order)\
            .filter(Order.CustomerId == customer_id)\
            .filter(Order.ShippedDate.is_(None))\
            .order_by(Order.OrderDate.desc())\
            .all()
        
        orders_details = []
        for order in unshipped_orders:
            order_total = self.calculate_order_amount_total(order.Id)
            orders_details.append({
                'order_id': order.Id,
                'order_date': order.OrderDate,
                'required_date': order.RequiredDate,
                'amount_total': float(order_total),
                'freight': float(order.Freight) if order.Freight else 0,
                'ship_name': order.ShipName,
                'order_detail_count': order.OrderDetailCount or 0
            })
        
        credit_check['unshipped_orders'] = orders_details
        return credit_check
    
    def update_order_amounts(self, order_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Update order amount totals based on current order details and product prices
        
        Args:
            order_id: Specific order to update, or None to update all orders
            
        Returns:
            Update results
        """
        if order_id:
            orders = self.session.query(Order).filter(Order.Id == order_id).all()
        else:
            orders = self.session.query(Order).all()
        
        updated_count = 0
        for order in orders:
            new_total = self.calculate_order_amount_total(order.Id)
            if order.AmountTotal != float(new_total):
                order.AmountTotal = float(new_total)
                updated_count += 1
        
        self.session.commit()
        
        return {
            'success': True,
            'updated_orders': updated_count,
            'total_orders_processed': len(orders)
        }
