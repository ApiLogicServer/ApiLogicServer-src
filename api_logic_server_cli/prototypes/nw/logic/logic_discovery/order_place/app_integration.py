"""
Use case: App Integration

Demonstrate that logic == Rules + Python (for extensibility).
"""

from logic_bank.exec_row_logic.logic_row import LogicRow
from logic_bank.logic_bank import Rule
from database.models import *
import integration.kafka.kafka_producer as kafka_producer
from integration.n8n.n8n_producer import send_n8n_message
from integration.row_dict_maps.OrderShipping import OrderShipping


def declare_logic():

    def send_order_to_shipping(row: Order, old_row: Order, logic_row: LogicRow):
        """ #als: Send Kafka message formatted by OrderShipping RowDictMapper

        Format row per shipping requirements, and send (e.g., a message)

        NB: the after_flush event makes Order.Id available.  Contrast to congratulate_sales_rep().

        Args:
            row (Order): inserted Order
            old_row (Order): n/a
            logic_row (LogicRow): bundles curr/old row, with ins/upd/dlt logic
        """
        if (logic_row.is_inserted() and row.Ready == True) or \
            (logic_row.is_updated() and row.Ready == True and old_row.Ready == False):
            kafka_producer.send_kafka_message(logic_row=logic_row,
                                              row_dict_mapper=OrderShipping,  # omit to just send order header
                                              kafka_topic="order_shipping",
                                              kafka_key=str(row.Id),
                                              msg="Sending Order to Shipping")

        """ #als: Send N8N message (also see discovery/integration.py)
        Workflow:  When Order is inserted = post n8n Webhook and call sendgrid email system
        """
        if logic_row.is_updated() and row.Ready == True and old_row.Ready == False:
            send_n8n_message(payload={
                                    "Order Id": row.Id,
                                    "Customer Name": row.Customer.CompanyName,
                                    "Order Total": str(row.AmountTotal),
                                    "Order Date": row.OrderDate,
                                    #"items": [row.OrderDetailList]
                                },
                                ins_upd_dlt="upd", wh_entity="Order",
                                msg="1. /Webhook integration.py: n8n, sending ready Order payload")

        logic_row.log("send_order_to_shipping - sent order to shipping and N8N/sendgrid")  # see in log


    Rule.after_flush_row_event(on_class=Order, calling=send_order_to_shipping)  # see above


    def congratulate_sales_rep(row: Order, old_row: Order, logic_row: LogicRow):
        """ use events for sending email, messages, etc. """
        if logic_row.ins_upd_dlt == "ins":  # logic engine fills parents for insert
            sales_rep = row.Employee        # parent accessor
            if sales_rep is None:           # breakpoint here
                logic_row.log("no salesrep for this order")
            elif sales_rep.Manager is None:
                logic_row.log("no manager for this order's salesrep")
            else:
                logic_row.log(f'Hi, {sales_rep.Manager.FirstName} - '
                              f'Congratulate {sales_rep.FirstName} on their new order')
            category_1 = logic_row.session.query(Category).filter(Category.Id == 1).one()
            logic_row.log("Illustrate database access")  # not granted for user: u2
            # Note: *Client* access is subject to authorization
            #       *Logic* is system code, not subject to authorization

    Rule.commit_row_event(on_class=Order, calling=congratulate_sales_rep)
