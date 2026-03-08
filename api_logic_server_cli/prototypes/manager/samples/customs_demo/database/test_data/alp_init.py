#!/usr/bin/env python
"""
CBSA Steel Derivative Goods Surtax - Seed Data
PC Number: 2025-0917  |  Program Code: 25267A
Effective ship date: 2025-12-26

Examples from: Germany, US, Japan, China
"""
import os, logging, logging.config, sys
from config import server_setup
import api.system.api_utils as api_utils
from flask import Flask
import logging
import config.config as config
from decimal import Decimal

os.environ["PROJECT_DIR"] = os.environ.get(
    "PROJECT_DIR", os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
)

app_logger = server_setup.logging_setup()
app_logger.setLevel(logging.INFO)

current_path = os.path.abspath(os.path.dirname(__file__))
sys.path.extend([current_path, os.path.join(current_path, "../..")])

flask_app = Flask("API Logic Server", template_folder='ui/templates')
flask_app.config.from_object(config.Config)
flask_app.config.from_prefixed_env(prefix="APILOGICPROJECT")

args = server_setup.get_args(flask_app)
server_setup.api_logic_server_setup(flask_app, args)

from database.models import (
    SysConfig, HsCodeRate, CountryOrigin, Province,
    CustomsEntry, SurtaxLineItem,
)
import safrs
import os
os.environ['AGGREGATE_DEFAULTS'] = 'True'

with flask_app.app_context():
    safrs.DB.create_all()
    session = safrs.DB.session

    # ------------------------------------------------------------------
    # 1. SysConfig — update system row with CBSA programme constants
    # ------------------------------------------------------------------
    cfg = session.query(SysConfig).filter_by(id=1).first()
    if cfg is None:
        cfg = SysConfig(id=1, name="system")
        session.add(cfg)
    cfg.surtax_effective_date = "2025-12-26"
    cfg.program_code          = "25267A"
    cfg.order_reference       = "PC 2025-0917"
    session.commit()

    # ------------------------------------------------------------------
    # 2. HS Code Schedule — steel derivative goods (SOR/2025-154)
    #    Base MFN duty rates reflect Canadian tariff schedule
    # ------------------------------------------------------------------
    hs_data = [
        # (hs_code,  description,                                     base_duty_rate)
        ("7208.51", "Flat-rolled iron/steel, cold-rolled, >=3mm",     Decimal("0.000000")),
        ("7214.20", "Steel bars and rods, hot-rolled, in coils",      Decimal("0.060000")),
        ("7219.21", "Flat-rolled stainless steel, hot-rolled, >10mm", Decimal("0.050000")),
        ("7306.30", "Steel tubes and pipes, welded, circular",        Decimal("0.058000")),
        ("7325.99", "Other cast articles of iron or steel",           Decimal("0.070000")),
        ("7326.19", "Other articles of iron or steel",                Decimal("0.065000")),
    ]
    hs_objs = {}
    for hs_code, desc, rate in hs_data:
        obj = HsCodeRate(hs_code=hs_code, description=desc, base_duty_rate=rate)
        session.add(obj)
        session.flush()
        hs_objs[hs_code] = obj
    session.commit()

    # ------------------------------------------------------------------
    # 3. Country of Origin — surtax applicability under PC 2025-0917
    #    25% surtax: US and China
    #    Exempt: Germany (CETA), Japan (CPTPP)
    # ------------------------------------------------------------------
    country_data = [
        # (code, name,             surtax_rate)
        ("US", "United States",    Decimal("0.250000")),
        ("CN", "China",            Decimal("0.250000")),
        ("DE", "Germany",          Decimal("0.000000")),
        ("JP", "Japan",            Decimal("0.000000")),
    ]
    country_objs = {}
    for code, name, rate in country_data:
        obj = CountryOrigin(country_code=code, country_name=name, surtax_rate=rate)
        session.add(obj)
        session.flush()
        country_objs[code] = obj
    session.commit()

    # ------------------------------------------------------------------
    # 4. Provinces — combined tax rates
    #    HST provinces: ON=13%, NS=15%
    #    GST+PST: BC=12%, QC=14.975%
    #    GST only: AB=5%
    # ------------------------------------------------------------------
    province_data = [
        # (code, name,                  tax_rate)
        ("ON", "Ontario",               Decimal("0.130000")),  # HST 13%
        ("BC", "British Columbia",      Decimal("0.120000")),  # GST 5% + PST 7%
        ("AB", "Alberta",               Decimal("0.050000")),  # GST 5% only
        ("QC", "Quebec",                Decimal("0.149750")),  # GST 5% + QST 9.975%
        ("NS", "Nova Scotia",           Decimal("0.150000")),  # HST 15%
        ("MB", "Manitoba",              Decimal("0.120000")),  # GST 5% + PST 7%
    ]
    prov_objs = {}
    for code, name, rate in province_data:
        obj = Province(province_code=code, province_name=name, tax_rate=rate)
        session.add(obj)
        session.flush()
        prov_objs[code] = obj
    session.commit()

    # ------------------------------------------------------------------
    # 5. Customs Entries with SurtaxLineItems
    #    LogicBank rules auto-calculate all derived columns on commit
    # ------------------------------------------------------------------

    # --- Entry 1: Germany → Ontario (after effective date, CETA exempt)
    # surtax_rate=0 for DE → no surtax | ship_date > 2025-12-26 → surtax_active=1 but rate=0
    # Expected: base duty only + 13% HST on duty-paid value
    e1 = CustomsEntry(
        entry_number  = "CBSA-2025-DE-001",
        importer_name = "Ontario Steel Corp",
        ship_date     = "2025-12-28",
        province_id   = prov_objs["ON"].id,
        sys_config_id = 1,
        notes         = "German steel - CETA exempt from surtax, 13% HST applies",
    )
    session.add(e1)
    session.flush()
    session.add(SurtaxLineItem(
        customs_entry_id  = e1.id,
        hs_code_id        = hs_objs["7208.51"].id,
        country_origin_id = country_objs["DE"].id,
        customs_value     = Decimal("150000.00"),
        quantity          = 800,
        description       = "Cold-rolled flat steel sheets - Germany",
    ))
    session.add(SurtaxLineItem(
        customs_entry_id  = e1.id,
        hs_code_id        = hs_objs["7306.30"].id,
        country_origin_id = country_objs["DE"].id,
        customs_value     = Decimal("50000.00"),
        quantity          = 200,
        description       = "Welded steel tubes - Germany",
    ))
    session.commit()

    # --- Entry 2: United States → British Columbia (25% surtax + 12% PST/GST)
    # Expected: base duty + 25% surtax + 12% provincial tax on duty-paid value
    e2 = CustomsEntry(
        entry_number  = "CBSA-2026-US-001",
        importer_name = "Pacific Metal Inc",
        ship_date     = "2026-01-15",
        province_id   = prov_objs["BC"].id,
        sys_config_id = 1,
        notes         = "US steel derivative goods - 25% surtax under PC 2025-0917 / 25267A",
    )
    session.add(e2)
    session.flush()
    session.add(SurtaxLineItem(
        customs_entry_id  = e2.id,
        hs_code_id        = hs_objs["7214.20"].id,
        country_origin_id = country_objs["US"].id,
        customs_value     = Decimal("200000.00"),
        quantity          = 500,
        description       = "Hot-rolled steel bars - United States",
    ))
    session.add(SurtaxLineItem(
        customs_entry_id  = e2.id,
        hs_code_id        = hs_objs["7326.19"].id,
        country_origin_id = country_objs["US"].id,
        customs_value     = Decimal("80000.00"),
        quantity          = 1200,
        description       = "Steel articles and fittings - United States",
    ))
    session.commit()

    # --- Entry 3: Japan → Alberta (CPTPP-exempt, GST 5% only)
    # Expected: base duty + NO surtax + 5% GST
    e3 = CustomsEntry(
        entry_number  = "CBSA-2025-JP-001",
        importer_name = "Alberta Energy Equipment Ltd",
        ship_date     = "2025-12-30",
        province_id   = prov_objs["AB"].id,
        sys_config_id = 1,
        notes         = "Japanese steel - CPTPP exempt from surtax, 5% GST only",
    )
    session.add(e3)
    session.flush()
    session.add(SurtaxLineItem(
        customs_entry_id  = e3.id,
        hs_code_id        = hs_objs["7219.21"].id,
        country_origin_id = country_objs["JP"].id,
        customs_value     = Decimal("300000.00"),
        quantity          = 400,
        description       = "Hot-rolled stainless steel coils - Japan",
    ))
    session.add(SurtaxLineItem(
        customs_entry_id  = e3.id,
        hs_code_id        = hs_objs["7325.99"].id,
        country_origin_id = country_objs["JP"].id,
        customs_value     = Decimal("45000.00"),
        quantity          = 300,
        description       = "Cast iron machinery components - Japan",
    ))
    session.commit()

    # --- Entry 4: China → Ontario (25% surtax + 13% HST)
    # Expected: base duty + 25% surtax + 13% HST on duty-paid value
    e4 = CustomsEntry(
        entry_number  = "CBSA-2026-CN-001",
        importer_name = "Toronto Industrial Supply Co",
        ship_date     = "2026-02-01",
        province_id   = prov_objs["ON"].id,
        sys_config_id = 1,
        notes         = "Chinese steel derivative goods - 25% surtax PC 2025-0917 / 25267A + 13% HST",
    )
    session.add(e4)
    session.flush()
    session.add(SurtaxLineItem(
        customs_entry_id  = e4.id,
        hs_code_id        = hs_objs["7326.19"].id,
        country_origin_id = country_objs["CN"].id,
        customs_value     = Decimal("120000.00"),
        quantity          = 2000,
        description       = "Steel fasteners and fittings - China",
    ))
    session.add(SurtaxLineItem(
        customs_entry_id  = e4.id,
        hs_code_id        = hs_objs["7306.30"].id,
        country_origin_id = country_objs["CN"].id,
        customs_value     = Decimal("60000.00"),
        quantity          = 500,
        description       = "Steel pipes - China",
    ))
    session.add(SurtaxLineItem(
        customs_entry_id  = e4.id,
        hs_code_id        = hs_objs["7214.20"].id,
        country_origin_id = country_objs["CN"].id,
        customs_value     = Decimal("35000.00"),
        quantity          = 800,
        description       = "Steel rods - China",
    ))
    session.commit()

    # --- Entry 5: United States → BC, ship BEFORE effective date (no surtax)
    # ship_date 2025-12-10 < 2025-12-26 → surtax_active=0 → no surtax even for US
    e5 = CustomsEntry(
        entry_number  = "CBSA-2025-US-BEFORE",
        importer_name = "Vancouver Port Logistics Inc",
        ship_date     = "2025-12-10",
        province_id   = prov_objs["BC"].id,
        sys_config_id = 1,
        notes         = "US goods shipped BEFORE PC 2025-0917 effective date - no surtax",
    )
    session.add(e5)
    session.flush()
    session.add(SurtaxLineItem(
        customs_entry_id  = e5.id,
        hs_code_id        = hs_objs["7306.30"].id,
        country_origin_id = country_objs["US"].id,
        customs_value     = Decimal("95000.00"),
        quantity          = 350,
        description       = "US steel pipes - shipped before surtax effective date",
    ))
    session.commit()

    print("✅ Seed data loaded successfully")
    print(f"   - {len(hs_data)} HS codes (steel derivative goods)")
    print(f"   - {len(country_data)} countries (US/CN taxed, DE/JP exempt)")
    print(f"   - {len(province_data)} provinces")
    print(f"   - 5 customs entries with 10 line items")
    print("   Open Admin UI: http://localhost:5656/admin-app")

