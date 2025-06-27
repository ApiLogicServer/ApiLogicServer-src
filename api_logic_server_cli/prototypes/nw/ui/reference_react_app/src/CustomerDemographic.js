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

const CustomerDemographicFilter = (props) => (
  <div {...props}>
    <TextInput label="Search by ID" source="Id" alwaysOn />
  </div>
);

// CustomerDemographic List
export const CustomerDemographicList = (props) => {
  return (
    <List filters={<CustomerDemographicFilter />} {...props} sort={{ field: 'Id', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} />}> 
      <Datagrid rowClick="show">
        <TextField source="Id" label="ID" />
        <TextField source="CustomerDesc" label="Customer Description" />
      </Datagrid>
    </List>
  );
};

// CustomerDemographic Show
export const CustomerDemographicShow = (props) => {
  return (
    <Show {...props}>
      <SimpleShowLayout>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Customer Demographic Information
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Labeled label="ID">
                <TextField source="Id" />
              </Labeled>
            </Grid>
            <Grid item xs={12}>
              <Labeled label="Customer Description">
                <TextField source="CustomerDesc" />
              </Labeled>
            </Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
        </Box>
      </SimpleShowLayout>
    </Show>
  );
};

// CustomerDemographic Create
export const CustomerDemographicCreate = (props) => {
  return (
    <Create {...props}>
      <SimpleForm>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Create New Customer Demographic
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <TextInput source="Id" label="ID" fullWidth validate={required()} />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={8}>
              <Box sx={{ p: 1 }}>
                <TextInput source="CustomerDesc" label="Customer Description" fullWidth />
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleForm>
    </Create>
  );
};

// CustomerDemographic Edit
export const CustomerDemographicEdit = (props) => {
  return (
    <Edit {...props}>
      <SimpleForm>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Edit Customer Demographic
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <TextInput source="Id" label="ID" fullWidth disabled />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={8}>
              <Box sx={{ p: 1 }}>
                <TextInput source="CustomerDesc" label="Customer Description" fullWidth />
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleForm>
    </Edit>
  );
};

export default {
  list: CustomerDemographicList,
  show: CustomerDemographicShow,
  create: CustomerDemographicCreate,
  edit: CustomerDemographicEdit,
};