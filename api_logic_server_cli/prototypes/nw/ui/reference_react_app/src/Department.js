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

export const DepartmentList = (props) => (
    <List {...props} sort={{ field: 'DepartmentName', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
        <Datagrid rowClick="show">
            <TextField source="DepartmentName" label="Department Name" />
            <NumberField source="SecurityLevel" label="Security Level" />
        </Datagrid>
    </List>
);

// Department Show
export const DepartmentShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Department Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Department Name">
                                <TextField source="DepartmentName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Security Level">
                                <NumberField source="SecurityLevel" />
                            </Labeled>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Employee List">
                <ReferenceManyField reference="Employee" target="OnLoanDepartmentId" addLabel={false} pagination={<Pagination />}>
                    <Datagrid rowClick="show">
                        <TextField source="LastName" label="Last Name" />
                        <TextField source="FirstName" label="First Name" />
                        <DateField source="HireDate" label="Hire Date" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
                <AddEmployeeButton />
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Custom Add Employee Button
const AddEmployeeButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Employee/create?source=${encodeURIComponent(JSON.stringify({ OnLoanDepartmentId: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add New Employee
        </Button>
    );
};

// Department Create
export const DepartmentCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Department
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="DepartmentName" label="Department Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="SecurityLevel" label="Security Level" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Create>
);

// Department Edit
export const DepartmentEdit = (props) => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Department
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="DepartmentName" label="Department Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="SecurityLevel" label="Security Level" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Edit>
);

export default {
    list: DepartmentList,
    show: DepartmentShow,
    create: DepartmentCreate,
    edit: DepartmentEdit,
};