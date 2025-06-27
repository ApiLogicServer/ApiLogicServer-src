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

const EmployeeAuditFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="LastName" alwaysOn />
    </Filter>
);

// EmployeeAudit List
export const EmployeeAuditList = (props) => {
    return (
        <List filters={<EmployeeAuditFilter />} {...props} 
              sort={{ field: 'LastName', order: 'ASC' }} 
              pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="LastName" label="Last Name" />
                <TextField source="FirstName" label="First Name" />
                <TextField source="Title" label="Title" />
                <NumberField source="Salary" label="Salary" options={{ style: 'currency', currency: 'USD' }} />
                <DateField source="CreatedOn" label="Created On" />
                <TextField source="CreatedBy" label="Created By" />
                <DateField source="UpdatedOn" label="Updated On" />
                <TextField source="UpdatedBy" label="Updated By" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// EmployeeAudit Show
export const EmployeeAuditShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Employee Audit Entry Details
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Last Name">
                                    <TextField source="LastName" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="First Name">
                                    <TextField source="FirstName" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Title">
                                    <TextField source="Title" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Salary">
                                    <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                    <Divider sx={{ my: 2 }} />
                </Box>
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Details">
                    <Grid container spacing={3}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Created On">
                                    <DateField source="CreatedOn" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Created By">
                                    <TextField source="CreatedBy" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Updated On">
                                    <DateField source="UpdatedOn" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Updated By">
                                    <TextField source="UpdatedBy" />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                </Tab>
            </TabbedShowLayout>
        </Show>
    );
};

// EmployeeAudit Create
export const EmployeeAuditCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Employee Audit Entry
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Title" label="Title" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>

                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput source="CreatedOn" label="Created On" fullWidth disabled />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="CreatedBy" label="Created By" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// EmployeeAudit Edit
export const EmployeeAuditEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Employee Audit Entry
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Title" label="Title" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>

                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <DateTimeInput source="UpdatedOn" label="Updated On" fullWidth disabled />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="UpdatedBy" label="Updated By" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: EmployeeAuditList,
    show: EmployeeAuditShow,
    create: EmployeeAuditCreate,
    edit: EmployeeAuditEdit,
};