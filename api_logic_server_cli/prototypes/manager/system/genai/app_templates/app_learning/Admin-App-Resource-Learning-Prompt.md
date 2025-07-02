## Context

Generate the {{resource.js}} file for a React Admin application using the following instructions.  

---

### Per-Resource Files (Required)

Sample code (follow these guidelines EXACTLY):
```
<sample-code>
// begin MANDATORY imports (always generated EXACTLY)
import React from 'react';
import { List, FunctionField, Datagrid, TextField, EmailField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button } from '@mui/material';
import { useRecordContext, useRedirect, Link, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
// end mandatory imports

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
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                    <AddOrderButton />
                </Tab>
                ...
            </TabbedShowLayout>
        </Show>
    );
};

// Custom Add Order Button
const AddOrderButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        // Use the newer React Admin approach for pre-filling forms
        redirect(`/Order/create?source=${encodeURIComponent(JSON.stringify({ customer_id: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add New Order
        </Button>
    );
};

// Customer Create
export const CustomerCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Customer
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="name" label="Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="balance" label="Balance" fullWidth />
                            </Box>
                        </Grid>
                        ...
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Customer Edit
export const CustomerEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Customer
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="name" label="Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="balance" label="Balance" fullWidth />
                            </Box>
                        </Grid>
                        ...
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: CustomerList,
    show: CustomerShow,
    create: CustomerCreate,
    edit: CustomerEdit,
};
```
</sample-code>


For each resource (`Customer`, `Order` etc) and **fully** implement:
    * `CustomerList`
    * `CustomerShow`
    * `CustomerCreate`
    * `CustomerEdit`

Use:

- `<ReferenceField>` for foreign key displays
- `<ReferenceInput>` for foreign key input, like this (IMPORTANT: validate is on SelectInput, NEVER ReferenceInput )
```
<ReferenceInput source="customer_id" reference="Customer" fullWidth>
    <SelectInput optionText="name" validate={required()} />
</ReferenceInput>
```
- `<ReferenceManyField>` for tabbed child lists

Use the attribute order from the schema.

DO NOT use `<EmailInput>` - use `<TextInput>`.

DO NOT put `<ReferenceField>` in `<Datagrid>`.

---

### Architecture

- **Framework**: React 18 + react-admin 4.x
- **Data Provider**: Custom pre-built in src/rav4-jsonapi-client
- **CORS**: Ensure API allows `http://localhost:3000`

```py
  from flask_cors import CORS  
  CORS(app, origins='*')  # or restrict to localhost:3000
```

## Response Format

Format the response as a JSResponseFormat:

class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)
