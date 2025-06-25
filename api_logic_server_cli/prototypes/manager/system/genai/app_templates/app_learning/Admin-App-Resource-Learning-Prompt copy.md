## Context

Generate a per-resource file for a React Admin application using the following instructions.  
The result must be a runnable React app (`npm start`) that connects to the supplied JSON:API, with fully implemented components (no placeholders or empty files).

---

### Per-Resource Files (Required)

For each resource (`Customer`, `Order` etc):

* Create a source file under `src/`, e.g., `Customer.js`
* Each file must **fully** implement:
    * `CustomerList`
    * `CustomerShow`
    * `CustomerCreate`
    * `CustomerEdit`

Use:

- `<ReferenceField>` for foreign key displays
- `<ReferenceInput>` for foreign key input
- `<ReferenceManyField>` for tabbed child lists
- For show pages

  * Always start with `<SimpleShowLayout>`, followed by a `<TabbedShowLayout>` for related data
    * DO NOT start with `<TabbedShowLayout>`

Use the attribute order from the schema.

You may add other imports, but be sure imports below are included.

DO NOT use `<EmailInput>` - use `<TextInput>`.

DO NOT put `<ReferenceField>` in `<Datagrid>`.

Do **not leave any file empty**.

Sample code for each resource (follow these guidelines EXACTLY):

```jsx
import React from 'react';
import { List, FunctionField, Datagrid, TextField, DateField, NumberField, ReferenceField, ReferenceManyField, Show, TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput, ReferenceInput, SelectInput, Create, SimpleForm, Edit, Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin';  // mandatory imports

import { Grid, Typography, Box, Divider } from '@mui/material';


// Filter for Customer List
const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="name" alwaysOn />
        <BooleanInput label="Email Opt Out" source="email_opt_out" />
    </Filter>
);

// Customer List
export const CustomerList = (props) => {
    return (
        <List filters={<CustomerFilter />} {...props} sort={{ field: 'name', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="name" label="Name" />
                <NumberField source="balance" label="Balance" />
                ...
            </Datagrid>
        </List>
    );
};


// Customer Show
export const CustomerShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Customer Information
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Name">
                                    <TextField source="name" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Balance">
                                    <NumberField source="balance" options={{ style: 'currency', currency: 'USD' }} />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                    ...
                    <Divider sx={{ my: 2 }} />
                </Box>
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Orders">
                    <ReferenceManyField reference="Order" target="customer_id" addLabel={false} pagination={<Pagination />}>
                        <Datagrid rowClick="show">
                            <TextField source="id" label="Order ID" />
                            <TextField source="notes" label="Notes" />
                            <DateField source="CreatedOn" label="Created On" />
                            <NumberField source="amount_total" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
                            <DateField source="date_shipped" label="Date Shipped" />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                ...
            </TabbedShowLayout>
        </Show>
    );
};

// generate similar multi-column blocks (e.g., box) for edit and create, using <Edit {...props} redirect={false}>

export default {
    list: CustomerList,
    show: CustomerShow,
    create: CustomerCreate,
    edit: CustomerEdit,
};

```

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

  - The tab (with OrderList) is shown *below* all the Customer fields.
- Each Order in the tab links to Order Display

### Automatic Joins

For foreign keys:

- Display joined value (e.g., `product.name` instead of `product_id`)
- Use first string field from parent table containing `name`, `title`, or `description`

Numeric Primary key fields:

- Display at the end of forms/lists

### Lookups (Foreign Keys)

For foreign key fields:

- Provide auto-complete dropdown (`<ReferenceInput>`)
- For numeric foreign keys, use the joined string field as lookup text

### Cascade Add

When adding a child row as a detail in a Master / Detail,
default the Foreign Key to the Parent (Master) Primary Key.

## Implementation

### Architecture

- **Framework**: React 18 + react-admin 4.x
- **Data Provider**: Custom pre-built in src/rav4-jsonapi-client
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

## Response Format

Format the response as a JSResponseFormat:

class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)
