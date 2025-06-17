```jsx
import React from 'react';
import {
  List, FunctionField, Datagrid, TextField, DateField, NumberField,
  ReferenceField, ReferenceManyField, Show, TabbedShowLayout, Tab,
  SimpleShowLayout, TextInput, NumberInput, DateTimeInput, ReferenceInput,
  SelectInput, Create, SimpleForm, Edit, Filter, Pagination, BooleanField, BooleanInput
} from 'react-admin';

// EmployeeAudit List Component
export const EmployeeAuditList = (props) => (
  <List {...props} filters={<EmployeeAuditFilter />} perPage={7} pagination={<Pagination />}>
    <Datagrid rowClick="show">
      <TextField source="LastName" label="Last Name" />
      <TextField source="Title" />
      <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
      <TextField source="CreatedBy" />
      <DateField source="CreatedOn" showTime />
      <TextField source="UpdatedBy" />
      <DateField source="UpdatedOn" showTime />
    </Datagrid>
  </List>
);

// EmployeeAudit Show Component
export const EmployeeAuditShow = (props) => (
  <Show {...props}>
    <TabbedShowLayout>
      <Tab label="Summary">
        <SimpleShowLayout>
          <TextField source="LastName" label="Last Name" />
          <TextField source="Title" />
          <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
          <TextField source="FirstName" />
          <TextField source="CreatedBy" />
          <DateField source="CreatedOn" showTime />
          <TextField source="UpdatedBy" />
          <DateField source="UpdatedOn" showTime />
        </SimpleShowLayout>
      </Tab>
      <Tab label="Employee">
        <ReferenceManyField reference="Employee" target="EmployeeId" addLabel={false}>
          <Datagrid rowClick="show">
            <TextField source="LastName" />
            <TextField source="FirstName" />
            <TextField source="Title" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

// EmployeeAudit Filter Component (used in EmployeeAuditList)
const EmployeeAuditFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by Last Name" source="LastName" alwaysOn />
    <TextInput label="Title" source="Title" />
    <DateTimeInput label="Creation Date" source="CreatedOn" />
  </Filter>
);

// EmployeeAudit Create Component
export const EmployeeAuditCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="LastName" label="Last Name" />
      <TextInput source="Title" />
      <NumberInput source="Salary" label="Salary" />
      <TextInput source="FirstName" />
      <TextInput source="CreatedBy" />
      <DateTimeInput source="CreatedOn" />
      <TextInput source="UpdatedBy" />
      <DateTimeInput source="UpdatedOn" />
    </SimpleForm>
  </Create>
);

// EmployeeAudit Edit Component
export const EmployeeAuditEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="LastName" label="Last Name" />
      <TextInput source="Title" />
      <NumberInput source="Salary" label="Salary" />
      <TextInput source="FirstName" />
      <TextInput source="CreatedBy" />
      <DateTimeInput source="CreatedOn" />
      <TextInput source="UpdatedBy" />
      <DateTimeInput source="UpdatedOn" />
    </SimpleForm>
  </Edit>
);
```