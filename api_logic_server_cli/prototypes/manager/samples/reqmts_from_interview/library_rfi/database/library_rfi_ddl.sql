-- library_rfi schema
-- 4a: constants extracted to sys_config (fine_rate_per_day, fine_cap_per_book,
--     fine_block_threshold, loan_period_days)
-- 4b: FKs -- loan.member_id, loan.book_id, hold.member_id, hold.book_id

ALTER TABLE sys_config ADD COLUMN fine_rate_per_day REAL DEFAULT 0.25;
ALTER TABLE sys_config ADD COLUMN fine_cap_per_book REAL DEFAULT 10.0;
ALTER TABLE sys_config ADD COLUMN fine_block_threshold REAL DEFAULT 5.0;
ALTER TABLE sys_config ADD COLUMN loan_period_days INTEGER DEFAULT 21;

CREATE TABLE member (
    id                     INTEGER PRIMARY KEY AUTOINCREMENT,
    name                   TEXT NOT NULL,
    email                  TEXT,
    sys_config_id          INTEGER DEFAULT 1 REFERENCES sys_config(id),
    fine_block_threshold   REAL DEFAULT 0,   -- mirror, Rule.copy from sys_config
    fine_balance           REAL DEFAULT 0,   -- Rule.sum of loan.fine_balance
    blocked                INTEGER DEFAULT 0 -- Rule.formula: 1 if fine_balance >= fine_block_threshold
);

CREATE TABLE book (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    title              TEXT NOT NULL,
    author             TEXT,
    active_loan_count  INTEGER DEFAULT 0,  -- Rule.count: loans not yet returned
    hold_count         INTEGER DEFAULT 0,  -- Rule.count: waiting holds
    available          INTEGER DEFAULT 1   -- Rule.formula: active_loan_count == 0
);

CREATE TABLE loan (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id           INTEGER NOT NULL REFERENCES member(id),
    book_id             INTEGER NOT NULL REFERENCES book(id),
    checkout_date        TEXT NOT NULL,
    due_date            TEXT,               -- Rule.formula: checkout_date + loan_period_days (x2 if renewed)
    return_date         TEXT,               -- set by client on return
    renewed             INTEGER DEFAULT 0,  -- client sets 0->1 to request renewal
    sys_config_id       INTEGER DEFAULT 1 REFERENCES sys_config(id),
    fine_rate_per_day   REAL DEFAULT 0,     -- mirror, Rule.copy from sys_config
    fine_cap_per_book   REAL DEFAULT 0,     -- mirror, Rule.copy from sys_config
    loan_period_days    INTEGER DEFAULT 0,  -- mirror, Rule.copy from sys_config
    fine_amount         REAL DEFAULT 0,     -- Rule.formula: days late * rate, capped
    fine_paid           REAL DEFAULT 0,     -- client-recorded payment
    fine_balance        REAL DEFAULT 0      -- Rule.formula: fine_amount - fine_paid
);

CREATE TABLE hold (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id       INTEGER NOT NULL REFERENCES member(id),
    book_id         INTEGER NOT NULL REFERENCES book(id),
    requested_date  TEXT NOT NULL,
    status          TEXT DEFAULT 'waiting'  -- 'waiting' | 'ready' | 'fulfilled' | 'cancelled'
);
