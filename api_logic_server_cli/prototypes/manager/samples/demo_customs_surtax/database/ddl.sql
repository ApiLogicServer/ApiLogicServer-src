-- Steel Derivative Goods Surtax Order — schema additions
-- Built fresh per Method 4 (System Creation Services)

-- 1. Extend sys_config with regulatory constants from PC Number 2025-0917
ALTER TABLE sys_config ADD COLUMN pc_number TEXT DEFAULT '2025-0917';
ALTER TABLE sys_config ADD COLUMN program_code TEXT DEFAULT '25267A';
ALTER TABLE sys_config ADD COLUMN order_title TEXT DEFAULT 'Steel Derivative Goods Surtax Order';
ALTER TABLE sys_config ADD COLUMN order_date DATE DEFAULT '2025-12-11';
ALTER TABLE sys_config ADD COLUMN legal_authority TEXT DEFAULT 'Subsection 53(2) and paragraph 79(a) of the Customs Tariff';
ALTER TABLE sys_config ADD COLUMN effective_date DATE DEFAULT '2025-12-26';

UPDATE sys_config SET
    pc_number = '2025-0917',
    program_code = '25267A',
    order_title = 'Steel Derivative Goods Surtax Order',
    order_date = '2025-12-11',
    legal_authority = 'Subsection 53(2) and paragraph 79(a) of the Customs Tariff',
    effective_date = '2025-12-26'
WHERE id = 1;

-- 2. Country of origin lookup — surtax_rate is a decimal multiplier (0.0 = exempt, 0.25 = full)
CREATE TABLE country_origin (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code    VARCHAR(2)   NOT NULL UNIQUE,
    country_name    VARCHAR(100) NOT NULL,
    trade_agreement VARCHAR(20),
    surtax_rate     NUMERIC(8,6) NOT NULL DEFAULT 0
);

-- 3. Province / territory lookup — single pre-combined sales-tax rate (no gst/pst/hst split)
CREATE TABLE province (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    province_code VARCHAR(2)   NOT NULL UNIQUE,
    province_name VARCHAR(100) NOT NULL,
    tax_rate      NUMERIC(8,4) NOT NULL DEFAULT 0
);

-- 4. HS code tariff schedule lookup — base MFN duty rate + steel-derivative schedule membership
CREATE TABLE hs_code_rate (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_code             VARCHAR(10)  NOT NULL UNIQUE,
    description         VARCHAR(200),
    base_duty_rate      NUMERIC(8,6) NOT NULL DEFAULT 0,
    is_steel_derivative INTEGER      NOT NULL DEFAULT 1
);

-- 5. CustomsEntry header
CREATE TABLE customs_entry (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_number        VARCHAR(30)  NOT NULL UNIQUE,
    importer_name       VARCHAR(100) NOT NULL,
    ship_date           DATE         NOT NULL,
    country_origin_id   INTEGER      NOT NULL REFERENCES country_origin(id),
    province_id         INTEGER      NOT NULL REFERENCES province(id),
    sys_config_id       INTEGER      NOT NULL DEFAULT 1 REFERENCES sys_config(id),
    -- copied from sys_config (Rule.copy)
    effective_date      DATE,
    program_code        VARCHAR(20),
    pc_number           VARCHAR(20),
    -- copied from country_origin / province (Rule.copy)
    country_surtax_rate NUMERIC(8,6) DEFAULT 0,
    province_tax_rate   NUMERIC(8,4) DEFAULT 0,
    -- derived (Rule.formula / Rule.sum)
    surtax_applicable   INTEGER      DEFAULT 0,
    total_customs_value NUMERIC(15,2) DEFAULT 0,
    total_duty_amount   NUMERIC(15,2) DEFAULT 0,
    total_surtax_amount NUMERIC(15,2) DEFAULT 0,
    duty_paid_value     NUMERIC(15,2) DEFAULT 0,
    sales_tax_amount    NUMERIC(15,2) DEFAULT 0,
    total_tax_due       NUMERIC(15,2) DEFAULT 0,
    notes               VARCHAR(200)
);

-- 6. SurtaxLineItem detail — one per imported product HS code
CREATE TABLE surtax_line_item (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customs_entry_id    INTEGER      NOT NULL REFERENCES customs_entry(id),
    hs_code_id          INTEGER      NOT NULL REFERENCES hs_code_rate(id),
    line_number         INTEGER      NOT NULL DEFAULT 1,
    description         VARCHAR(200),
    customs_value       NUMERIC(15,2) NOT NULL DEFAULT 0,
    -- copied from hs_code_rate (Rule.copy)
    base_duty_rate      NUMERIC(8,6) DEFAULT 0,
    is_steel_derivative INTEGER      DEFAULT 1,
    -- derived (Rule.formula)
    surtax_applicable   INTEGER      DEFAULT 0,
    base_duty_amount    NUMERIC(15,2) DEFAULT 0,
    surtax_amount       NUMERIC(15,2) DEFAULT 0
);
