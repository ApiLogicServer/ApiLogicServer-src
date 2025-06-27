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

const EmployeeFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="LastName" alwaysOn />
    </Filter>
);

// Employee List
export const EmployeeList = (props) => {
    return (
        <List filters={<EmployeeFilter />} {...props} sort={{ field: 'LastName', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="LastName" label="Last Name" />
                <TextField source="FirstName" label="First Name" />
                <EmailField source="Email" label="Email" />
                <NumberField source="Salary" label="Salary" options={{ style: 'currency', currency: 'USD'}} />
                <ReferenceField source="WorksForDepartmentId" reference="Department" label="Department">
                    <TextField source="DepartmentName" />
                </ReferenceField>
                <EditButton />
                <DeleteButton />
                <ShowButton />
            </Datagrid>
        </List>
    );
};

// Employee Show
export const EmployeeShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Employee Information
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
                                <Labeled label="Salary">
                                    <NumberField source="Salary" options={{ style: 'currency', currency: 'USD'}} />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Email">
                                    <EmailField source="Email" />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                    <Divider sx={{ my: 2 }} />
                </Box>
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Audit Logs">
                    <ReferenceManyField reference="EmployeeAudit" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="Audit ID" />
                            <TextField source="LastName" label="Last Name" />
                            <TextField source="FirstName" label="First Name" />
                            <DateField source="CreatedOn" label="Created On" />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                <Tab label="Territories">
                    <ReferenceManyField reference="EmployeeTerritory" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <NumberField source="TerritoryId" label="Territory ID" />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                <Tab label="Order History">
                    <ReferenceManyField reference="Order" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="Order ID" />
                            <DateField source="OrderDate" label="Order Date" />
                            <NumberField source="AmountTotal" label="Total Amount" options={{ style: 'currency', currency: 'USD'}} />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </Show>
    );
};

// Employee Create
export const EmployeeCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Employee
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Email" label="Email" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="WorksForDepartmentId" reference="Department" fullWidth>
                                    <SelectInput optionText="DepartmentName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Employee Edit
export const EmployeeEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Employee
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Email" label="Email" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="WorksForDepartmentId" reference="Department" fullWidth>
                                    <SelectInput optionText="DepartmentName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: EmployeeList,
    show: EmployeeShow,
    create: EmployeeCreate,
    edit: EmployeeEdit,
};