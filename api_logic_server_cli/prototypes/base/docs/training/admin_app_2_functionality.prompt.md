

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

**Default: generate one resource file per step, report as you go.**

Process resources one at a time — read that resource's schema slice from `admin.yaml`,
generate that resource's complete `.js` file, move to the next. This is the default, not a
hard rule enforced by a token-overflow constraint: that constraint applied to the original
ChatGPT-based generator (`genai_react_app.py`, `a_generate_resource_files()`), which made one
stateless API call per resource because a single-shot completion had no way to recover if it
ran out of room mid-file, and generating the entire app in one call did not work reliably.

An AI assistant with a full session (not a single stateless completion) may not have the
same ceiling — you can hold more schema in context and self-check output as you go. Use
judgment: if a project has few resources, generating more than one file per step is fine if
you're confident in the result. If a project has many resources, or you're unsure, fall back
to one-at-a-time. Either way, **report per-file progress and timing** — this is required
regardless of batching, since it's the visibility a raw API call never had:
- After each resource file (or batch): file name(s), what it implements
  (List/Show/Create/Edit), and how long that step took (wall-clock).
- After `App.js` wiring: same, one line. This step is always separate — it's just imports +
  `<Resource>` registration, not per-table content, and depends on every resource file
  already existing.
- At the end: a total summary — every file produced, its one-line description, its
  individual time, and the **total elapsed time** for the whole generation run — the same
  way other generation steps in this project (Method 4, Executable Requirements) report back
  with a summary instead of silently finishing.

---

## App Wiring

In `App.js`:
- Import each resource file
- Register them in `<Admin>` using:

```jsx
<Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
```
