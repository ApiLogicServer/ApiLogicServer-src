import React from 'react';
import {
  List,Pagination,
  Datagrid,
  TextField,
  Show,
  TabbedShowLayout,
  Tab,
  SimpleShowLayout,
  TextInput,
  Create,
  SimpleForm,
  Edit,
  Filter,
  NumberField
} from 'react-admin';

// SampleDBVersion Filter
const SampleDBVersionFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
  </Filter>
);

// SampleDBVersion List
export const SampleDBVersionList = (props) => (
  <List {...props} filters={<SampleDBVersionFilter />}
    perPage={7}
    sort={{ field: 'Id', order: 'ASC' }}
    pagination={<Pagination rowsPerPageOptions={[7, 14, 28]} />}  
  >
    <Datagrid rowClick="show">
      <NumberField source="Id" label="ID" />
      <TextField source="Notes" label="Notes" />
    </Datagrid>
  </List>
);

// SampleDBVersion Show
export const SampleDBVersionShow = (props) => (
  <Show {...props}>
    <TabbedShowLayout>
      <Tab label="Details">
        <SimpleShowLayout>
          <NumberField source="Id" label="ID" />
          <TextField source="Notes" label="Notes" />
        </SimpleShowLayout>
      </Tab>
      {/* Add additional tabs for related resources if applicable */}
    </TabbedShowLayout>
  </Show>
);

// SampleDBVersion Create
export const SampleDBVersionCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="Notes" label="Notes" />
      {/* Add fields as needed */}
    </SimpleForm>
  </Create>
);

// SampleDBVersion Edit
export const SampleDBVersionEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <NumberField source="Id" label="ID" disabled />
      <TextInput source="Notes" label="Notes" />
      {/* Add additional fields or modify existing ones as needed */}
    </SimpleForm>
  </Edit>
);
