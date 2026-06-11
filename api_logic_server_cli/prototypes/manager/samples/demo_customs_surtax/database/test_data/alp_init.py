#!/usr/bin/env python
import os, logging, logging.config, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))  # ensure project root on path
# Seed loading flushes each header before appending its line items (so
# row-logic on the header completes first); disable opt-locking so those
# in-transaction header updates aren't mistaken for concurrent edits
os.environ['OPT_LOCKING'] = 'ignored'
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
from datetime import date
from decimal import Decimal
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()
    session = safrs.DB.session

    # --- Lookup data ---

    # Countries of origin (CountryOrigin.surtax_rate: 0.0 = exempt, 0.25 = subject to 25% surtax)
    germany = CountryOrigin(id=1, country_code='DE', country_name='Germany', trade_agreement='CETA', surtax_rate=Decimal('0.0'))
    united_states = CountryOrigin(id=2, country_code='US', country_name='United States', trade_agreement='CUSMA', surtax_rate=Decimal('0.0'))
    japan = CountryOrigin(id=3, country_code='JP', country_name='Japan', trade_agreement='CPTPP', surtax_rate=Decimal('0.0'))
    china = CountryOrigin(id=4, country_code='CN', country_name='China', trade_agreement=None, surtax_rate=Decimal('0.25'))
    session.add_all([germany, united_states, japan, china])

    # Provinces (Province.tax_rate: single pre-combined GST/PST/HST rate)
    ontario = Province(id=1, province_code='ON', province_name='Ontario', tax_rate=Decimal('0.13'))
    alberta = Province(id=2, province_code='AB', province_name='Alberta', tax_rate=Decimal('0.05'))
    british_columbia = Province(id=3, province_code='BC', province_name='British Columbia', tax_rate=Decimal('0.12'))
    nova_scotia = Province(id=4, province_code='NS', province_name='Nova Scotia', tax_rate=Decimal('0.15'))
    manitoba = Province(id=5, province_code='MB', province_name='Manitoba', tax_rate=Decimal('0.12'))
    session.add_all([ontario, alberta, british_columbia, nova_scotia, manitoba])

    # HS codes in the Steel Derivative Goods Surtax Order schedule (base_duty_rate: MFN duty rate)
    hs_7208 = HsCodeRate(id=1, hs_code='7208.10', description='Flat-rolled steel, hot-rolled, in coils', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    hs_7213 = HsCodeRate(id=2, hs_code='7213.10', description='Bars and rods, hot-rolled, of iron/non-alloy steel, in coils', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    hs_7216 = HsCodeRate(id=3, hs_code='7216.10', description='Angles, shapes and sections of iron/non-alloy steel', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    hs_7228 = HsCodeRate(id=4, hs_code='7228.30', description='Other bars and rods of alloy steel, hot-rolled', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    hs_7301 = HsCodeRate(id=5, hs_code='7301.10', description='Sheet piling of iron or steel', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    hs_7306 = HsCodeRate(id=6, hs_code='7306.30', description='Welded tubes and pipes, circular, of iron/non-alloy steel', base_duty_rate=Decimal('0.0'), is_steel_derivative=1)
    session.add_all([hs_7208, hs_7213, hs_7216, hs_7228, hs_7301, hs_7306])

    session.commit()  # lookups committed first so FK references resolve cleanly

    # --- Example transactions (per prompt: Germany/US/Japan exempt, China subject 25%) ---
    # All ship_dates are >= sys_config.effective_date (2025-12-26), so the surtax
    # order is in effect; whether surtax actually applies depends on country_surtax_rate.

    # 1. Germany - CETA exempt (surtax_rate = 0.0)
    # Header is added + flushed before line items so its surtax_applicable
    # formula resolves first (line items read row.customs_entry.surtax_applicable)
    entry_de = CustomsEntry(entry_number='B3-2026-0001', importer_name='Northern Steel Importers Inc.',
                             ship_date=date(2026, 1, 15), country_origin_id=germany.id, province_id=ontario.id)
    session.add(entry_de)
    session.flush()
    entry_de.SurtaxLineItemList.append(SurtaxLineItem(line_number=1, hs_code_id=hs_7208.id,
                                                        description='Hot-rolled steel coil', customs_value=Decimal('50000.00')))
    entry_de.SurtaxLineItemList.append(SurtaxLineItem(line_number=2, hs_code_id=hs_7216.id,
                                                        description='Steel angles', customs_value=Decimal('15000.00')))
    session.flush()

    # 2. United States - CUSMA exempt (surtax_rate = 0.0)
    entry_us = CustomsEntry(entry_number='B3-2026-0002', importer_name='Maple Leaf Manufacturing Ltd.',
                             ship_date=date(2026, 1, 20), country_origin_id=united_states.id, province_id=alberta.id)
    session.add(entry_us)
    session.flush()
    entry_us.SurtaxLineItemList.append(SurtaxLineItem(line_number=1, hs_code_id=hs_7213.id,
                                                        description='Hot-rolled steel rod, in coils', customs_value=Decimal('30000.00')))
    session.flush()

    # 3. Japan - CPTPP exempt (surtax_rate = 0.0)
    entry_jp = CustomsEntry(entry_number='B3-2026-0003', importer_name='Pacific Coast Trading Co.',
                             ship_date=date(2026, 2, 1), country_origin_id=japan.id, province_id=british_columbia.id)
    session.add(entry_jp)
    session.flush()
    entry_jp.SurtaxLineItemList.append(SurtaxLineItem(line_number=1, hs_code_id=hs_7306.id,
                                                        description='Welded steel pipe', customs_value=Decimal('42000.00')))
    entry_jp.SurtaxLineItemList.append(SurtaxLineItem(line_number=2, hs_code_id=hs_7301.id,
                                                        description='Steel sheet piling', customs_value=Decimal('18000.00')))
    session.flush()

    # 4. China - subject to surtax (surtax_rate = 0.25)
    entry_cn = CustomsEntry(entry_number='B3-2026-0004', importer_name='Great Lakes Steel Distributors',
                             ship_date=date(2026, 1, 10), country_origin_id=china.id, province_id=ontario.id)
    session.add(entry_cn)
    session.flush()
    entry_cn.SurtaxLineItemList.append(SurtaxLineItem(line_number=1, hs_code_id=hs_7208.id,
                                                        description='Hot-rolled steel coil', customs_value=Decimal('60000.00')))
    entry_cn.SurtaxLineItemList.append(SurtaxLineItem(line_number=2, hs_code_id=hs_7228.id,
                                                        description='Alloy steel bars, hot-rolled', customs_value=Decimal('25000.00')))
    session.flush()

    session.commit()
