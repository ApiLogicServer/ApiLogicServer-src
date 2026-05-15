#!/usr/bin/env python
import os, logging, logging.config, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path
from config import server_setup
import api.system.api_utils as api_utils
from flask import Flask
import logging
import config.config as config

os.environ["PROJECT_DIR"] = os.environ.get("PROJECT_DIR", os.path.abspath(os.path.dirname(__file__)))

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.INFO)

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([current_path, '.'])

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")

args = server_setup.get_args(flask_app)
server_setup.api_logic_server_setup(flask_app, args)

from database.models import *
import safrs
from decimal import Decimal
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

session = safrs.DB.session

with flask_app.app_context():
    safrs.DB.create_all()

    # --- CountryOrigin lookup ---
    # Germany: CETA exempt (0%), US: CUSMA exempt (0%), Japan: CPTPP exempt (0%), China: 25%
    countries = [
        CountryOrigin(country_code='DE', country_name='Germany',        surtax_rate=Decimal('0.000000')),
        CountryOrigin(country_code='US', country_name='United States',  surtax_rate=Decimal('0.000000')),
        CountryOrigin(country_code='JP', country_name='Japan',          surtax_rate=Decimal('0.000000')),
        CountryOrigin(country_code='CN', country_name='China',          surtax_rate=Decimal('0.250000')),
        CountryOrigin(country_code='GB', country_name='United Kingdom', surtax_rate=Decimal('0.250000')),
    ]
    for c in countries:
        session.add(c)
    session.commit()

    # --- Province lookup (single combined tax_rate) ---
    provinces = [
        Province(province_code='ON', province_name='Ontario',           tax_rate=Decimal('0.1300')),  # HST 13%
        Province(province_code='BC', province_name='British Columbia',  tax_rate=Decimal('0.1200')),  # GST 5% + PST 7%
        Province(province_code='AB', province_name='Alberta',           tax_rate=Decimal('0.0500')),  # GST 5% only
        Province(province_code='QC', province_name='Quebec',            tax_rate=Decimal('0.1498')),  # GST 5% + QST ~9.975%
        Province(province_code='NS', province_name='Nova Scotia',       tax_rate=Decimal('0.1500')),  # HST 15%
        Province(province_code='MB', province_name='Manitoba',          tax_rate=Decimal('0.1200')),  # GST 5% + PST 7%
    ]
    for p in provinces:
        session.add(p)
    session.commit()

    # --- HsCodeRate lookup (steel derivative goods per SOR/2025-154) ---
    hs_codes = [
        HsCodeRate(hs_code='7301.10', description='Sheet piling of iron or steel',                base_duty_rate=Decimal('0.000000')),
        HsCodeRate(hs_code='7302.10', description='Railways/tramway track construction material', base_duty_rate=Decimal('0.000000')),
        HsCodeRate(hs_code='7304.11', description='Line pipe for oil or gas pipelines',           base_duty_rate=Decimal('0.000000')),
        HsCodeRate(hs_code='7306.30', description='Welded circular cross-section tubes/pipes',    base_duty_rate=Decimal('0.000000')),
        HsCodeRate(hs_code='7308.90', description='Other structures and parts of iron or steel',  base_duty_rate=Decimal('0.000000')),
        HsCodeRate(hs_code='7315.11', description='Roller chains',                                base_duty_rate=Decimal('0.055000')),
    ]
    for h in hs_codes:
        session.add(h)
    session.commit()

    # Retrieve lookup IDs (assigned after commit)
    de = session.query(CountryOrigin).filter_by(country_code='DE').one()
    us = session.query(CountryOrigin).filter_by(country_code='US').one()
    jp = session.query(CountryOrigin).filter_by(country_code='JP').one()
    cn = session.query(CountryOrigin).filter_by(country_code='CN').one()

    on = session.query(Province).filter_by(province_code='ON').one()
    bc = session.query(Province).filter_by(province_code='BC').one()
    ab = session.query(Province).filter_by(province_code='AB').one()
    qc = session.query(Province).filter_by(province_code='QC').one()

    hs_7301 = session.query(HsCodeRate).filter_by(hs_code='7301.10').one()
    hs_7302 = session.query(HsCodeRate).filter_by(hs_code='7302.10').one()
    hs_7304 = session.query(HsCodeRate).filter_by(hs_code='7304.11').one()
    hs_7306 = session.query(HsCodeRate).filter_by(hs_code='7306.30').one()
    hs_7308 = session.query(HsCodeRate).filter_by(hs_code='7308.90').one()
    hs_7315 = session.query(HsCodeRate).filter_by(hs_code='7315.11').one()

    # --- Example 1: Germany (CETA exempt) — Ontario HST ---
    entry_de = CustomsEntry(
        entry_number='CBSA-2026-001', importer_name='Deutsche Stahl GmbH Import',
        ship_date='2026-01-15', country_origin_id=de.id, province_id=on.id, sys_config_id=1,
    )
    session.add(entry_de)
    session.commit()
    session.add(SurtaxLineItem(customs_entry_id=entry_de.id, hs_code_id=hs_7301.id,
        description='Heavy sheet piling for seawall project', customs_value=Decimal('50000.00')))
    session.commit()

    # --- Example 2: United States (CUSMA exempt) — British Columbia ---
    entry_us = CustomsEntry(
        entry_number='CBSA-2026-002', importer_name='Pacific Steel Distributors Inc.',
        ship_date='2026-01-20', country_origin_id=us.id, province_id=bc.id, sys_config_id=1,
    )
    session.add(entry_us)
    session.commit()
    session.add(SurtaxLineItem(customs_entry_id=entry_us.id, hs_code_id=hs_7304.id,
        description='Line pipe for natural gas pipeline', customs_value=Decimal('100000.00')))
    session.add(SurtaxLineItem(customs_entry_id=entry_us.id, hs_code_id=hs_7306.id,
        description='Welded circular pipes for distribution', customs_value=Decimal('75000.00')))
    session.commit()

    # --- Example 3: Japan (CPTPP exempt) — Alberta GST only ---
    entry_jp = CustomsEntry(
        entry_number='CBSA-2025-003', importer_name='Nippon Steel Canada Ltd.',
        ship_date='2025-12-28', country_origin_id=jp.id, province_id=ab.id, sys_config_id=1,
    )
    session.add(entry_jp)
    session.commit()
    session.add(SurtaxLineItem(customs_entry_id=entry_jp.id, hs_code_id=hs_7302.id,
        description='Railway track rails for transit project', customs_value=Decimal('80000.00')))
    session.commit()

    # --- Example 4: China (25% surtax) — Quebec QST ---
    entry_cn = CustomsEntry(
        entry_number='CBSA-2026-004', importer_name='Sinochem Steel Imports Inc.',
        ship_date='2026-02-01', country_origin_id=cn.id, province_id=qc.id, sys_config_id=1,
    )
    session.add(entry_cn)
    session.commit()
    session.add(SurtaxLineItem(customs_entry_id=entry_cn.id, hs_code_id=hs_7308.id,
        description='Structural steel for commercial building', customs_value=Decimal('120000.00')))
    session.add(SurtaxLineItem(customs_entry_id=entry_cn.id, hs_code_id=hs_7315.id,
        description='Industrial roller chains', customs_value=Decimal('15000.00')))
    session.commit()

    # --- Example 5: US pre-surtax (ship_date < 2025-12-26, surtax_applicable=0) ---
    entry_us_pre = CustomsEntry(
        entry_number='CBSA-2025-005', importer_name='Pacific Steel Distributors Inc.',
        ship_date='2025-12-20', country_origin_id=us.id, province_id=on.id, sys_config_id=1,
    )
    session.add(entry_us_pre)
    session.commit()
    session.add(SurtaxLineItem(customs_entry_id=entry_us_pre.id, hs_code_id=hs_7304.id,
        description='Line pipe - pre-surtax shipment', customs_value=Decimal('50000.00')))
    session.commit()

    print("\n✅ Seed data loaded successfully.")
    print("   Open Admin App at http://localhost:5656/")

