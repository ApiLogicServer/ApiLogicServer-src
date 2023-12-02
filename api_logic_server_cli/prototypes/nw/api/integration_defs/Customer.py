from api.system.integration_services import IntegrationServices
from database import models
from flask import request, jsonify
from sqlalchemy import Column
from database.models import Order

class Customer(IntegrationServices):

    def __init__(self):
        customer = super(Customer, self).__init__(
            model_class=models.Customer
            , alias="customers"
            , fields = [models.Customer.Id, (models.Customer.CompanyName, "Customer Name")] 
            , related = 
                IntegrationServices(model_class=Order
                    , alias = "orders"
                    , fields = [Order.Id, (Order.AmountTotal, "Total"), (Order.ShippedDate, "Ship Date")]  # FIXME fails , Order.Employee.LastName]
                    , related = IntegrationServices(model_class=models.OrderDetail, alias="details"
                        , fields = [models.OrderDetail.Quantity, models.OrderDetail.Amount]
                        , related = IntegrationServices(model_class=models.Product, alias="product"
                            , fields=[models.Product.ProductName, models.Product.UnitPrice, models.Product.UnitsInStock]
                            , isParent=True
                            , isCombined=True
                        )
                    )
                )
            )
        return customer
