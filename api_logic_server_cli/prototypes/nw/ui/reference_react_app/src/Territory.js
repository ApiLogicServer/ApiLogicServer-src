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

// Filter for Territory List
const TerritoryFilter = props => (
    <Filter {...props}>
        <TextInput label="Search by Description" source="TerritoryDescription" alwaysOn />
    </Filter>
);

// Territory List
export const TerritoryList = props => (
    <List filters={<TerritoryFilter />} {...props} sort={{ field: 'TerritoryDescription', order: 'ASC' }}>
        <Datagrid rowClick="show">
            <TextField source="TerritoryDescription" label="Territory Description" />
            <TextField source="Id" label="ID" />
            <TextField source="RegionId" label="Region ID" />
        </Datagrid>
    </List>
);

// Territory Show
export const TerritoryShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Territory Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextField source="TerritoryDescription" label="Territory Description" />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextField source="Id" label="ID" />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextField source="RegionId" label="Region ID" />
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
            <TabbedShowLayout>
                <Tab label="Employee Territories">
                    <ReferenceManyField 
                        reference="EmployeeTerritory" 
                        target="TerritoryId" 
                        addLabel={false} 
                        pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="ID" />
                            <TextField source="EmployeeId" label="Employee ID" />
                        </Datagrid>
                    </ReferenceManyField>
                    <AddEmployeeTerritoryButton />
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

// Custom Add Employee Territory Button
const AddEmployeeTerritoryButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();

    const handleClick = () => {
        redirect(`/EmployeeTerritory/create?source=${encodeURIComponent(JSON.stringify({ TerritoryId: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add Employee Territory
        </Button>
    );
};

// Territory Create
export const TerritoryCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Territory
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="TerritoryDescription" label="Territory Description" validate={required()} fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <ReferenceInput source="RegionId" reference="Region" fullWidth>
                            <SelectInput optionText="RegionDescription" validate={required()} />
                        </ReferenceInput>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Create>
);

// Territory Edit
export const TerritoryEdit = props => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Territory
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <TextInput source="TerritoryDescription" label="Territory Description" validate={required()} fullWidth />
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <ReferenceInput source="RegionId" reference="Region" fullWidth>
                            <SelectInput optionText="RegionDescription" validate={required()} />
                        </ReferenceInput>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Edit>
);

export default {
    list: TerritoryList,
    show: TerritoryShow,
    create: TerritoryCreate,
    edit: TerritoryEdit,
};