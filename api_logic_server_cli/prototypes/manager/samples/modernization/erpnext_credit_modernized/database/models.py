# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Column, Float, ForeignKey, Integer, Numeric, Text, UniqueConstraint, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  October 29, 2026 18:18:32
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/erpnext_credit_modernized/database/db.sqlite
# Dialect:  sqlite
#
# mypy: ignore-errors
########################################################################################################################
 
from database.system.SAFRSBaseX import SAFRSBaseX, TestBase
from flask_login import UserMixin
import safrs, flask_sqlalchemy, os
from safrs import jsonapi_attr
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import NullType
from typing import List

db = SQLAlchemy() 
Base = declarative_base()  # type: flask_sqlalchemy.model.DefaultMeta
metadata = Base.metadata

#NullType = db.String  # datatype fixup
#TIMESTAMP= db.TIMESTAMP

from sqlalchemy.dialects.sqlite import *

if os.getenv('APILOGICPROJECT_NO_FLASK') is None or os.getenv('APILOGICPROJECT_NO_FLASK') == 'None':
    Base = SAFRSBaseX   # enables rules to be used outside of Flask, e.g., test data loading
else:
    Base = TestBase     # ensure proper types, so rules work for data loading
    print('*** Models.py Using TestBase ***')



class Company(Base):  # type: ignore
    __tablename__ = 'company'
    _s_collection_name = 'Company'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    credit_limit = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)

    # child relationships (access children)
    CustomerGroupCreditLimitList : Mapped[List["CustomerGroupCreditLimit"]] = relationship(back_populates="company")
    JournalEntryList : Mapped[List["JournalEntry"]] = relationship(back_populates="company")
    CustomerCompanyList : Mapped[List["CustomerCompany"]] = relationship(back_populates="company")
    SalesInvoiceList : Mapped[List["SalesInvoice"]] = relationship(back_populates="company")
    CustomerCreditLimitList : Mapped[List["CustomerCreditLimit"]] = relationship(back_populates="company")
    DeliveryNoteList : Mapped[List["DeliveryNote"]] = relationship(back_populates="company")
    LedgerEntryList : Mapped[List["LedgerEntry"]] = relationship(back_populates="company")
    SalesOrderList : Mapped[List["SalesOrder"]] = relationship(back_populates="company")



class CustomerGroup(Base):  # type: ignore
    __tablename__ = 'customer_group'
    _s_collection_name = 'CustomerGroup'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)

    # parent relationships (access parent)

    # child relationships (access children)
    CustomerList : Mapped[List["Customer"]] = relationship(back_populates="customer_group")
    CustomerGroupCreditLimitList : Mapped[List["CustomerGroupCreditLimit"]] = relationship(back_populates="customer_group")



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)
    credit_controller = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)



class Customer(Base):  # type: ignore
    __tablename__ = 'customer'
    _s_collection_name = 'Customer'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    customer_group_id = Column(ForeignKey('customer_group.id'), nullable=False)

    # parent relationships (access parent)
    customer_group : Mapped["CustomerGroup"] = relationship(back_populates=("CustomerList"))

    # child relationships (access children)
    CustomerCompanyList : Mapped[List["CustomerCompany"]] = relationship(back_populates="customer")
    JournalEntryAccountList : Mapped[List["JournalEntryAccount"]] = relationship(back_populates="customer")
    SalesInvoiceList : Mapped[List["SalesInvoice"]] = relationship(back_populates="customer")
    CustomerCreditLimitList : Mapped[List["CustomerCreditLimit"]] = relationship(back_populates="customer")
    DeliveryNoteList : Mapped[List["DeliveryNote"]] = relationship(back_populates="customer")
    LedgerEntryList : Mapped[List["LedgerEntry"]] = relationship(back_populates="customer")
    SalesOrderList : Mapped[List["SalesOrder"]] = relationship(back_populates="customer")



class CustomerGroupCreditLimit(Base):  # type: ignore
    __tablename__ = 'customer_group_credit_limit'
    _s_collection_name = 'CustomerGroupCreditLimit'  # type: ignore
    __table_args__ = (
        UniqueConstraint('customer_group_id', 'company_id'),
    )

    id = Column(Integer, primary_key=True)
    customer_group_id = Column(ForeignKey('customer_group.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    credit_limit = Column(Numeric(15, 2), server_default=text("0"))
    bypass_credit_limit_check = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("CustomerGroupCreditLimitList"))
    customer_group : Mapped["CustomerGroup"] = relationship(back_populates=("CustomerGroupCreditLimitList"))

    # child relationships (access children)



class JournalEntry(Base):  # type: ignore
    __tablename__ = 'journal_entry'
    _s_collection_name = 'JournalEntry'  # type: ignore

    id = Column(Integer, primary_key=True)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    docstatus = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("JournalEntryList"))

    # child relationships (access children)
    JournalEntryAccountList : Mapped[List["JournalEntryAccount"]] = relationship(back_populates="journal_entry")



class CustomerCompany(Base):  # type: ignore
    __tablename__ = 'customer_company'
    _s_collection_name = 'CustomerCompany'  # type: ignore
    __table_args__ = (
        UniqueConstraint('customer_id', 'company_id'),
    )

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    ledger_balance = Column(Numeric(15, 2), server_default=text("0"))
    open_sales_order_amount = Column(Numeric(15, 2), server_default=text("0"))
    unbilled_delivery_amount = Column(Numeric(15, 2), server_default=text("0"))
    outstanding = Column(Numeric(15, 2), server_default=text("0"))
    outstanding_ignoring_sales_orders = Column(Numeric(15, 2), server_default=text("0"))
    customer_credit_limit = Column(Numeric(15, 2), server_default=text("0"))
    bypass_credit_limit_check = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("CustomerCompanyList"))
    customer : Mapped["Customer"] = relationship(back_populates=("CustomerCompanyList"))

    # child relationships (access children)
    CustomerCreditLimitList : Mapped[List["CustomerCreditLimit"]] = relationship(back_populates="customer_company")
    DeliveryNoteList : Mapped[List["DeliveryNote"]] = relationship(back_populates="customer_company")
    LedgerEntryList : Mapped[List["LedgerEntry"]] = relationship(back_populates="customer_company")
    SalesOrderList : Mapped[List["SalesOrder"]] = relationship(back_populates="customer_company")



class JournalEntryAccount(Base):  # type: ignore
    __tablename__ = 'journal_entry_account'
    _s_collection_name = 'JournalEntryAccount'  # type: ignore

    id = Column(Integer, primary_key=True)
    journal_entry_id = Column(ForeignKey('journal_entry.id'), nullable=False)
    party_type = Column(Text)
    customer_id = Column(ForeignKey('customer.id'))
    debit = Column(Numeric(15, 2), server_default=text("0"))
    credit = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    customer : Mapped["Customer"] = relationship(back_populates=("JournalEntryAccountList"))
    journal_entry : Mapped["JournalEntry"] = relationship(back_populates=("JournalEntryAccountList"))

    # child relationships (access children)
    LedgerEntryList : Mapped[List["LedgerEntry"]] = relationship(back_populates="journal_entry_account")



class SalesInvoice(Base):  # type: ignore
    __tablename__ = 'sales_invoice'
    _s_collection_name = 'SalesInvoice'  # type: ignore

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    grand_total = Column(Numeric(15, 2), server_default=text("0"))
    is_return = Column(Integer, server_default=text("0"))
    is_opening = Column(Integer, server_default=text("0"))
    docstatus = Column(Integer, server_default=text("0"))
    unlinked_line_count = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("SalesInvoiceList"))
    customer : Mapped["Customer"] = relationship(back_populates=("SalesInvoiceList"))

    # child relationships (access children)
    LedgerEntryList : Mapped[List["LedgerEntry"]] = relationship(back_populates="sales_invoice")
    DeliveryNoteItemList : Mapped[List["DeliveryNoteItem"]] = relationship(back_populates="sales_invoice")
    SalesInvoiceItemList : Mapped[List["SalesInvoiceItem"]] = relationship(back_populates="sales_invoice")



class CustomerCreditLimit(Base):  # type: ignore
    __tablename__ = 'customer_credit_limit'
    _s_collection_name = 'CustomerCreditLimit'  # type: ignore
    __table_args__ = (
        UniqueConstraint('customer_id', 'company_id'),
    )

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    customer_company_id = Column(ForeignKey('customer_company.id'))
    credit_limit = Column(Numeric(15, 2), server_default=text("0"))
    bypass_credit_limit_check = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("CustomerCreditLimitList"))
    customer_company : Mapped["CustomerCompany"] = relationship(back_populates=("CustomerCreditLimitList"))
    customer : Mapped["Customer"] = relationship(back_populates=("CustomerCreditLimitList"))

    # child relationships (access children)



class DeliveryNote(Base):  # type: ignore
    __tablename__ = 'delivery_note'
    _s_collection_name = 'DeliveryNote'  # type: ignore

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    customer_company_id = Column(ForeignKey('customer_company.id'))
    grand_total = Column(Numeric(15, 2), server_default=text("0"))
    net_total = Column(Numeric(15, 2), server_default=text("0"))
    status = Column(Text, server_default=text("'Draft'"))
    is_return = Column(Integer, server_default=text("0"))
    per_billed = Column(Numeric(7, 4), server_default=text("0"))
    docstatus = Column(Integer, server_default=text("0"))
    unbilled_line_total = Column(Numeric(15, 2), server_default=text("0"))
    unbilled_amount = Column(Numeric(15, 2), server_default=text("0"))
    unlinked_line_count = Column(Integer, server_default=text("0"))
    no_invoice_line_count = Column(Integer, server_default=text("0"))
    uninvoiced_share = Column(Numeric(15, 2), server_default=text("0"))
    bypass_extra_amount = Column(Numeric(15, 2), server_default=text("0"))
    so_linked_uninvoiced_share = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("DeliveryNoteList"))
    customer_company : Mapped["CustomerCompany"] = relationship(back_populates=("DeliveryNoteList"))
    customer : Mapped["Customer"] = relationship(back_populates=("DeliveryNoteList"))

    # child relationships (access children)
    DeliveryNoteItemList : Mapped[List["DeliveryNoteItem"]] = relationship(back_populates="delivery_note")



class LedgerEntry(Base):  # type: ignore
    __tablename__ = 'ledger_entry'
    _s_collection_name = 'LedgerEntry'  # type: ignore

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    customer_company_id = Column(ForeignKey('customer_company.id'))
    debit = Column(Numeric(15, 2), server_default=text("0"))
    credit = Column(Numeric(15, 2), server_default=text("0"))
    is_cancelled = Column(Integer, server_default=text("0"))
    amount = Column(Numeric(15, 2), server_default=text("0"))
    sales_invoice_id = Column(ForeignKey('sales_invoice.id'))
    journal_entry_account_id = Column(ForeignKey('journal_entry_account.id'))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("LedgerEntryList"))
    customer_company : Mapped["CustomerCompany"] = relationship(back_populates=("LedgerEntryList"))
    customer : Mapped["Customer"] = relationship(back_populates=("LedgerEntryList"))
    journal_entry_account : Mapped["JournalEntryAccount"] = relationship(back_populates=("LedgerEntryList"))
    sales_invoice : Mapped["SalesInvoice"] = relationship(back_populates=("LedgerEntryList"))

    # child relationships (access children)



class SalesOrder(Base):  # type: ignore
    __tablename__ = 'sales_order'
    _s_collection_name = 'SalesOrder'  # type: ignore

    id = Column(Integer, primary_key=True)
    customer_id = Column(ForeignKey('customer.id'), nullable=False)
    company_id = Column(ForeignKey('company.id'), nullable=False)
    customer_company_id = Column(ForeignKey('customer_company.id'))
    grand_total = Column(Numeric(15, 2), server_default=text("0"))
    per_billed = Column(Numeric(7, 4), server_default=text("0"))
    status = Column(Text, server_default=text("'Draft'"))
    docstatus = Column(Integer, server_default=text("0"))
    open_amount = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    company : Mapped["Company"] = relationship(back_populates=("SalesOrderList"))
    customer_company : Mapped["CustomerCompany"] = relationship(back_populates=("SalesOrderList"))
    customer : Mapped["Customer"] = relationship(back_populates=("SalesOrderList"))

    # child relationships (access children)
    DeliveryNoteItemList : Mapped[List["DeliveryNoteItem"]] = relationship(back_populates="sales_order")
    SalesInvoiceItemList : Mapped[List["SalesInvoiceItem"]] = relationship(back_populates="sales_order")



class DeliveryNoteItem(Base):  # type: ignore
    __tablename__ = 'delivery_note_item'
    _s_collection_name = 'DeliveryNoteItem'  # type: ignore

    id = Column(Integer, primary_key=True)
    delivery_note_id = Column(ForeignKey('delivery_note.id'), nullable=False)
    qty = Column(Numeric(15, 4), server_default=text("0"))
    returned_qty = Column(Numeric(15, 4), server_default=text("0"))
    net_amount = Column(Numeric(15, 2), server_default=text("0"))
    sales_order_id = Column(ForeignKey('sales_order.id'))
    sales_invoice_id = Column(ForeignKey('sales_invoice.id'))
    billed_qty = Column(Numeric(15, 4), server_default=text("0"))
    unbilled_amount = Column(Numeric(15, 2), server_default=text("0"))
    grand_total_share = Column(Numeric(15, 2), server_default=text("0"))

    # parent relationships (access parent)
    delivery_note : Mapped["DeliveryNote"] = relationship(back_populates=("DeliveryNoteItemList"))
    sales_invoice : Mapped["SalesInvoice"] = relationship(back_populates=("DeliveryNoteItemList"))
    sales_order : Mapped["SalesOrder"] = relationship(back_populates=("DeliveryNoteItemList"))

    # child relationships (access children)
    SalesInvoiceItemList : Mapped[List["SalesInvoiceItem"]] = relationship(back_populates="delivery_note_item")



class SalesInvoiceItem(Base):  # type: ignore
    __tablename__ = 'sales_invoice_item'
    _s_collection_name = 'SalesInvoiceItem'  # type: ignore

    id = Column(Integer, primary_key=True)
    sales_invoice_id = Column(ForeignKey('sales_invoice.id'), nullable=False)
    qty = Column(Numeric(15, 4), server_default=text("0"))
    sales_order_id = Column(ForeignKey('sales_order.id'))
    delivery_note_item_id = Column(ForeignKey('delivery_note_item.id'))
    counts_as_billed = Column(Integer, server_default=text("0"))

    # parent relationships (access parent)
    delivery_note_item : Mapped["DeliveryNoteItem"] = relationship(back_populates=("SalesInvoiceItemList"))
    sales_invoice : Mapped["SalesInvoice"] = relationship(back_populates=("SalesInvoiceItemList"))
    sales_order : Mapped["SalesOrder"] = relationship(back_populates=("SalesInvoiceItemList"))

    # child relationships (access children)
