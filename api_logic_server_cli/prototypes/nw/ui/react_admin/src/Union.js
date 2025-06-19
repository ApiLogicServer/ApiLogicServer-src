import React from 'react';
import { List, Datagrid, TextField, NumberField, Show, SimpleShowLayout, ReferenceManyField, TabbedShowLayout, Tab, TextInput, Create, SimpleForm, Edit, ReferenceField, ReferenceInput, SelectInput, Filter, Pagination } from 'react-admin';

// Filter component to be used in List view
const UnionFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by Name" source="q" alwaysOn />
  </Filter>
);

// List view for Unions
export const UnionList = (props) => (
  <List {...props} filters={<UnionFilter />} pagination={<Pagination rowsPerPageOptions={[7, 14, 28]} />} perPage={7}>
    <Datagrid rowClick="show">
      <TextField source="Name" label="Union Name" />
      <NumberField source="Id" label="Union ID" />
    </Datagrid>
  </List>
);

// Show view for a Union
export const UnionShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="Name" label="Union Name" />
      <NumberField source="Id" label="Union ID" />
      <TabbedShowLayout>
        <Tab label="Employees">
          <ReferenceManyField reference="Employee" target="UnionId" addLabel={false}>
            <Datagrid>
              <TextField source="LastName" />
              <TextField source="FirstName" />
              <ReferenceField source="WorksForDepartmentId" reference="Department">
                <TextField source="DepartmentName" />
              </ReferenceField>
            </Datagrid>
          </ReferenceManyField>
        </Tab>
      </TabbedShowLayout>
    </SimpleShowLayout>
  </Show>
);

// Create view for a new Union
export const UnionCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="Name" label="Union Name" />
    </SimpleForm>
  </Create>
);

// Edit view for an existing Union
export const UnionEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="Name" label="Union Name" />
      <NumberField source="Id" label="Union ID" />
    </SimpleForm>
  </Edit>
);