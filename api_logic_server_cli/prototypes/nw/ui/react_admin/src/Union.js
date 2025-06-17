// Union.js - React Admin resource definitions and components for the Union entity.
import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  NumberField,
  Show,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  TextInput,
  Create,
  SimpleForm,
  Edit,
  ReferenceManyField,
  EditButton,
  ShowButton,
  Pagination,
  Filter,
} from 'react-admin';

const UnionFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by Name" source="Name" alwaysOn />
  </Filter>
);

export const UnionList = (props) => (
  <List
    {...props}
    filters={<UnionFilter />}
    pagination={<Pagination rowsPerPageOptions={[10, 25, 50]} />}
    sort={{ field: 'Name', order: 'ASC' }}
  >
    <Datagrid rowClick="show">
      <TextField source="Name" label="Union Name" />
      <NumberField source="Id" label="ID" />
      <ShowButton />
    </Datagrid>
  </List>
);

export const UnionShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="Name" label="Union Name" />
      <TabbedShowLayout>
        <Tab label="Members">
          <ReferenceManyField reference="Employee" target="UnionId" label="Union Employees">
            <Datagrid>
              <TextField source="LastName" label="Last Name" />
              <TextField source="FirstName" label="First Name" />
              <ShowButton />
            </Datagrid>
          </ReferenceManyField>
        </Tab>
      </TabbedShowLayout>
    </SimpleShowLayout>
  </Show>
);

export const UnionCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="Name" label="Union Name" />
    </SimpleForm>
  </Create>
);

export const UnionEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="Name" label="Union Name" />
    </SimpleForm>
  </Edit>
);