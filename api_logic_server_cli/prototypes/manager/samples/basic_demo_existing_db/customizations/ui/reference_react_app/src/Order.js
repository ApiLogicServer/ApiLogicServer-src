// begin MANDATORY imports (always generated EXACTLY)
import React from 'react';
import { List, FunctionField, Datagrid, TextField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button } from '@mui/material';
import { useRecordContext, useRedirect, Link, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
// end mandatory imports

const OrderFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by ID" source="id" alwaysOn />
        <TextInput label="Customer ID" source="customer_id" />
    </Filter>
);

// Order List
export const OrderList = (props) => {
    return (
        <List filters={<OrderFilter />} {...props} sort={{ field: 'id', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="id" label="Order ID" />
                <TextField source="notes" label="Notes" />
                <ReferenceField label="Customer" source="customer_id" reference="Customer">
                    <TextField source="name" />
                </ReferenceField>
                <DateField source="CreatedOn" label="Created On" />
                <NumberField source="amount_total" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
                <DateField source="date_shipped" label="Date Shipped" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// Order Show
export const OrderShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Order Details
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Order ID">
                                    <TextField source="id" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Customer">
                                    <ReferenceField source="customer_id" reference="Customer">
                                        <TextField source="name" />
                                    </ReferenceField>
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Created On">
                                    <DateField source="CreatedOn" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Amount Total">
                                    <NumberField source="amount_total" options={{ style: 'currency', currency: 'USD' }} />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                    <Divider sx={{ my: 2 }} />
                </Box>
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Items">
                    <ReferenceManyField reference="Item" target="order_id" addLabel={false} pagination={<Pagination />}>
                        <Datagrid rowClick="show">
                            <TextField source="id" label="Item ID" />
                            <ReferenceField label="Product" source="product_id" reference="Product">
                                <TextField source="name" />
                            </ReferenceField>
                            <NumberField source="quantity" label="Quantity" />
                            <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                    <AddItemButton />
                </Tab>
                <Tab label="General">
                    <SimpleShowLayout>
                        <TextField source="notes" label="Notes" />
                        <DateField source="date_shipped" label="Date Shipped" />
                    </SimpleShowLayout>
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
            sx={{ mt: 2 }}
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
                <Box sx={{ mb: 3 }}>
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
                                <TextInput source="notes" label="Notes" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput source="CreatedOn" label="Created On" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Order Edit
export const OrderEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
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
                                <TextInput source="notes" label="Notes" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput source="CreatedOn" label="Created On" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
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