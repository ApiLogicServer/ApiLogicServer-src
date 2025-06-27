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

const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
        <BooleanInput label="Email Opt Out" source="email_opt_out" />
    </Filter>
);

// Customer List
export const CustomerList = (props) => (
    <List filters={<CustomerFilter />} {...props} sort={{ field: 'CompanyName', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
        <Datagrid rowClick="show">
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="ContactName" label="Contact Name" />
            <TextField source="City" label="City" />
            <TextField source="Country" label="Country" />
            <NumberField source="Balance" label="Balance" options={{ style: 'currency', currency: 'USD' }} />
            <EditButton />
            <DeleteButton />
        </Datagrid>
    </List>
);

// Customer Show
export const CustomerShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Customer Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Company Name">
                                <TextField source="CompanyName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Balance">
                                <NumberField source="Balance" options={{ style: 'currency', currency: 'USD' }} />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Contact Name">
                                <TextField source="ContactName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Contact Title">
                                <TextField source="ContactTitle" />
                            </Labeled>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Orders">
                <ReferenceManyField reference="Order" target="CustomerId" addLabel={false} pagination={<Pagination />}>
                    <Datagrid rowClick="show">
                        <TextField source="Id" label="Order ID" />
                        <TextField source="ShipName" label="Ship Name" />
                        <DateField source="OrderDate" label="Order Date" />
                        <NumberField source="AmountTotal" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
                        <DateField source="ShippedDate" label="Shipped Date" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
                <AddOrderButton />
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Custom Add Order Button
const AddOrderButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Order/create?source=${encodeURIComponent(JSON.stringify({ CustomerId: record?.id }))}`);
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
export const CustomerCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Customer
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="CompanyName" label="Company Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactName" label="Contact Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="Balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Create>
);

// Customer Edit
export const CustomerEdit = (props) => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Customer
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="CompanyName" label="Company Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactName" label="Contact Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="Balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Edit>
);

export default {
    list: CustomerList,
    show: CustomerShow,
    create: CustomerCreate,
    edit: CustomerEdit,
};