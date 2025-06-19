import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  NumberField,
  ReferenceField,
  Show,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  ReferenceManyField,
  Edit,
  SimpleForm,
  TextInput,
  NumberInput,
  ReferenceInput,
  Create,
  SelectInput, Pagination
} from 'react-admin';

export const DepartmentList = (props) => (
  <List {...props} filters={<DepartmentFilter />} pagination={<DepartmentPagination />}>
    <Datagrid rowClick="show">
      <TextField source="DepartmentName" label="Department Name" />
      <NumberField source="SecurityLevel" label="Security Level" />
      <NumberField source="Id" label="ID" />
    </Datagrid>
  </List>
);

export const DepartmentShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="DepartmentName" label="Department Name" />
      <NumberField source="SecurityLevel" label="Security Level" />
      <NumberField source="Id" label="ID" />
    </SimpleShowLayout>
    <TabbedShowLayout>
      <Tab label="Departments">
        <ReferenceManyField reference="Department" target="DepartmentId" label="" perPage={5} sort={{ field: 'Id', order: 'ASC' }}>
          <Datagrid>
            <ReferenceField source="DepartmentId" reference="Department"><TextField source="DepartmentName" /></ReferenceField>
            <NumberField source="SecurityLevel" label="Security Level" />
            <NumberField source="Id" label="ID" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
      <Tab label="On Loan Employees">
        <ReferenceManyField reference="Employee" target="OnLoanDepartmentId" label="" perPage={5} sort={{ field: 'Id', order: 'ASC' }}>
          <Datagrid>
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <NumberField source="Id" label="Employee ID" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
      <Tab label="Works For Employees">
        <ReferenceManyField reference="Employee" target="WorksForDepartmentId" label="" perPage={5} sort={{ field: 'Id', order: 'ASC' }}>
          <Datagrid>
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <NumberField source="Id" label="Employee ID" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

export const DepartmentCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="DepartmentName" label="Department Name" />
      <NumberInput source="SecurityLevel" label="Security Level" />
    </SimpleForm>
  </Create>
);

export const DepartmentEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="DepartmentName" label="Department Name" />
      <NumberInput source="SecurityLevel" label="Security Level" />
      <NumberInput source="Id" label="ID" />
    </SimpleForm>
  </Edit>
);

const DepartmentFilter = (props) => (
  <div>
    <TextInput label="Search By Name" source="DepartmentName" alwaysOn {...props} />
  </div>
);

const DepartmentPagination = () => (
  <Pagination rowsPerPageOptions={[5, 10, 25]} />
);
