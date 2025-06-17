import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  EditButton,
  ShowButton,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  Show,
  Create,
  Edit,
  SimpleForm,
  TextInput,
  ReferenceManyField,
  ReferenceInput,
  SelectInput,
  required,
  Filter,
  Pagination,
} from 'react-admin';
import { Box } from '@mui/material';

const LocationFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
    <TextInput label="Country" source="country" defaultValue="" />
  </Filter>
);

export const LocationList = props => (
  <List filters={<LocationFilter />} pagination={<Pagination rowsPerPageOptions={[5, 10, 25, 50]} />} {...props}>
    <Datagrid rowClick="show">
      <TextField source="country" label="Country" sortable={true} />
      <TextField source="city" label="City" />
      <TextField source="notes" label="Notes" />
      <EditButton />
      <ShowButton />
    </Datagrid>
  </List>
);

export const LocationShow = props => (
  <Show {...props}>
    <TabbedShowLayout>
      <Tab label="Details">
        <SimpleShowLayout>
          <TextField source="country" label="Country" />
          <TextField source="city" label="City" />
          <TextField source="notes" label="Notes" />
        </SimpleShowLayout>
      </Tab>
      <Tab label="Orders">
        <ReferenceManyField
          reference="Order"
          target="Location"
          label="Orders in this Location"
          pagination={<Pagination rowsPerPageOptions={[5, 10, 25, 50]} />}
        >
          <Datagrid>
            <TextField source="id" label="Order ID" />
            <TextField source="shipName" label="Ship Name" />
            <TextField source="orderDate" label="Order Date" />
            <ShowButton />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

export const LocationCreate = props => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="country" label="Country" validate={required()} />
      <TextInput source="city" label="City" validate={required()} />
      <TextInput source="notes" label="Notes" />
    </SimpleForm>
  </Create>
);

export const LocationEdit = props => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="country" label="Country" validate={required()} />
      <TextInput source="city" label="City" validate={required()} />
      <TextInput source="notes" label="Notes" />
    </SimpleForm>
  </Edit>
);
