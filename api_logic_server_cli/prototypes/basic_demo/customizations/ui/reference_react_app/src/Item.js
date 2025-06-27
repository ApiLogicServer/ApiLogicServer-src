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

const ItemFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search ID" source="id" alwaysOn />
  </Filter>
);

// Item List
export const ItemList = (props) => {
  return (
    <List filters={<ItemFilter />} {...props} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
      <Datagrid rowClick="show">
        <TextField source="id" label="ID" />
        <ReferenceField source="order_id" reference="Order" label="Order">
          <TextField source="id" />
        </ReferenceField>
        <ReferenceField source="product_id" reference="Product" label="Product">
          <TextField source="name" />
        </ReferenceField>
        <NumberField source="quantity" label="Quantity" />
        <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
        <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
        <EditButton />
        <DeleteButton />
      </Datagrid>
    </List>
  );
};

// Item Create
export const ItemCreate = (props) => {
  return (
    <Create {...props}>
      <SimpleForm>
        <ReferenceInput source="order_id" reference="Order" fullWidth>
          <SelectInput optionText="id" validate={required()} />
        </ReferenceInput>
        <ReferenceInput source="product_id" reference="Product" fullWidth>
          <SelectInput optionText="name" validate={required()} />
        </ReferenceInput>
        <NumberInput source="quantity" label="Quantity" fullWidth validate={required()} />
        <NumberInput source="amount" label="Amount" fullWidth />
        <NumberInput source="unit_price" label="Unit Price" fullWidth />
      </SimpleForm>
    </Create>
  );
};

// Item Edit
export const ItemEdit = (props) => {
  return (
    <Edit {...props} redirect={false}>
      <SimpleForm>
        <ReferenceInput source="order_id" reference="Order" fullWidth>
          <SelectInput optionText="id" validate={required()} />
        </ReferenceInput>
        <ReferenceInput source="product_id" reference="Product" fullWidth>
          <SelectInput optionText="name" validate={required()} />
        </ReferenceInput>
        <NumberInput source="quantity" label="Quantity" fullWidth validate={required()} />
        <NumberInput source="amount" label="Amount" fullWidth />
        <NumberInput source="unit_price" label="Unit Price" fullWidth />
      </SimpleForm>
    </Edit>
  );
};

// Item Show
export const ItemShow = (props) => {
  return (
    <Show {...props}>
      <SimpleShowLayout>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Item Details
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="ID">
                  <TextField source="id" />
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Order">
                  <ReferenceField source="order_id" reference="Order">
                    <TextField source="id" />
                  </ReferenceField>
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Product">
                  <ReferenceField source="product_id" reference="Product">
                    <TextField source="name" />
                  </ReferenceField>
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Quantity">
                  <NumberField source="quantity" />
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Amount">
                  <NumberField source="amount" options={{ style: 'currency', currency: 'USD' }} />
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Unit Price">
                  <NumberField source="unit_price" options={{ style: 'currency', currency: 'USD' }} />
                </Labeled>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleShowLayout>
      <TabbedShowLayout>
        <Tab label="Order Details">
          <ReferenceField source="order_id" reference="Order" fullWidth>
            <SimpleShowLayout>
              <TextField source="id" label="Order ID" />
              <TextField source="notes" label="Notes" />
              <DateField source="CreatedOn" label="Created On" />
              <NumberField source="amount_total" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
              <DateField source="date_shipped" label="Date Shipped" />
            </SimpleShowLayout>
          </ReferenceField>
        </Tab>
        <Tab label="Product Details">
          <ReferenceField source="product_id" reference="Product" fullWidth>
            <SimpleShowLayout>
              <TextField source="name" label="Product Name" />
              <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
            </SimpleShowLayout>
          </ReferenceField>
        </Tab>
      </TabbedShowLayout>
    </Show>
  );
};

export default {
  list: ItemList,
  show: ItemShow,
  create: ItemCreate,
  edit: ItemEdit,
};
 