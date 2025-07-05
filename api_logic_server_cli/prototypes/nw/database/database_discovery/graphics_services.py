from database import models
import logging
from safrs import jsonapi_attr
from sqlalchemy.orm import relationship, remote, foreign
from functools import wraps # This convenience func preserves name and docstring
import decimal as decimal
from sqlalchemy import extract, func
from flask import request, jsonify
from safrs import jsonapi_rpc, SAFRSAPI
import safrs

"""
Graphics methods for database classes, created when: 
* `als genai create` contains prompts like: 'Graph Sales by Category', etc.
* `als add-graphics` --using the docs/graphics directory

Called by api/api_discovery/dashboard_services.py when admin app loaded

You typically do not alter this file - rebuilt on als genai--graphics.

"""

app_logger = logging.getLogger(__name__)


def add_method(cls):
  """
  Decorator to add method to class, e.g., db class group by query method

  Thanks to: https://mgarod.medium.com/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
  """
  def decorator(func):
    @wraps(func) 
    def wrapper(self, *args, **kwargs): 
      return func(*args, **kwargs)
    
    setattr(cls, func.__name__, wrapper)
    # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
    return func # returning func means func can still be used normally
  return decorator

##############################
# generated services follow
##############################



@classmethod
@add_method(models.Category)
@jsonapi_rpc(http_methods=['GET', 'OPTIONS'])
def sales_by_category(*args, **kwargs):
    """        
    Complex query with multiple joins, for graphics, from 'Graph Sales by Category', etc.
    Test with Swagger.
    """
    if request.method == 'OPTIONS':
        return jsonify({ "result": "ok" })
        
    from database.models import Category, Product, OrderDetail, Order
    db = safrs.DB
    session = db.session    # sqlalchemy.orm.scoping.scoped_session
    # Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

    # SQLAlchemy query
    query = sales_by_category = ((session.query(Category.CategoryName, func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount))
            .label("TotalSales"))
            .join(Product, Category.Id == Product.CategoryId)
            .join(OrderDetail, Product.Id == OrderDetail.ProductId)
            .join(Order, OrderDetail.OrderId == Order.Id)
            .filter(Order.ShippedDate.is_not(None))
            .group_by(Category.CategoryName)
            .order_by(func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount))
            .desc()))) 
    # Execute query and fetch results
    results = query.all()
    from decimal import Decimal
    columns = ['Category Name' , 'Total Sales']
    results = [{columns[0]: row[0], columns[1]: round(float(row[1]), 2)} for row in results]
    title = 'Sales by Category'
    graph_type = 'Bar'.lower()
    json_results = {
        "results": results,
        "columns": columns,
        "title": title,
        "chart_type": graph_type,
        "xAxis": columns[0],
        "yAxis": columns[1],
    }
    
    return json_results 
@classmethod
@add_method(models.Category)
@jsonapi_rpc(http_methods=['GET', 'OPTIONS'])
def number_of_sales_per_category(*args, **kwargs):
    """        
    Complex query with multiple joins, for graphics, from 'Graph Sales by Category', etc.
    Test with Swagger.
    """
    if request.method == 'OPTIONS':
        return jsonify({ "result": "ok" })
        
    from database.models import Category, Product, OrderDetail, Order
    db = safrs.DB
    session = db.session    # sqlalchemy.orm.scoping.scoped_session
    # Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

    # SQLAlchemy query
    query = number_of_sales_per_category = ((session.query(Category.CategoryName, func.count(Order.Id)
            .label("NumberOfSales"))
            .join(Product, Product.CategoryId == Category.Id)
            .join(OrderDetail, OrderDetail.ProductId == Product.Id)
            .join(Order, Order.Id == OrderDetail.OrderId)
            .filter(Order.ShippedDate.is_not(None))
            .group_by(Category.CategoryName)
            .order_by(func.count(Order.Id)
            .desc()))) 
    # Execute query and fetch results
    results = query.all()
    from decimal import Decimal
    columns = ['Category Name' , 'Number of Sales']
    results = [{columns[0]: row[0], columns[1]: round(float(row[1]), 2)} for row in results]
    title = 'Number of Sales Per Category'
    graph_type = 'Bar'.lower()
    json_results = {
        "results": results,
        "columns": columns,
        "title": title,
        "chart_type": graph_type,
        "xAxis": columns[0],
        "yAxis": columns[1],
    }
    
    return json_results 
@classmethod
@add_method(models.Order)
@jsonapi_rpc(http_methods=['GET', 'OPTIONS'])
def count_orders_by_month(*args, **kwargs):
    """        
    Complex query with multiple joins, for graphics, from 'Graph Sales by Category', etc.
    Test with Swagger.
    """
    if request.method == 'OPTIONS':
        return jsonify({ "result": "ok" })
        
    from database.models import Order
    db = safrs.DB
    session = db.session    # sqlalchemy.orm.scoping.scoped_session
    # Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

    # SQLAlchemy query
    query = count_orders_by_month = ((session.query(func.strftime('%Y-%m', func.date(Order.OrderDate))
            .label("OrderMonth"), func.count(Order.Id)
            .label("OrderCount"))
            .filter(Order.OrderDate.is_not(None))
            .group_by(func.strftime('%Y-%m', func.date(Order.OrderDate)))
            .order_by(func.strftime('%Y-%m', func.date(Order.OrderDate))))) 
    # Execute query and fetch results
    results = query.all()
    from decimal import Decimal
    columns = ['Month' , 'Order Count']
    results = [{columns[0]: row[0], columns[1]: round(float(row[1]), 2)} for row in results]
    title = 'Order Count by Month'
    graph_type = 'Line'.lower()
    json_results = {
        "results": results,
        "columns": columns,
        "title": title,
        "chart_type": graph_type,
        "xAxis": columns[0],
        "yAxis": columns[1],
    }
    
    return json_results 