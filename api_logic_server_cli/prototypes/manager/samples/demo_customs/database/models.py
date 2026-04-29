# coding: utf-8
from sqlalchemy import DECIMAL, DateTime  # API Logic Server GenAI assist
from sqlalchemy import Boolean, Column, DECIMAL, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text, text
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

########################################################################################################################
# Classes describing database for SqlAlchemy ORM, initially created by schema introspection.
#
# Alter this file per your database maintenance policy
#    See https://apilogicserver.github.io/Docs/Project-Rebuild/#rebuilding
#
# Created:  April 29, 2026 13:52:58
# Database: sqlite:////Users/val/dev/ApiLogicServer/ApiLogicServer-dev/build_and_test/genai-logic/demo_customs/database/db.sqlite
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



class CcpCustomer(Base):  # type: ignore
    __tablename__ = 'ccp_customer'
    _s_collection_name = 'CcpCustomer'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    address1 = Column(String(50))
    address2 = Column(String(50))
    city = Column(String(30))
    state = Column(String(10))
    country = Column(String(3))
    postal = Column(String(15))
    business_nbr = Column(String(20))
    gst_reg = Column(String(20))
    duty_bill_to_acct_nbr = Column(Integer)
    duty_bill_to_cd = Column(String(1))
    payor_location = Column(String(5))
    weight = Column(String(10))
    export_country = Column(String(3))
    foreign_trade_zone = Column(String(5))
    discounts = Column(String(10))
    last_modified_nm = Column(String(20))
    data_form = Column(String(10))
    customeroid = Column(Integer)
    profile_ref_nbr = Column(Integer)
    dpi = Column(String(1))
    po_box = Column(String(1))
    phone_nbr = Column(String(20))
    broker_cd = Column(String(5))
    rod = Column(String(1))

    # parent relationships (access parent)

    # child relationships (access children)



class Shipment(Base):  # type: ignore
    __tablename__ = 'shipment'
    _s_collection_name = 'Shipment'  # type: ignore

    local_shipment_oid_nbr = Column(Integer, primary_key=True)
    awb_nbr = Column(String(20))
    base_charge_amt : DECIMAL = Column(DECIMAL(16, 4))
    cargo_desc = Column(String(45))
    cargo_qty = Column(Integer)
    cash_in_advance_flg = Column(String(1))
    ci_seq_nbr = Column(String(1))
    comat_flg = Column(String(1))
    consolidated_freight_flg = Column(String(1))
    container_nbr = Column(String(10))
    contract_wgt_type_cd = Column(String(1))
    create_dt = Column(Date)
    csa_flg = Column(String(1))
    customer_seq_nbr = Column(Integer)
    customs_clearance_cd = Column(String(1))
    customs_clearance_entry_flg = Column(String(1))
    dang_goods_cd = Column(String(1))
    data_entry_location_cd = Column(String(5))
    deleted_flg = Column(String(1))
    dest_customs_currency_cd = Column(String(3))
    dest_eec_flg = Column(String(1))
    dest_location_cd = Column(String(5))
    dest_loc_cntry_cd = Column(String(2))
    dim_height_qty = Column(Integer)
    dim_length_qty = Column(Integer)
    dim_wgt : DECIMAL = Column(DECIMAL(9, 1))
    dim_width_qty = Column(Integer)
    dim_shipment_flg = Column(String(1))
    discharge_location_cd = Column(String(4))
    drop_dscnt_cd = Column(String(1))
    dutiable_flg = Column(String(1))
    duty_bill_to_acct_nbr = Column(Integer)
    duty_bill_to_cd = Column(String(1))
    duty_cash_flg = Column(String(1))
    duty_credit_card_flg = Column(String(1), server_default=text("'N'"))
    ecs_filing_status_cd = Column(String(1))
    export_country_cd = Column(String(2))
    export_license_flg = Column(String(1))
    fda_confirmation_flg = Column(String(1))
    carrier_assigned_mawb_nbr = Column(String(12))
    planned_clearance_location_cd = Column(String(5))
    form_type_cd = Column(String(4))
    free_domicile_cd = Column(String(1))
    freight_charge_amt : DECIMAL = Column(DECIMAL(16, 4))
    ftsr_nbr = Column(Integer)
    goods_class_cd = Column(String(2))
    hal_flg = Column(String(1))
    hal_phone_nbr = Column(String(20))
    handling_unit_qty = Column(Integer)
    hawb_serial_nbr = Column(Integer)
    input_tmstp = Column(Date)
    intermediate_consignee_cd = Column(String(1))
    invoice_cd = Column(String(1))
    keyed_currency_cd = Column(String(3))
    keyer_nm = Column(String(12))
    last_modified_nm = Column(String(35))
    last_modified_tmstp = Column(DateTime)
    local_customs_currency_cd = Column(String(3))
    manuf_orig_cntry_cd = Column(String(2))
    manifest_status_cd = Column(String(2))
    mde_source_cd = Column(String(1))
    meter_nbr = Column(Integer)
    oda_charge_flg = Column(String(1))
    opa_charge_flg = Column(String(1))
    origin_loc_city_nm = Column(String(35))
    origin_loc_cntry_cd = Column(String(2))
    origin_eec_flg = Column(String(1))
    origin_location_cd = Column(String(5))
    package_movement_scan_cd = Column(String(1))
    packaging_type_cd = Column(String(3))
    piece_qty = Column(Integer)
    pkg_mark_desc = Column(String(35))
    prior_notice_nbr = Column(String(30))
    ramp_transfer_flg = Column(String(1))
    record_status_cd = Column(String(1))
    rod_flg = Column(String(1), server_default=text("'N'"))
    rpl_flg = Column(String(1))
    sdl_flg = Column(String(1))
    sed_cd = Column(String(1))
    sed_exempt_nbr = Column(String(2))
    service_cd = Column(String(5))
    service_type_cd = Column(String(2))
    shipment_control_nbr = Column(String(25))
    ship_dt = Column(Date)
    shipment_desc = Column(String(200))
    shipment_id_nbr = Column(Integer)
    shipper_reference_desc = Column(String(35))
    split_billing_address_amt : DECIMAL = Column(DECIMAL(16, 4))
    split_billing_kilo_wgt : DECIMAL = Column(DECIMAL(16, 4))
    spu_flg = Column(String(1))
    total_wgt : DECIMAL = Column(DECIMAL(7, 1))
    total_wgt_uom_cd = Column(String(3))
    tracking_id_nbr = Column(String(20))
    tracking_id_qual_nbr = Column(String(30))
    transaction_seq_tmstp = Column(DateTime)
    trprt_bill_to_acct_nbr = Column(Integer)
    trprt_bill_to_cd = Column(String(1))
    trprt_credit_card_flg = Column(String(1), server_default=text("'N'"))
    tran_data_source_cd = Column(String(2))
    unassign_reason_cd = Column(String(4))
    unloading_usa_port_cd = Column(String(5))
    value_changed_flg = Column(String(1))
    weekday_delivery_flg = Column(String(1))
    xtn_nbr = Column(String(32))
    dest_loc_city_nm = Column(String(35))
    final_import_clearance_loc_cd = Column(String(5))
    image_folder_id_cd = Column(String(20))
    aci_download_flg = Column(String(1))
    broker_dest_loc_cd = Column(String(5))
    visa_trans_cd = Column(String(2))
    etl_tmstp = Column(DateTime)
    split_shipment_flg = Column(String(1))
    shipment_type_cd = Column(Integer)
    entry_category_type_cd = Column(String(3))
    eci_flg = Column(String(1), server_default=text("'N'"))
    ci_image_flg = Column(String(1), server_default=text("'N'"))
    trprt_bill_to_pymt_method_cd = Column(Integer)
    duplicate_shipment_record_flg = Column(String(1), server_default=text("'N'"))
    oga_shipment_flg = Column(String(1), server_default=text("'N'"))
    cad_value_amt : DECIMAL = Column(DECIMAL(12, 2))
    transaction_nbr = Column(Integer)
    ci_image_tmstp = Column(DateTime)
    iid_master_cd = Column(String(4))
    iid_classify_cd = Column(String(8))
    automation_ci_flg = Column(String(1))
    iid_flg = Column(String(1))
    carriage_value_amt : DECIMAL = Column(DECIMAL(12, 2))
    customs_value_amt : DECIMAL = Column(DECIMAL(12, 2))
    dest_customs_value_amt : DECIMAL = Column(DECIMAL(12, 2))
    local_customs_value_amt : DECIMAL = Column(DECIMAL(12, 2))
    active_flg = Column(String(1), server_default=text("'Y'"))
    entry_dt = Column(Date)
    admissibility_mode = Column(String(1))
    prev_admissibility_mode = Column(String(1))
    cargocontrolnbr = Column(String(22))
    portofexit = Column(String(6))
    portofentry = Column(String(6))
    warehousecode = Column(String(6))
    surface_intl_shipment_nbr = Column(Numeric)

    # parent relationships (access parent)

    # child relationships (access children)
    PieceList : Mapped[List["Piece"]] = relationship(cascade="all, delete", back_populates="shipment")
    ShipmentCommodityList : Mapped[List["ShipmentCommodity"]] = relationship(cascade="all, delete", back_populates="shipment")
    SpecialHandlingList : Mapped[List["SpecialHandling"]] = relationship(cascade="all, delete", back_populates="shipment")
    ShipmentPartyList : Mapped[List["ShipmentParty"]] = relationship(cascade="all, delete", back_populates="shipment")



class ShipmentXml(Base):  # type: ignore
    __tablename__ = 'shipment_xml'
    _s_collection_name = 'ShipmentXml'  # type: ignore

    id           = Column(Integer, primary_key=True)
    received_at  = Column(DateTime, default=datetime.utcnow)
    payload      = Column(Text, nullable=False)
    is_processed = Column(Boolean, default=False)

    # parent relationships (access parent)

    # child relationships (access children)



class SysConfig(Base):  # type: ignore
    __tablename__ = 'sys_config'
    _s_collection_name = 'SysConfig'  # type: ignore

    id = Column(Integer, primary_key=True)
    name = Column(Text, server_default=text("'system'"), nullable=False)
    discount_rate = Column(Float, server_default=text("0.05"))
    tax_rate = Column(Float, server_default=text("0.10"))
    notes = Column(Text)

    # parent relationships (access parent)

    # child relationships (access children)



class VirtualRouteLeg(Base):  # type: ignore
    __tablename__ = 'virtual_route_leg'
    _s_collection_name = 'VirtualRouteLeg'  # type: ignore

    id = Column(Integer, primary_key=True)
    virtual_route_nbr = Column(String(6))
    virtual_route_dt = Column(Date)
    virtual_route_leg_nbr = Column(Integer)
    leg_dest_loc_cd = Column(String(5))
    leg_orig_loc_cd = Column(String(5))
    arrival_gmt_tmstp = Column(DateTime)
    arrival_local_tmstp = Column(DateTime)
    broker_complete_flg = Column(String(1))
    conveyance_type_cd = Column(String(2))
    customs_complete_flg = Column(String(1))
    depart_gmt_tmstp = Column(DateTime)
    depart_local_tmstp = Column(DateTime)
    leg_origin_country_cd = Column(String(2))
    leg_dest_country_cd = Column(String(2))
    sched_arrival_dt = Column(Date)
    sched_route_leg_orig_loc_cd = Column(String(5))
    sched_route_leg_dest_loc_cd = Column(String(5))
    sched_route_departure_dt = Column(Date)
    sched_route_leg_dptr_dt = Column(Date)
    sched_route_nbr = Column(String(8))
    sort_dt = Column(Date)
    tail_nbr = Column(String(8))
    us_process_cd = Column(String(1))
    virtual_route_locked_flg = Column(String(1))
    flight_nbr_obs = Column(String(6))
    download_flg = Column(String(1))
    carrier_cd = Column(String(4))
    etl_tmstp = Column(DateTime)
    eta_tmstp = Column(DateTime)
    in_range_tmstp = Column(DateTime)

    # parent relationships (access parent)

    # child relationships (access children)



class Piece(Base):  # type: ignore
    __tablename__ = 'piece'
    _s_collection_name = 'Piece'  # type: ignore

    local_piece_oid_nbr = Column(Integer, primary_key=True)
    local_shipment_oid_nbr = Column(ForeignKey('shipment.local_shipment_oid_nbr', ondelete='CASCADE'))
    arrival_port_cd = Column(String(5))
    awb_type_cd = Column(String(1))
    awb_format_cd = Column(String(1))
    contract_wgt_type_cd = Column(String(1))
    customs_value_amt : DECIMAL = Column(DECIMAL(16, 4))
    decln_oid_nbr = Column(Integer)
    decln_status_cd = Column(String(1))
    dest_location_cd = Column(String(5))
    dim_wgt : DECIMAL = Column(DECIMAL(9, 1))
    final_dest_cd = Column(String(5))
    form_type_cd = Column(String(4))
    harmonized_tariff_nbr = Column(String(20))
    ipd_doc_nbr = Column(String(12))
    last_foreign_port_cd = Column(String(5))
    last_modified_location_cd = Column(String(5))
    last_modified_nm = Column(String(35))
    manifest_status_cd = Column(String(2))
    manifest_tmstp = Column(DateTime)
    payment_option_cd = Column(String(1))
    payor_account_nbr = Column(Integer)
    payor_account_type_cd = Column(String(1))
    piece_qty = Column(Integer)
    piece_status_cd = Column(String(1))
    piece_type_cd = Column(String(1))
    port_of_export_cd = Column(String(5))
    port_of_unlading_cd = Column(String(5))
    rih_clearance_loc_cd = Column(String(5))
    shipper_reference_desc = Column(String(35))
    split_billing_business_cd = Column(String(12))
    split_billing_address_amt : DECIMAL = Column(DECIMAL(16, 4))
    split_billing_kilo_wgt : DECIMAL = Column(DECIMAL(16, 4))
    split_billing_currency_cd = Column(String(3))
    total_wgt : DECIMAL = Column(DECIMAL(7, 1))
    total_wgt_uom_cd = Column(String(3))
    tracking_nbr = Column(String(12))
    transaction_seq_tmstp = Column(DateTime)
    variable_pct = Column(Integer)
    xref_nbr = Column(String(12))
    etl_tmstp = Column(DateTime)
    shipment_type_cd = Column(Integer)
    split_seq_nbr = Column(Integer, server_default=text("0"))
    piece_deleted_flg = Column(String(1))
    piece_seq_nbr = Column(Integer)
    piece_movement_flg = Column(String(1))

    # parent relationships (access parent)
    shipment : Mapped["Shipment"] = relationship(back_populates=("PieceList"))

    # child relationships (access children)
    ShipmentPartyList : Mapped[List["ShipmentParty"]] = relationship(back_populates="piece")



class ShipmentCommodity(Base):  # type: ignore
    __tablename__ = 'shipment_commodity'
    _s_collection_name = 'ShipmentCommodity'  # type: ignore

    local_shipment_oid_nbr = Column(ForeignKey('shipment.local_shipment_oid_nbr', ondelete='CASCADE'), primary_key=True, nullable=False)
    sequence_nbr = Column(Integer, primary_key=True, nullable=False)
    clearance_country_cd = Column(String(2))
    commodity_desc = Column(String(300))
    commodity_wgt : DECIMAL = Column(DECIMAL(12, 4))
    commodity_wgt_uom_cd = Column(String(3))
    customs_value_amt : DECIMAL = Column(DECIMAL(16, 4))
    export_cargo_control_nbr = Column(String(6))
    export_license_expr_dt = Column(Date)
    export_license_nbr = Column(String(12))
    harmonized_tariff_nbr = Column(String(20))
    hazardous_material_cd = Column(String(4))
    last_modified_nm = Column(String(35))
    last_modified_tmstp = Column(DateTime)
    origin_country_cd = Column(String(2))
    oversize_flg = Column(String(1))
    piece_qty = Column(Integer)
    package_qty = Column(Integer)
    tariff_source_cd = Column(String(1))
    etl_tmstp = Column(DateTime)
    shipment_type_cd = Column(Integer)
    commodity_currency_cd = Column(String(3))
    unit_of_measure_cd = Column(String(3))
    classification_status_desc = Column(String(200))
    classification_status_cd = Column(String(10))
    part_expiration_dt = Column(Date)
    allow_client_generated_ids = True

    # parent relationships (access parent)
    shipment : Mapped["Shipment"] = relationship(back_populates=("ShipmentCommodityList"))

    # child relationships (access children)



class SpecialHandling(Base):  # type: ignore
    __tablename__ = 'special_handling'
    _s_collection_name = 'SpecialHandling'  # type: ignore

    id = Column(Integer, primary_key=True)
    oid_nbr = Column(ForeignKey('shipment.local_shipment_oid_nbr', ondelete='CASCADE'))
    oid_type_cd = Column(String(1))
    special_handling_cd = Column(String(5))
    etl_tmstp = Column(DateTime)
    shipment_type_cd = Column(Integer)

    # parent relationships (access parent)
    shipment : Mapped["Shipment"] = relationship(back_populates=("SpecialHandlingList"))

    # child relationships (access children)



class ShipmentParty(Base):  # type: ignore
    __tablename__ = 'shipment_party'
    _s_collection_name = 'ShipmentParty'  # type: ignore

    shipment_party_oid_nbr = Column(Integer, primary_key=True)
    local_shipment_oid_nbr = Column(ForeignKey('shipment.local_shipment_oid_nbr', ondelete='CASCADE'))
    shipment_party_type_cd = Column(String(1))
    clearance_location_cd = Column(String(5))
    address_qty = Column(Integer)
    broker_id_cd = Column(String(4))
    city_nm = Column(String(35))
    contact_phone_nbr = Column(String(20))
    country_cd = Column(String(2))
    country_sub_entity_cd = Column(String(9))
    customer_acct_nbr = Column(Integer)
    customs_id_cd = Column(String(18))
    customs_self_assessment_flg = Column(String(1))
    company_nm = Column(String(70))
    contact_nm = Column(String(35))
    email_nm = Column(String(255))
    last_modified_nm = Column(String(35))
    last_modified_tmstp = Column(DateTime)
    postal_cd = Column(String(15))
    state_cd = Column(String(2))
    etl_tmstp = Column(DateTime)
    shipment_type_cd = Column(Integer)
    csa_business_nbr = Column(String(25))
    local_piece_oid_nbr = Column(ForeignKey('piece.local_piece_oid_nbr', ondelete='CASCADE'))
    piece_shpmt_type_cd = Column(Integer)
    split_seq_nbr = Column(Integer)
    business_nbr = Column(String(15))
    cfia_payor_nm = Column(String(35))
    cfia_account_nbr = Column(String(15))
    fax_nbr = Column(String(15))
    pref_cont_mthd_cd = Column(String(2))
    additional_contact_flg = Column(String(1), server_default=text("'N'"))

    # parent relationships (access parent)
    piece : Mapped["Piece"] = relationship(back_populates=("ShipmentPartyList"))
    shipment : Mapped["Shipment"] = relationship(back_populates=("ShipmentPartyList"))

    # child relationships (access children)
