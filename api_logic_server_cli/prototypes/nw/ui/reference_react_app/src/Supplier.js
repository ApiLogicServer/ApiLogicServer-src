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

const SupplierFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
    </Filter>
);

// Supplier List
export const SupplierList = (props) => {
    return (
        <List 
            filters={<SupplierFilter />} 
            {...props} 
            sort={{ field: 'CompanyName', order: 'ASC' }} 
            pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="CompanyName" label="Company Name" />
                <TextField source="ContactName" label="Contact Name" />
                <TextField source="ContactTitle" label="Contact Title" />
                <TextField source="City" label="City" />
                <TextField source="Country" label="Country" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// Supplier Show
export const SupplierShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Supplier Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Labeled label="Company Name">
                            <TextField source="CompanyName" />
                        </Labeled>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Labeled label="Contact Name">
                            <TextField source="ContactName" />
                        </Labeled>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Labeled label="Contact Title">
                            <TextField source="ContactTitle" />
                        </Labeled>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </SimpleShowLayout>
        </Show>
    );
};

// Supplier Create
export const SupplierCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Supplier
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="CompanyName" label="Company Name" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="ContactName" label="Contact Name" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="Address" label="Address" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="City" label="City" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="Country" label="Country" fullWidth />
                    </Grid>
                </Grid>
            </SimpleForm>
        </Create>
    );
};

// Supplier Edit
export const SupplierEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Supplier
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="CompanyName" label="Company Name" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="ContactName" label="Contact Name" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="Address" label="Address" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="City" label="City" fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="Country" label="Country" fullWidth />
                    </Grid>
                </Grid>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: SupplierList,
    show: SupplierShow,
    create: SupplierCreate,
    edit: SupplierEdit,
};