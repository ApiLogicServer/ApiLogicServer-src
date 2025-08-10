from flask import request
from safrs import jsonapi_rpc
import safrs
from integration.row_dict_maps.OrderB2BMapper import OrderB2BMapper
import logging

app_logger = logging.getLogger("api_logic_server_app")

def add_service(app, api, project_dir, swagger_host: str, PORT: str, method_decorators = []):
    api.expose_object(OrderB2BEndPoint)

class OrderB2BEndPoint(safrs.JABase):
    @classmethod
    @jsonapi_rpc(http_methods=["POST"])
    def OrderB2B(self, *args, **kwargs):  # yaml comment => swagger description
        """ # yaml creates Swagger description
            args :
                data:
                    Account: "Alice"
                    Notes: "RUSH order for Q4 promotion"
                    Items :
                    - Name: "Widget"
                      QuantityOrdered: 5
                    - Name: "Gadget"
                      QuantityOrdered: 3
            ---
        
        Creates B2B orders from external partner systems with automatic lookups and business logic.
        Features automatic customer/product lookups by name, unit price copying, 
        amount calculations, customer balance updates, and credit limit validation.
        """
        db = safrs.DB
        session = db.session
        
        try:
            mapper_def = OrderB2BMapper()
            request_dict_data = request.json["meta"]["args"]["data"]
            
            app_logger.info(f"OrderB2B: Processing order for account: {request_dict_data.get('Account')}")
            
            sql_alchemy_row = mapper_def.dict_to_row(row_dict=request_dict_data, session=session)
            
            session.add(sql_alchemy_row)
            session.flush()  # Ensures ID is generated before accessing it
            
            order_id = sql_alchemy_row.id
            customer_name = sql_alchemy_row.customer.name if sql_alchemy_row.customer else "Unknown"
            item_count = len(sql_alchemy_row.ItemList)
            
            return {
                "message": "B2B Order created successfully", 
                "order_id": order_id,
                "customer": customer_name,
                "items_count": item_count
            }
            
        except Exception as e:
            app_logger.error(f"OrderB2B: Error creating order: {str(e)}")
            session.rollback()
            return {"error": "Failed to create B2B order", "details": str(e)}, 400
