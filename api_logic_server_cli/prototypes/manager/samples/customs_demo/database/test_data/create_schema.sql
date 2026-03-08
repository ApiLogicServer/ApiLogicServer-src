-- ============================================================
-- CBSA Steel Derivative Goods Surtax Order PC 2025-0917
-- Program Code: 25267A  Effective ship date: 2025-12-26
-- ============================================================

-- 1) Extend sys_config with surtax programme constants
ALTER TABLE sys_config ADD COLUMN surtax_effective_date TEXT DEFAULT '2025-12-26';
ALTER TABLE sys_config ADD COLUMN program_code TEXT DEFAULT '25267A';
ALTER TABLE sys_config ADD COLUMN order_reference TEXT DEFAULT 'PC 2025-0917';

UPDATE sys_config SET
    surtax_effective_date = '2025-12-26',
    program_code          = '25267A',
    order_reference       = 'PC 2025-0917'
WHERE id = 1;

-- 2) HS Code schedule - steel derivative goods (SOR/2025-154)
CREATE TABLE hs_code_rate (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_code         TEXT    NOT NULL UNIQUE,
    description     TEXT    NOT NULL,
    base_duty_rate  DECIMAL(8,6) NOT NULL DEFAULT 0.0
);

-- 3) Country of origin - surtax applicability per country
CREATE TABLE country_origin (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT    NOT NULL UNIQUE,
    country_name TEXT    NOT NULL,
    surtax_rate  DECIMAL(8,6) NOT NULL DEFAULT 0.0
);

-- 4) Province - combined tax rate (GST, HST, or GST+PST)
CREATE TABLE province (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    province_code TEXT    NOT NULL UNIQUE,
    province_name TEXT    NOT NULL,
    tax_rate      DECIMAL(8,6) NOT NULL DEFAULT 0.05
);

-- 5) Customs entry header
CREATE TABLE customs_entry (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_number          TEXT    NOT NULL,
    importer_name         TEXT,
    ship_date             TEXT    NOT NULL,
    province_id           INTEGER REFERENCES province(id),
    sys_config_id         INTEGER REFERENCES sys_config(id) DEFAULT 1,
    province_tax_rate     DECIMAL(8,6),
    surtax_effective_date TEXT,
    surtax_active         INTEGER DEFAULT 0,
    total_customs_value   DECIMAL(15,2) DEFAULT 0,
    total_base_duty       DECIMAL(15,2) DEFAULT 0,
    total_surtax          DECIMAL(15,2) DEFAULT 0,
    total_provincial_tax  DECIMAL(15,2) DEFAULT 0,
    grand_total_duties    DECIMAL(15,2) DEFAULT 0,
    notes                 TEXT
);

-- 6) Surtax line item - one per HS-code product per entry
CREATE TABLE surtax_line_item (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    customs_entry_id      INTEGER NOT NULL REFERENCES customs_entry(id),
    hs_code_id            INTEGER NOT NULL REFERENCES hs_code_rate(id),
    country_origin_id     INTEGER NOT NULL REFERENCES country_origin(id),
    customs_value         DECIMAL(15,2) NOT NULL DEFAULT 0,
    quantity              INTEGER       NOT NULL DEFAULT 1,
    description           TEXT,
    base_duty_rate        DECIMAL(8,6)  DEFAULT 0,
    surtax_rate           DECIMAL(8,6)  DEFAULT 0,
    surtax_applicable     INTEGER       DEFAULT 0,
    base_duty_amount      DECIMAL(15,2) DEFAULT 0,
    duty_paid_value       DECIMAL(15,2) DEFAULT 0,
    surtax_amount         DECIMAL(15,2) DEFAULT 0,
    provincial_tax_amount DECIMAL(15,2) DEFAULT 0,
    line_total            DECIMAL(15,2) DEFAULT 0
);
