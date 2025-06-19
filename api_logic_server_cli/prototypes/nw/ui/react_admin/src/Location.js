import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  ReferenceManyField,
  Show,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  createFilter,
  Create,
  Edit,
  SimpleForm,
  TextInput,
} from 'react-admin';

// List Component for Location
export const LocationList = () => (
  <List
    filters={<LocationFilter />}
    perPage={7}
    title="Location List"
  >
    <Datagrid rowClick="show">
      <TextField source="country" label="Country" />
      <TextField source="city" label="City" />
      <TextField source="notes" label="Notes" />
    </Datagrid>
  </List>
);

// Filter Component for Location
const LocationFilter = () => (
  <createFilter>
    <TextInput label="Country" source="country" alwaysOn />
    <TextInput label="City" source="city" />
  </createFilter>
);

// Show Component for Location
export const LocationShow = (props) => (
  <Show {...props} title="Location Details">
    <SimpleShowLayout>
      <TextField source="country" label="Country" />
      <TextField source="city" label="City" />
      <TextField source="notes" label="Notes" />
    </SimpleShowLayout>
    <TabbedShowLayout>
      <Tab label="Order List">
        <ReferenceManyField
          reference="Order"
          target="City"
          source="City"
          label="Orders in City"
        >
          <Datagrid rowClick="show">
            <TextField source="ShipName" label="Ship Name" />
            <TextField source="OrderDate" label="Order Date" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

// Create Component for Location
export const LocationCreate = (props) => (
  <Create {...props} title="Create a Location">
    <SimpleForm>
      <TextInput source="country" label="Country" />
      <TextInput source="city" label="City" />
      <TextInput source="notes" label="Notes" />
    </SimpleForm>
  </Create>
);

// Edit Component for Location
export const LocationEdit = (props) => (
  <Edit {...props} title="Edit Location">
    <SimpleForm>
      <TextInput source="country" label="Country" />
      <TextInput source="city" label="City" />
      <TextInput source="notes" label="Notes" />
    </SimpleForm>
  </Edit>
);