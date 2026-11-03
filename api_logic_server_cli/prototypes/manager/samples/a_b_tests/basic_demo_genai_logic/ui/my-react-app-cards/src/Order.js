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

const OrderFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="id" alwaysOn />
    </Filter>
);

// Order List
export const OrderList = (props) => {
    return (
        <List filters={<OrderFilter />} {...props} sort={{ field: 'id', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="id" label="Order ID" />
                <DateField source="CreatedOn" label="Created On" />
                <NumberField source="amount_total" label="Total Amount" options={{ style: 'currency', currency: 'USD' }} />
                <DateField source="date_shipped" label="Date Shipped" />
                <ReferenceField source="customer_id" reference="Customer" label="Customer">
                    <TextField source="name" />
                </ReferenceField>
            </Datagrid>
        </List>
    );
};

// Order Show
export const OrderShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Order Details
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', mb: 2 }}>
                    <Box sx={{ width: '50%' }}>
                        <Labeled label="Order ID">
                            <TextField source="id" />
                        </Labeled>
                    </Box>
                    <Box sx={{ width: '50%' }}>
                        <Labeled label="Total Amount">
                            <NumberField source="amount_total" options={{ style: 'currency', currency: 'USD' }} />
                        </Labeled>
                    </Box>
                </Box>
                <Box sx={{ mb: 2 }}>
                    <Labeled label="Created On">
                        <DateField source="CreatedOn" />
                    </Labeled>
                </Box>
                <Box sx={{ mb: 2 }}>
                    <Labeled label="Date Shipped">
                        <DateField source="date_shipped" />
                    </Labeled>
                </Box>
                <Divider sx={{ my: 2 }} />
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Customer">
                    <ReferenceField source="customer_id" reference="Customer" addLabel={false}>
                        <SimpleShowLayout>
                            <Labeled label="Name">
                                <TextField source="name" />
                            </Labeled>
                            <Labeled label="Email">
                                <EmailField source="email" />
                            </Labeled>
                        </SimpleShowLayout>
                    </ReferenceField>
                </Tab>
                <Tab label="Items">
                    <ReferenceManyField reference="Item" target="order_id" addLabel={false} pagination={<Pagination />}>
                        <Datagrid rowClick="show">
                            <TextField source="id" label="Item ID" />
                            <NumberField source="quantity" label="Quantity" />
                            <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                    <AddItemButton />
                </Tab>
            </TabbedShowLayout>
        </Show>
    );
};

// Custom Add Item Button
const AddItemButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Item/create?source=${encodeURIComponent(JSON.stringify({ order_id: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
        >
            Add New Item
        </Button>
    );
};

// Order Create
export const OrderCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Order
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <ReferenceInput source="customer_id" reference="Customer" fullWidth>
                                <SelectInput optionText="name" validate={required()} />
                            </ReferenceInput>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <DateTimeInput source="CreatedOn" label="Created On" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="amount_total" label="Total Amount" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </SimpleForm>
        </Create>
    );
};

// Order Edit
export const OrderEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Order
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <ReferenceInput source="customer_id" reference="Customer" fullWidth>
                                <SelectInput optionText="name" validate={required()} />
                            </ReferenceInput>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <DateTimeInput source="CreatedOn" label="Created On" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="amount_total" label="Total Amount" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: OrderList,
    show: OrderShow,
    create: OrderCreate,
    edit: OrderEdit,
};