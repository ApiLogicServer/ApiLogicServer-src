```javascript
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
  TextInput, 
  NumberInput, 
  ReferenceInput, 
  SelectInput, 
  Create, 
  SimpleForm, 
  Edit, 
  Filter, 
  DateField, 
  ReferenceManyField, 
  BooleanField, 
  BooleanInput,
  ImageField
} from 'react-admin';

const EmployeeFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
    <TextInput label="Last Name" source="LastName" />
    <ReferenceInput label="Department" source="WorksForDepartmentId" reference="Department" allowEmpty>
      <SelectInput optionText="name" />
    </ReferenceInput>
  </Filter>
);

const EmployeeList = (props) => (
  <List filters={<EmployeeFilter />} {...props}>
    <Datagrid rowClick="show">
      <TextField source="LastName" label="Last Name" />
      <TextField source="FirstName" label="First Name" />
      <TextField source="Title" />
      <TextField source="Email" />
      <NumberField source="Salary" label="Salary" options={{ style: 'currency', currency: 'USD' }} />
      <TextField source="EmployeeType" label="Employee Type" />
      <ImageField source="PhotoPath" label="Photo" />
      <NumberField source="ProperSalary" label="Proper Salary" options={{ style: 'currency', currency: 'USD' }}/>
      <DateField source="HireDate" label="Hire Date" />
    </Datagrid>
  </List>
);

const EmployeeShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="LastName" label="Last Name" />
      <TextField source="FirstName" label="First Name" />
      <TextField source="Title" />
      <TextField source="Email" />
      <NumberField source="Salary" label="Salary" options={{ style: 'currency', currency: 'USD' }} />
      <TextField source="EmployeeType" label="Employee Type" />
      <ImageField source="PhotoPath" label="Photo" />
      <NumberField source="ProperSalary" label="Proper Salary" options={{ style: 'currency', currency: 'USD' }}/>
      <DateField source="HireDate" label="Hire Date" />
      <TextField source="Notes" label="Notes" />
    </SimpleShowLayout>
    <TabbedShowLayout>
      <Tab label="Audits">
        <ReferenceManyField reference="EmployeeAudit" target="EmployeeId" label="Employee Audits">
          <Datagrid>
            <TextField source="Title" />
            <TextField source="CreatedOn" label="Created On" />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
      <Tab label="Territories">
        <ReferenceManyField reference="EmployeeTerritory" target="EmployeeId" label="Territories">
          <Datagrid>
            <ReferenceField label="Territory Description" source="TerritoryId" reference="Territory">
              <TextField source="TerritoryDescription" />
            </ReferenceField>
          </Datagrid>
        </ReferenceManyField>
      </Tab>
      <Tab label="Orders">
        <ReferenceManyField reference="Order" target="EmployeeId" label="Orders">
          <Datagrid>
            <TextField source="ShipName" />
            <DateField source="OrderDate" />
            <NumberField source="AmountTotal" options={{ style: 'currency', currency: 'USD' }} />
          </Datagrid>
        </ReferenceManyField>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

const EmployeeEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="LastName" label="Last Name" />
      <TextInput source="FirstName" label="First Name" />
      <TextInput source="Title" />
      <TextInput source="Email" />
      <NumberInput source="Salary" label="Salary" />
      <SelectInput source="EmployeeType" choices={[
        { id: 'Salaried', name: 'Salaried' },
        { id: 'Hourly', name: 'Hourly' }
      ]} />
      <ImageField source="PhotoPath" label="Photo" />
      <DateField source="HireDate" label="Hire Date" />
      <TextInput multiline source="Notes" label="Notes" />
      <ReferenceInput label="On Loan Department" source="OnLoanDepartmentId" reference="Department">
        <SelectInput optionText="DepartmentName" />
      </ReferenceInput>
      <ReferenceInput label="Works For Department" source="WorksForDepartmentId" reference="Department">
        <SelectInput optionText="DepartmentName" />
      </ReferenceInput>
    </SimpleForm>
  </Edit>
);

const EmployeeCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="LastName" label="Last Name*" />
      <TextInput source="FirstName" label="First Name" />
      <TextInput source="Title" />
      <TextInput source="Email" />
      <NumberInput source="Salary" label="Salary" />
      <SelectInput source="EmployeeType" choices={[
        { id: 'Salaried', name: 'Salaried' },
        { id: 'Hourly', name: 'Hourly' }
      ]} />
      <DateField source="HireDate" label="Hire Date" />
      <TextInput multiline source="Notes" label="Notes" />
      <ReferenceInput label="On Loan Department" source="OnLoanDepartmentId" reference="Department">
        <SelectInput optionText="DepartmentName" />
      </ReferenceInput>
      <ReferenceInput label="Works For Department" source="WorksForDepartmentId" reference="Department">
        <SelectInput optionText="DepartmentName" />
      </ReferenceInput>
    </SimpleForm>
  </Create>
);

export { EmployeeList, EmployeeShow, EmployeeEdit, EmployeeCreate };
```