
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

// generate pages and components...

const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="name" alwaysOn />
        <BooleanInput label="Email Opt Out" source="email_opt_out" />
    </Filter>
);

// Customer List
export const CustomerList = (props) => (
    <List filters={<CustomerFilter />} {...props} sort={{ field: 'name', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
        <Datagrid rowClick="show">
            <TextField source="name" label="Name" />
            <NumberField source="balance" label="Balance" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="credit_limit" label="Credit Limit" options={{ style: 'currency', currency: 'USD' }} />
            <TextField source="email" label="Email" />
            <BooleanField source="email_opt_out" label="Email Opt Out" />
        </Datagrid>
    </List>
);

// Custom Add Order Button
const AddOrderButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
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
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Credit Limit">
                                <NumberField source="credit_limit" options={{ style: 'currency', currency: 'USD' }} />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Email">
                                <TextField source="email" />
                            </Labeled>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Orders">
                <ReferenceManyField reference="Order" target="customer_id" addLabel={false} pagination={<Pagination />}>                    
                    <Datagrid>
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
            <Tab label="Emails">
                <ReferenceManyField reference="SysEmail" target="customer_id" addLabel={false} pagination={<Pagination />}>                    
                    <Datagrid>
                        <TextField source="id" label="Email ID" />
                        <TextField source="subject" label="Subject" />
                        <TextField source="message" label="Message" />
                        <DateField source="CreatedOn" label="Created On" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

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
                            <TextInput source="name" label="Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="credit_limit" label="Credit Limit" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="email" label="Email" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <BooleanInput source="email_opt_out" label="Email Opt Out" />
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
                            <TextInput source="name" label="Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="credit_limit" label="Credit Limit" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="email" label="Email" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <BooleanInput source="email_opt_out" label="Email Opt Out" />
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