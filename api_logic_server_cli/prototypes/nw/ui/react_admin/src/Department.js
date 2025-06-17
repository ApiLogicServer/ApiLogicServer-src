import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  NumberField,
  ReferenceField,
  Show,
  TabbedShowLayout,
  Tab,
  SimpleShowLayout,
  TextInput,
  NumberInput,
  ReferenceManyField,
  Create,
  SimpleForm,
  Edit,
  Filter,
} from 'react-admin';

// Define Filters for the List
// FIXEDME - deleted bogus code: detailed;

const DepartmentFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by Department Name" source="DepartmentName" alwaysOn />
    <NumberInput label="Security Level" source="SecurityLevel" />
  </Filter>
);

// List Component
export const DepartmentList = (props) => (
  <List filters={<DepartmentFilter />} {...props}>
    <Datagrid rowClick="show">
      <TextField source="DepartmentName" label="Department Name" />
      <NumberField source="SecurityLevel" label="Security Level" />
    </Datagrid>
  </List>
);

// Show Component
export const DepartmentShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="DepartmentName" label="Department Name" />
      <NumberField source="SecurityLevel" label="Security Level" />
      <TextField source="Id" label="ID" />
    </SimpleShowLayout>
    <TabbedShowLayout>
      <Tab label="On Loan Employees">
        <ReferenceManyField
          reference="Employee"
          target="OnLoanDepartmentId"
          label="On Loan Employees"
        >
          <Datagrid>
            <TextField source="LastName" label="Employee Last Name" />
            <TextField source="FirstName" label="Employee First Name" />
            <TextField source="Title" label="Title" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
      <Tab label="Works For Employees">
        <ReferenceManyField
          reference="Employee"
          target="WorksForDepartmentId"
          label="Works For Employees"
        >
          <Datagrid>
            <TextField source="LastName" label="Employee Last Name" />
            <TextField source="FirstName" label="Employee First Name" />
            <TextField source="Title" label="Title" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

// Create Component
export const DepartmentCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="DepartmentName" label="Department Name" />
      <NumberInput source="SecurityLevel" label="Security Level" />
    </SimpleForm>
  </Create>
);

// Edit Component
export const DepartmentEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="DepartmentName" label="Department Name" />
      <NumberInput source="SecurityLevel" label="Security Level" />
      <NumberInput source="Id" label="ID" disabled />
    </SimpleForm>
  </Edit>
);