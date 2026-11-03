-- demo_emp_types domain schema (applied to database/db.sqlite, then rebuild-from-database)
-- STI: one employee table, discriminator `type` ('salaried' | 'hourly' | 'commissioned'),
-- independent second axis `military` ('yes' | 'no').

-- Step 4a: constants -> sys_config (read with SysConfig.current(session), no FK)
ALTER TABLE sys_config ADD COLUMN max_hourly_weekly_salary REAL DEFAULT 5000.0;
ALTER TABLE sys_config ADD COLUMN military_stipend_per_service_year REAL DEFAULT 100.0;

CREATE TABLE department (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    budget        NUMERIC(15,2) NOT NULL DEFAULT 0,
    total_salary  NUMERIC(15,2) DEFAULT 0          -- derived: sum(Employee.salary)
);

-- "union" is an SQL keyword; table named labor_union, FK column keeps the prompt's union_id
CREATE TABLE labor_union (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    dues_rate  REAL NOT NULL DEFAULT 0
);

CREATE TABLE employee (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT NOT NULL,
    dept_id             INTEGER NOT NULL REFERENCES department(id),
    type                TEXT NOT NULL,              -- 'salaried' | 'hourly' | 'commissioned'
    salary              NUMERIC(15,2) DEFAULT 0,    -- entered (salaried); derived (hourly, commissioned)
    -- hourly only
    hours_worked        REAL,
    hourly_rate         REAL,
    union_id            INTEGER REFERENCES labor_union(id),
    union_dues          NUMERIC(15,2) DEFAULT 0,    -- derived
    -- commissioned only
    base_salary         NUMERIC(15,2),
    commission_total    NUMERIC(15,2) DEFAULT 0,    -- derived: sum(Order.amount)
    order_count         INTEGER DEFAULT 0,          -- derived: count(Order) (only commissioned may have Orders)
    -- military axis (independent of type)
    military            TEXT NOT NULL,              -- 'yes' | 'no' (no DEFAULT: LogicBank eager defaults copy TEXT default "'no'" with its quotes)
    branch              TEXT,                       -- 'Army','Navy','Air Force','Marines','Coast Guard'
    rank                TEXT,
    service_years       INTEGER,
    military_stipend    NUMERIC(15,2) DEFAULT 0,    -- derived
    total_compensation  NUMERIC(15,2) DEFAULT 0     -- derived
);

CREATE TABLE "order" (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id    INTEGER NOT NULL REFERENCES employee(id),
    customer_name  TEXT NOT NULL,
    amount         NUMERIC(15,2) NOT NULL DEFAULT 0
);
