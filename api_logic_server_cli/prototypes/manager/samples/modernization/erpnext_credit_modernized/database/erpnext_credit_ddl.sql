-- erpnext_credit schema (docs/requirements/erpnext_credit/requirements.md)
-- Applied once to database/db.sqlite, then rebuild-from-database.

-- Accounts Settings.credit_controller (a role) -> singleton settings row
ALTER TABLE sys_config ADD COLUMN credit_controller TEXT;

CREATE TABLE company (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE,
    credit_limit    NUMERIC(15,2) DEFAULT 0          -- default credit limit (0 = no limit)
);

CREATE TABLE customer_group (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL UNIQUE
);

CREATE TABLE customer (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL UNIQUE,
    customer_group_id   INTEGER NOT NULL REFERENCES customer_group(id)
);

-- Derived bucket: one row per (customer, company); holds the outstanding parts (section 3)
CREATE TABLE customer_company (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id             INTEGER NOT NULL REFERENCES customer(id),
    company_id              INTEGER NOT NULL REFERENCES company(id),
    ledger_balance          NUMERIC(15,2) DEFAULT 0,  -- Rule.sum LedgerEntry.amount (not cancelled)
    open_sales_order_amount NUMERIC(15,2) DEFAULT 0,  -- Rule.sum SalesOrder.open_amount
    unbilled_delivery_amount NUMERIC(15,2) DEFAULT 0, -- Rule.sum DeliveryNote.unbilled_amount
    outstanding             NUMERIC(15,2) DEFAULT 0,  -- Rule.formula: sum of the 3 parts
    outstanding_ignoring_sales_orders NUMERIC(15,2) DEFAULT 0, -- Rule.formula: parts 1 + 3
    customer_credit_limit   NUMERIC(15,2) DEFAULT 0,  -- Rule.sum CustomerCreditLimit.credit_limit (<= 1 row)
    bypass_credit_limit_check INTEGER DEFAULT 0,      -- Rule.sum CustomerCreditLimit.bypass flag (<= 1 row)
    UNIQUE (customer_id, company_id)
);

CREATE TABLE customer_credit_limit (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id                 INTEGER NOT NULL REFERENCES customer(id),
    company_id                  INTEGER NOT NULL REFERENCES company(id),
    customer_company_id         INTEGER REFERENCES customer_company(id),  -- set by early_row_event
    credit_limit                NUMERIC(15,2) DEFAULT 0,
    bypass_credit_limit_check   INTEGER DEFAULT 0,
    UNIQUE (customer_id, company_id)
);

CREATE TABLE customer_group_credit_limit (
    id                          INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_group_id           INTEGER NOT NULL REFERENCES customer_group(id),
    company_id                  INTEGER NOT NULL REFERENCES company(id),
    credit_limit                NUMERIC(15,2) DEFAULT 0,
    bypass_credit_limit_check   INTEGER DEFAULT 0,
    UNIQUE (customer_group_id, company_id)
);

CREATE TABLE sales_order (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL REFERENCES customer(id),
    company_id          INTEGER NOT NULL REFERENCES company(id),
    customer_company_id INTEGER REFERENCES customer_company(id),  -- set by early_row_event
    grand_total         NUMERIC(15,2) DEFAULT 0,
    per_billed          NUMERIC(7,4) DEFAULT 0,       -- percent billed (input)
    status              TEXT DEFAULT 'Draft',          -- Draft, To Deliver and Bill, Closed, ...
    docstatus           INTEGER DEFAULT 0,             -- 0 draft, 1 submitted, 2 cancelled
    open_amount         NUMERIC(15,2) DEFAULT 0        -- Rule.formula (section 3 part 2)
);

CREATE TABLE sales_invoice (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL REFERENCES customer(id),
    company_id          INTEGER NOT NULL REFERENCES company(id),
    grand_total         NUMERIC(15,2) DEFAULT 0,
    is_return           INTEGER DEFAULT 0,
    is_opening          INTEGER DEFAULT 0,
    docstatus           INTEGER DEFAULT 0,
    unlinked_line_count INTEGER DEFAULT 0              -- Rule.count lines with no SO and no DN line link
);

CREATE TABLE delivery_note (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id         INTEGER NOT NULL REFERENCES customer(id),
    company_id          INTEGER NOT NULL REFERENCES company(id),
    customer_company_id INTEGER REFERENCES customer_company(id),  -- set by early_row_event
    grand_total         NUMERIC(15,2) DEFAULT 0,
    net_total           NUMERIC(15,2) DEFAULT 0,
    status              TEXT DEFAULT 'Draft',          -- Draft, Submitted, Closed, Stopped
    is_return           INTEGER DEFAULT 0,
    per_billed          NUMERIC(7,4) DEFAULT 0,        -- input (section 5: skipped when 100)
    docstatus           INTEGER DEFAULT 0,
    unbilled_line_total NUMERIC(15,2) DEFAULT 0,       -- Rule.sum DeliveryNoteItem.unbilled_amount
    unbilled_amount     NUMERIC(15,2) DEFAULT 0,       -- Rule.formula (note qualifies ? line total : 0)
    unlinked_line_count INTEGER DEFAULT 0,             -- Rule.count lines with no SO and no SI link
    no_invoice_line_count INTEGER DEFAULT 0,           -- Rule.count lines with no SI link
    uninvoiced_share    NUMERIC(15,2) DEFAULT 0,       -- Rule.sum DeliveryNoteItem.grand_total_share (no SI link)
    so_linked_uninvoiced_share NUMERIC(15,2) DEFAULT 0, -- Rule.sum DeliveryNoteItem.grand_total_share (SO link, no SI link)
    bypass_extra_amount NUMERIC(15,2) DEFAULT 0        -- Rule.formula (section 5 extra, flag on)
);

CREATE TABLE delivery_note_item (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_note_id    INTEGER NOT NULL REFERENCES delivery_note(id),
    qty                 NUMERIC(15,4) DEFAULT 0,
    returned_qty        NUMERIC(15,4) DEFAULT 0,
    net_amount          NUMERIC(15,2) DEFAULT 0,
    sales_order_id      INTEGER REFERENCES sales_order(id),
    sales_invoice_id    INTEGER REFERENCES sales_invoice(id),
    billed_qty          NUMERIC(15,4) DEFAULT 0,       -- Rule.sum SalesInvoiceItem.qty (submitted, not return)
    unbilled_amount     NUMERIC(15,2) DEFAULT 0,       -- Rule.formula (section 3 part 3, per line)
    grand_total_share   NUMERIC(15,2) DEFAULT 0        -- Rule.formula net_amount / note net_total x note grand_total (section 5)
);

CREATE TABLE sales_invoice_item (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    sales_invoice_id        INTEGER NOT NULL REFERENCES sales_invoice(id),
    qty                     NUMERIC(15,4) DEFAULT 0,
    sales_order_id          INTEGER REFERENCES sales_order(id),
    delivery_note_item_id   INTEGER REFERENCES delivery_note_item(id),
    counts_as_billed        INTEGER DEFAULT 0          -- Rule.formula: invoice submitted and not a return
);

CREATE TABLE journal_entry (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id          INTEGER NOT NULL REFERENCES company(id),
    docstatus           INTEGER DEFAULT 0
);

CREATE TABLE journal_entry_account (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    journal_entry_id    INTEGER NOT NULL REFERENCES journal_entry(id),
    party_type          TEXT,                           -- 'Customer' for customer lines
    customer_id         INTEGER REFERENCES customer(id), -- the party, when party_type = 'Customer'
    debit               NUMERIC(15,2) DEFAULT 0,
    credit              NUMERIC(15,2) DEFAULT 0
);

CREATE TABLE ledger_entry (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id             INTEGER NOT NULL REFERENCES customer(id),
    company_id              INTEGER NOT NULL REFERENCES company(id),
    customer_company_id     INTEGER REFERENCES customer_company(id),  -- set by early_row_event
    debit                   NUMERIC(15,2) DEFAULT 0,
    credit                  NUMERIC(15,2) DEFAULT 0,
    is_cancelled            INTEGER DEFAULT 0,
    amount                  NUMERIC(15,2) DEFAULT 0,    -- Rule.formula debit - credit
    sales_invoice_id        INTEGER REFERENCES sales_invoice(id),           -- posting source
    journal_entry_account_id INTEGER REFERENCES journal_entry_account(id)  -- posting source
);
