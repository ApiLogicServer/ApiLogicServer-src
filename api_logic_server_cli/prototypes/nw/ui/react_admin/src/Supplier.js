// Supplier.js

import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  ReferenceField,
  Show,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  Edit,
  Create,
  SimpleForm,
  TextInput,
  NumberInput,
  SelectInput,
  ReferenceInput,
  Filter,
  Pagination,
} from 'react-admin';

// Filters for the Supplier List
const SupplierFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
    <TextInput label="Search by Contact Name" source="ContactName" />
    <TextInput label="Search by City" source="City" />
  </Filter>
);

// Supplier List Component
export const SupplierList = (props) => (
  <List filters={<SupplierFilter />} pagination={<Pagination />} {...props}>
    <Datagrid rowClick="show">
      <TextField source="CompanyName" label="Company Name" />
      <TextField source="ContactName" label="Contact Name" />
      <TextField source="ContactTitle" label="Contact Title" />
      <TextField source="Address" label="Address" />
      <TextField source="City" label="City" />
      <TextField source="Country" label="Country" />
      <TextField source="Phone" label="Phone" />
    </Datagrid>
  </List>
);

// Supplier Show Component
export const SupplierShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="CompanyName" label="Company Name" />
      <TextField source="ContactName" label="Contact Name" />
      <TextField source="ContactTitle" label="Contact Title" />
      <TextField source="Address" label="Address" />
      <TextField source="City" label="City" />
      <TextField source="Region" label="Region" />
      <TextField source="PostalCode" label="Postal Code" />
      <TextField source="Country" label="Country" />
      <TextField source="Phone" label="Phone" />
      <TextField source="Fax" label="Fax" />
      <TextField source="HomePage" label="Home Page" />
    </SimpleShowLayout>
  </Show>
);

// Supplier Create Component
export const SupplierCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="CompanyName" label="Company Name" />
      <TextInput source="ContactName" label="Contact Name" />
      <TextInput source="ContactTitle" label="Contact Title" />
      <TextInput source="Address" label="Address" />
      <TextInput source="City" label="City" />
      <TextInput source="Region" label="Region" />
      <TextInput source="PostalCode" label="Postal Code" />
      <TextInput source="Country" label="Country" />
      <TextInput source="Phone" label="Phone" />
      <TextInput source="Fax" label="Fax" />
      <TextInput source="HomePage" label="Home Page" />
    </SimpleForm>
  </Create>
);

// Supplier Edit Component
export const SupplierEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="CompanyName" label="Company Name" />
      <TextInput source="ContactName" label="Contact Name" />
      <TextInput source="ContactTitle" label="Contact Title" />
      <TextInput source="Address" label="Address" />
      <TextInput source="City" label="City" />
      <TextInput source="Region" label="Region" />
      <TextInput source="PostalCode" label="Postal Code" />
      <TextInput source="Country" label="Country" />
      <TextInput source="Phone" label="Phone" />
      <TextInput source="Fax" label="Fax" />
      <TextInput source="HomePage" label="Home Page" />
    </SimpleForm>
  </Edit>
);
