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

const SysEmailFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="subject" alwaysOn />
    </Filter>
);

// SysEmail List
export const SysEmailList = (props) => {
    return (
        <List filters={<SysEmailFilter />} {...props} sort={{ field: 'id', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="id" label="Email ID" />
                <ReferenceField label="Customer" source="customer_id" reference="Customer">
                    <TextField source="name" />
                </ReferenceField>
                <TextField source="subject" label="Subject" />
                <DateField source="CreatedOn" label="Created On" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// SysEmail Show
export const SysEmailShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Email Details
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Email ID">
                                    <TextField source="id" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Customer">
                                    <ReferenceField source="customer_id" reference="Customer">
                                        <TextField source="name" />
                                    </ReferenceField>
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Subject">
                                    <TextField source="subject" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12}>
                            <Divider sx={{ my: 2 }} />
                            <Labeled label="Message">
                                <TextField source="message" />
                            </Labeled>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleShowLayout>
        </Show>
    );
};

// SysEmail Create
export const SysEmailCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Email
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="customer_id" reference="Customer" fullWidth>
                                    <SelectInput optionText="name" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="subject" label="Subject" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12}>
                            <Box sx={{ p: 1 }}>
                                <TextInput multiline source="message" label="Message" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// SysEmail Edit
export const SysEmailEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Email
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="customer_id" reference="Customer" fullWidth>
                                    <SelectInput optionText="name" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="subject" label="Subject" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12}>
                            <Box sx={{ p: 1 }}>
                                <TextInput multiline source="message" label="Message" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: SysEmailList,
    show: SysEmailShow,
    create: SysEmailCreate,
    edit: SysEmailEdit,
};