import sqlalchemy
from sqlalchemy import create_engine, inspect, MetaData
from sqlalchemy.orm import Session
import models

    # *******************************************
    # Use this to inspect SQLAlchemy2 connection
    # *******************************************

def print_meta(meta):
    print("\n\nmeta.sorted_tables (meta = models.metadata.sorted_tables)\n")
    for each_table in meta.sorted_tables:
        print(f'\n{each_table.key}')
        for each_column in each_table.columns:
            print(f'\t{each_column.name}')

db_url = "sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/servers/ApiLogicProject/database/db.sqlite"
# db_url = "sqlite:////Users/val/dev/servers/ApiLogicProject/database/nw-gold.sqlite"

e = sqlalchemy.create_engine(db_url)
inspector = inspect(e)
conn = e.connect()

with Session(e) as session:
    print(f'session: {session}')
    # metadata = MetaData(bind=e)
    metadata = MetaData()  # SQLAlchemy2
    meta = models.metadata  # tables should show list of db tables
    print_meta(meta)
    print("\n\n")

    """
    Caution - use of debugger may result in "no app context"
    https://stackoverflow.com/questions/34122949/working-outside-of-application-context-flask
    """
    order_id = 10643
    order : models.Order = session.query(models.Order).filter(models.Order.Id == order_id).one()
    # hover to view code completion...
    print(f'Order: {order.Id}, AmountTotal: {order.AmountTotal}, ready: {order.Ready}, Required: {order.RequiredDate}, Customer: {order.CustomerId}, Balance: {order.Customer.Balance}\n\n')
    order.AmountTotal

    departments = session.query(models.Department).all()
    for each_dept in departments:
        print(f'\nDept: {each_dept}')
        for each_works_for_emp in each_dept.EmployeeList1:
            print(f'...each_works_for_emp: {each_works_for_emp}')
        print("")
        for each_on_loan_emp in each_dept.EmployeeList:
            print(f'...each_on_loan_emp: {each_on_loan_emp}')
        print("")
        for each_sub_dept in each_dept.DepartmentList:
            print(f'...each_sub_dept: {each_sub_dept}')

