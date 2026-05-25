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

const SysMcpFilter = (props) => (
    <TextInput label="Search" source="id" alwaysOn />
);

// SysMcp List
export const SysMcpList = (props) => {
    return (
        <List filters={<SysMcpFilter />} {...props} sort={{ field: 'id', order: 'ASC' }}>
            <Datagrid rowClick="show">
                <TextField source="id" label="ID" />
                <TextField source="request" label="Request" />
            </Datagrid>
        </List>
    );
};

// SysMcp Show
export const SysMcpShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        SysMcp Details
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="ID">
                                    <TextField source="id" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={8}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Request">
                                    <TextField source="request" />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleShowLayout>
        </Show>
    );
};

// SysMcp Create
export const SysMcpCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create SysMcp
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={12} md={12}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="request" label="Request" multiline fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// SysMcp Edit
export const SysMcpEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit SysMcp
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={12} md={12}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="request" label="Request" multiline fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: SysMcpList,
    show: SysMcpShow,
    create: SysMcpCreate,
    edit: SysMcpEdit,
};