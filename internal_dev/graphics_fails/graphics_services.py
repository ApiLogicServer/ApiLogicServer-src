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
Graphics methods for database classes, from 'Graph Sales by Category', etc.
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
@classmethod
@add_method(models.Region)
@jsonapi_rpc(http_methods=['GET', 'OPTIONS'])
def sales_by_region(*args, **kwargs):
    """        
    Complex query with multiple joins, for graphics, from 'Graph Sales by Category', etc.
    Test with Swagger.
    """
    if request.method == 'OPTIONS':
        return jsonify({ "result": "ok" })
        
    from database.models import Region, Order, OrderDetail, Customer
    db = safrs.DB
    session = db.session    # sqlalchemy.orm.scoping.scoped_session
    # Security.set_user_sa()  # an endpoint that requires no auth header (see also @bypass_security)

    # SQLAlchemy query  - this one FAILED
    query = sales_by_region = (session.query(Region.RegionDescription, func.sum(Order.AmountTotal).label("TotalSales")) 
                               .join(Order, Region.Id == Order.ShipRegion) 
                               .filter(Order.ShippedDate.isnot(None)) 
                               .group_by(Region.RegionDescription) 
                               .order_by(func.sum(Order.AmountTotal).desc()) ) 
    
    # it ran FINE later... hmm... are we in retries-mode?
    query = session.query(Region.RegionDescription, func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount)).label('TotalSales')
                          .join(Order, OrderDetail.OrderId == Order.Id)
                          .join(Customer, Order.CustomerId == Customer.Id)
                          .join(Region, Customer.Region == Region.RegionDescription)
                          .filter(Order.ShippedDate.isnot(None))
                          .group_by(Region.RegionDescription)
                          .order_by(func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount)).desc()) )

    # from earlier gen
    query = sales_by_region = (
    session.query(
        Region.RegionDescription.label("Region"),
        func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount)).label("TotalSales")
    )
    .join(Order, OrderDetail.OrderId == Order.Id)
    .join(Customer, Order.CustomerId == Customer.Id)
    .join(Region, Customer.Region == Region.RegionDescription)
    .filter(Order.ShippedDate.isnot(None))  # Consider only shipped orders
    .group_by(Region.RegionDescription)
    .order_by(func.sum(OrderDetail.Quantity * OrderDetail.UnitPrice * (1 - OrderDetail.Discount)).desc())
) 
    


    # Execute query and fetch results
    results = query.all()
    from decimal import Decimal
    columns = ['RegionDescription', 'TotalSales']  # Region Total Sales
    results = [{columns[0]: row[0], columns[1]: str(Decimal(row[1]).quantize(Decimal('0.01')))} for row in results]
    title = "Sales by Region" # Sales by Region
    chart_type = 'bar' # 
    json_results = {
        "results": results,
        "columns": columns,
        "title": title,
        "chart_type": "bar",
        "xAxis": columns[0],
        "yAxis": columns[1],
    }
    
    return json_results 