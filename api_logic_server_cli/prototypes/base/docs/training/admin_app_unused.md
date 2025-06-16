
Generate a full React Admin application using the following instructions.  
The result must be a runnable React app (`npm start`) that connects to the supplied JSON:API, with fully implemented components (no placeholders or empty files).

## Backend Description

The JSON:API backend is described by:

### 1. Schema (`docs/db.dbml`):

```dbml
Table Customer {
    id INTEGER [primary key]
    name VARCHAR 
    balance DECIMAL 
    credit_limit DECIMAL 
    email VARCHAR 
    email_opt_out BOOLEAN 
}

Table Item {
    id INTEGER [primary key]
    order_id INTEGER 
    product_id INTEGER 
    quantity INTEGER 
    amount DECIMAL 
    unit_price DECIMAL 
}

Table Order {
    id INTEGER [primary key]
    notes VARCHAR 
    customer_id INTEGER 
    CreatedOn DATE 
    date_shipped DATE 
    amount_total DECIMAL 
}

Table Product {
    id INTEGER [primary key]
    name VARCHAR 
    unit_price DECIMAL 
}

// Relationships
Ref: Item.(order_id) < Order.(id)
Ref: Item.(product_id) < Product.(id)
Ref: Order.(customer_id) < Customer.(id)
```

### 2. JSON:API Discovery (`docs/mcp_learning/mcp_discovery.json`):

- Base URL: `http://localhost:5656/api`
- Auth: `http://localhost:5656/api/auth/login`
- Tool type: `json-api`
- Describes four resources: Customer, Order, Item, Product

---

## App Features

### Multi-Page

For each resource:
- Create a **List page** showing 7 user-friendly columns
- Add **pagination**, **sorting**, and **filtering**
- Link each row to a **Display (Show) page**

### Multi-Resource

Each **Display Page** should:
- Show all fields in a **multi-column layout**
- Include a **tab sheet** (`<TabbedShowLayout>`) for each related resource using `<ReferenceManyField>`
- Link child rows to their own display page

Example:  
- Customer Display has tab for OrderList  
- Each Order in the tab links to Order Display

### Automatic Joins

For foreign keys:
- Display joined value (e.g., `product.name` instead of `product_id`)
- Use first string field from parent table containing `name`, `title`, or `description`

Primary key fields:
- Display at the end of forms/lists

### Lookups (Foreign Keys)

For foreign key fields:
- Provide auto-complete dropdown (`<ReferenceInput>`)
- For numeric foreign keys, use the joined string field as lookup text

---

## Per-Resource Files (Required)

For each resource (`Customer`, `Order`, `Product`, `Item`):
- Create a source file under `src/`, e.g., `Customer.js`
- **Each file must fully implement**:
  - `CustomerList`
  - `CustomerShow`
  - `CustomerCreate`
  - `CustomerEdit`

Use:
- `<ReferenceField>` for foreign key displays
- `<ReferenceInput>` for foreign key input
- `<ReferenceManyField>` for tabbed child lists
- `<TabbedShowLayout>` for display pages

Do **not leave any file empty**.

---

## App Wiring

In `App.js`:
- Import each resource file
- Register them in `<Admin>` using:

```jsx
<Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
```

---

## Architecture

- **Framework**: React 18 + react-admin 4.x
- **Data Provider**: Custom `dataProvider.js` using `fetchUtils` (no external `ra-jsonapi-client`)
  - Must support: `getList`, `getOne`, `getMany`, `getManyReference`, `create`, `update`, `delete`
  - Must support: filters, joins, sorting, pagination
- **Backend**: JSON:API per `mcp_discovery.json`
- **CORS**: Ensure API allows `http://localhost:3000`
  ```py
  from flask_cors import CORS  
  CORS(app, origins='*')  # or restrict to localhost:3000
  ```
- **Project Setup**:
  - Use `create-react-app`
  - Include: `react-admin`, `@mui/material`, `@emotion/react`, `@emotion/styled`, `react-router-dom`
  - Do not use any deprecated or unmaintained libraries
  - Include complete and correct `App.js`, `index.js`, `dataProvider.js`, and `index.html`

---

## Run Instructions

```bash
npm install
npm start
```

Then open in browser: `http://localhost:3000`
