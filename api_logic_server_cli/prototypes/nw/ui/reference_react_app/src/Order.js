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
        <TextInput label="Search" source="ShipName" alwaysOn />
        <BooleanInput label="Ready" source="Ready" />
    </Filter>
);

// Order List
export const OrderList = (props) => {
    return (
        <List filters={<OrderFilter />} {...props} sort={{ field: 'OrderDate', order: 'DESC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="Id" label="Order ID" />
                <ReferenceField label="Customer" source="CustomerId" reference="Customer">
                    <TextField source="CompanyName" />
                </ReferenceField>
                <DateField source="OrderDate" label="Order Date" />
                <NumberField source="AmountTotal" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
                <BooleanField source="Ready" label="Ready" />
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
            <TabbedShowLayout>
                <Tab label="Summary">
                    <SimpleShowLayout>
                        <Box sx={{ mb: 3 }}>
                            <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                                Order Information
                            </Typography>
                            <Grid container spacing={3} sx={{ mb: 2 }}>
                                <Grid item xs={12} sm={6} md={4}>
                                    <Box sx={{ p: 1 }}>
                                        <Labeled label="Order ID">
                                            <TextField source="Id" />
                                        </Labeled>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={4}>
                                    <Box sx={{ p: 1 }}>
                                        <Labeled label="Order Date">
                                            <DateField source="OrderDate" />
                                        </Labeled>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={4}>
                                    <Box sx={{ p: 1 }}>
                                        <ReferenceField label="Customer" source="CustomerId" reference="Customer">
                                            <TextField source="CompanyName" />
                                        </ReferenceField>
                                    </Box>
                                </Grid>
                                <Grid item xs={12} sm={6} md={4}>
                                    <Box sx={{ p: 1 }}>
                                        <Labeled label="Amount Total">
                                            <NumberField source="AmountTotal" options={{ style: 'currency', currency: 'USD' }} />
                                        </Labeled>
                                    </Box>
                                </Grid>
                            </Grid>
                            <Divider sx={{ my: 2 }} />
                        </Box>
                    </SimpleShowLayout>
                </Tab>
                <Tab label="Order Details">
                    <ReferenceManyField reference="OrderDetail" target="OrderId" addLabel={false} pagination={<Pagination />}>
                        <Datagrid rowClick="edit">
                            <TextField source="Id" label="Detail ID" />
                            <ReferenceField label="Product" source="ProductId" reference="Product">
                                <TextField source="ProductName" />
                            </ReferenceField>
                            <NumberField source="Quantity" label="Quantity" />
                            <NumberField source="UnitPrice" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </Show>
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
                                <ReferenceInput source="CustomerId" reference="Customer" fullWidth>
                                    <SelectInput optionText="CompanyName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput label="Order Date" source="OrderDate" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Freight" label="Freight" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
                <BooleanInput source="Ready" label="Ready" />
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
                                <ReferenceInput source="CustomerId" reference="Customer" fullWidth>
                                    <SelectInput optionText="CompanyName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput label="Order Date" source="OrderDate" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Freight" label="Freight" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
                <BooleanInput source="Ready" label="Ready" />
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