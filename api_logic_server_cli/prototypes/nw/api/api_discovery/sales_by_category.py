from flask import request, jsonify
import logging
import safrs
from sqlalchemy.orm import aliased
from sqlalchemy import func
from database.models import Category, Product, OrderDetail, Order

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    pass

    @app.route('/sales_by_category')
    def sales_by_category():
        """        
        Illustrates:
        * Complex query with multiple joins

        Test it with:
        
                curl -X GET "http://localhost:5656/sales_by_category"
        
        """
        db = safrs.DB           # Use the safrs.DB, not db!
        session = db.session    # sqlalchemy.orm.scoping.scoped_session
        # Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

        # Alias tables for better readability
        category = aliased(Category)
        product = aliased(Product)
        order_detail = aliased(OrderDetail)
        order = aliased(Order)

        # SQLAlchemy query for Sales by Category
        sales_by_category = (
            session.query(
                category.CategoryName,
                func.sum(order_detail.Quantity * order_detail.UnitPrice * (1 - order_detail.Discount)).label("TotalSales")
            )
            .join(product, category.Id == product.CategoryId)
            .join(order_detail, product.Id == order_detail.ProductId)
            .join(order, order_detail.OrderId == order.Id)
            .filter(order.ShippedDate.isnot(None))  # Consider only shipped orders
            .group_by(category.CategoryName)
            .order_by(func.sum(order_detail.Quantity * order_detail.UnitPrice * (1 - order_detail.Discount)).desc())
        )

        # Execute query and fetch results
        results = sales_by_category.all()
        return jsonify( { "result": results } )