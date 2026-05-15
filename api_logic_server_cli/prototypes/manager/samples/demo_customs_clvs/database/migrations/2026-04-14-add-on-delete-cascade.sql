-- Rebuild shipment child tables to enforce DB-level cascade deletes.
-- Target DB: samples/requirements/customs_demo/database/customs.sqlite

PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

CREATE TABLE piece_new (
    local_piece_oid_nbr INTEGER NOT NULL,
    local_shipment_oid_nbr INTEGER,
    arrival_port_cd VARCHAR(5),
    awb_type_cd VARCHAR(1),
    awb_format_cd VARCHAR(1),
    contract_wgt_type_cd VARCHAR(1),
    customs_value_amt DECIMAL(16, 4),
    decln_oid_nbr INTEGER,
    decln_status_cd VARCHAR(1),
    dest_location_cd VARCHAR(5),
    dim_wgt DECIMAL(9, 1),
    final_dest_cd VARCHAR(5),
    form_type_cd VARCHAR(4),
    harmonized_tariff_nbr VARCHAR(20),
    ipd_doc_nbr VARCHAR(12),
    last_foreign_port_cd VARCHAR(5),
    last_modified_location_cd VARCHAR(5),
    last_modified_nm VARCHAR(35),
    manifest_status_cd VARCHAR(2),
    manifest_tmstp DATETIME,
    payment_option_cd VARCHAR(1),
    payor_account_nbr INTEGER,
    payor_account_type_cd VARCHAR(1),
    piece_qty INTEGER,
    piece_status_cd VARCHAR(1),
    piece_type_cd VARCHAR(1),
    port_of_export_cd VARCHAR(5),
    port_of_unlading_cd VARCHAR(5),
    rih_clearance_loc_cd VARCHAR(5),
    shipper_reference_desc VARCHAR(35),
    split_billing_business_cd VARCHAR(12),
    split_billing_address_amt DECIMAL(16, 4),
    split_billing_kilo_wgt DECIMAL(16, 4),
    split_billing_currency_cd VARCHAR(3),
    total_wgt DECIMAL(7, 1),
    total_wgt_uom_cd VARCHAR(3),
    tracking_nbr VARCHAR(12),
    transaction_seq_tmstp DATETIME,
    variable_pct INTEGER,
    xref_nbr VARCHAR(12),
    etl_tmstp DATETIME,
    shipment_type_cd INTEGER,
    split_seq_nbr INTEGER DEFAULT 0,
    piece_deleted_flg VARCHAR(1),
    piece_seq_nbr INTEGER,
    piece_movement_flg VARCHAR(1),
    PRIMARY KEY (local_piece_oid_nbr),
    FOREIGN KEY(local_shipment_oid_nbr) REFERENCES shipment (local_shipment_oid_nbr) ON DELETE CASCADE
);

INSERT INTO piece_new SELECT * FROM piece;
DROP TABLE piece;
ALTER TABLE piece_new RENAME TO piece;

CREATE TABLE shipment_party_new (
    shipment_party_oid_nbr INTEGER NOT NULL,
    local_shipment_oid_nbr INTEGER,
    shipment_party_type_cd VARCHAR(1),
    clearance_location_cd VARCHAR(5),
    address_qty INTEGER,
    broker_id_cd VARCHAR(4),
    city_nm VARCHAR(35),
    contact_phone_nbr VARCHAR(20),
    country_cd VARCHAR(2),
    country_sub_entity_cd VARCHAR(9),
    customer_acct_nbr INTEGER,
    customs_id_cd VARCHAR(18),
    customs_self_assessment_flg VARCHAR(1),
    company_nm VARCHAR(70),
    contact_nm VARCHAR(35),
    email_nm VARCHAR(255),
    last_modified_nm VARCHAR(35),
    last_modified_tmstp DATETIME,
    postal_cd VARCHAR(15),
    state_cd VARCHAR(2),
    etl_tmstp DATETIME,
    shipment_type_cd INTEGER,
    csa_business_nbr VARCHAR(25),
    local_piece_oid_nbr INTEGER,
    piece_shpmt_type_cd INTEGER,
    split_seq_nbr INTEGER,
    business_nbr VARCHAR(15),
    cfia_payor_nm VARCHAR(35),
    cfia_account_nbr VARCHAR(15),
    fax_nbr VARCHAR(15),
    pref_cont_mthd_cd VARCHAR(2),
    additional_contact_flg VARCHAR(1) DEFAULT 'N',
    PRIMARY KEY (shipment_party_oid_nbr),
    FOREIGN KEY(local_shipment_oid_nbr) REFERENCES shipment (local_shipment_oid_nbr) ON DELETE CASCADE,
    FOREIGN KEY(local_piece_oid_nbr) REFERENCES piece (local_piece_oid_nbr) ON DELETE CASCADE
);

INSERT INTO shipment_party_new SELECT * FROM shipment_party;
DROP TABLE shipment_party;
ALTER TABLE shipment_party_new RENAME TO shipment_party;

CREATE TABLE shipment_commodity_new (
    local_shipment_oid_nbr INTEGER NOT NULL,
    sequence_nbr INTEGER NOT NULL,
    clearance_country_cd VARCHAR(2),
    commodity_desc VARCHAR(300),
    commodity_wgt DECIMAL(12, 4),
    commodity_wgt_uom_cd VARCHAR(3),
    customs_value_amt DECIMAL(16, 4),
    export_cargo_control_nbr VARCHAR(6),
    export_license_expr_dt DATE,
    export_license_nbr VARCHAR(12),
    harmonized_tariff_nbr VARCHAR(20),
    hazardous_material_cd VARCHAR(4),
    last_modified_nm VARCHAR(35),
    last_modified_tmstp DATETIME,
    origin_country_cd VARCHAR(2),
    oversize_flg VARCHAR(1),
    piece_qty INTEGER,
    package_qty INTEGER,
    tariff_source_cd VARCHAR(1),
    etl_tmstp DATETIME,
    shipment_type_cd INTEGER,
    commodity_currency_cd VARCHAR(3),
    unit_of_measure_cd VARCHAR(3),
    classification_status_desc VARCHAR(200),
    classification_status_cd VARCHAR(10),
    part_expiration_dt DATE,
    PRIMARY KEY (local_shipment_oid_nbr, sequence_nbr),
    FOREIGN KEY(local_shipment_oid_nbr) REFERENCES shipment (local_shipment_oid_nbr) ON DELETE CASCADE
);

INSERT INTO shipment_commodity_new SELECT * FROM shipment_commodity;
DROP TABLE shipment_commodity;
ALTER TABLE shipment_commodity_new RENAME TO shipment_commodity;

CREATE TABLE special_handling_new (
    id INTEGER NOT NULL,
    oid_nbr INTEGER,
    oid_type_cd VARCHAR(1),
    special_handling_cd VARCHAR(5),
    etl_tmstp DATETIME,
    shipment_type_cd INTEGER,
    PRIMARY KEY (id),
    FOREIGN KEY(oid_nbr) REFERENCES shipment (local_shipment_oid_nbr) ON DELETE CASCADE
);

INSERT INTO special_handling_new SELECT * FROM special_handling;
DROP TABLE special_handling;
ALTER TABLE special_handling_new RENAME TO special_handling;

COMMIT;
PRAGMA foreign_keys = ON;
