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

const ShipperFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="CompanyName" alwaysOn />
    </Filter>
);

// Shipper List
export const ShipperList = (props) => {
    return (
        <List filters={<ShipperFilter />} {...props} sort={{ field: 'CompanyName', order: 'ASC' }}>
            <Datagrid rowClick="show">
                <TextField source="CompanyName" label="Company Name" />
                <TextField source="Phone" label="Phone" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// Shipper Show
export const ShipperShow = (props) => {
    return (
        <Show {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Shipper Information
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextField source="CompanyName" label="Company Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextField source="Phone" label="Phone" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Show>
    );
};

// Shipper Create
export const ShipperCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Shipper
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="CompanyName" label="Company Name" validate={required()} fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Phone" label="Phone" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Shipper Edit
export const ShipperEdit = (props) => {
    return (
        <Edit {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Shipper
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="CompanyName" label="Company Name" validate={required()} fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Phone" label="Phone" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: ShipperList,
    show: ShipperShow,
    create: ShipperCreate,
    edit: ShipperEdit,
};