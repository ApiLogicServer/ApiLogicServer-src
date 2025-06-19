import React from 'react';
import {
    List, Show, Edit, Create, Datagrid, TextField, NumberField, DateField,
    SimpleShowLayout, TabbedShowLayout, Tab, SimpleForm, TextInput, NumberInput, DateTimeInput,
    ReferenceField, ReferenceManyField, ReferenceInput, SelectInput, BooleanField, BooleanInput, 
    FunctionField, Pagination, Filter
} from 'react-admin';

// Filter for Employee
const EmployeeFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Last Name" source="LastName" alwaysOn />
        <TextInput label="First Name" source="FirstName" />
        <ReferenceInput label="Department" source="WorksForDepartmentId" reference="Department">
            <SelectInput optionText="DepartmentName" />
        </ReferenceInput>
    </Filter>
);

// Employee List
export const EmployeeList = (props) => (
    <List {...props} filters={<EmployeeFilter />} pagination={<Pagination rowsPerPageOptions={[7, 14, 28]} />} perPage={7}>
        <Datagrid rowClick="show">
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <TextField source="Title" />
            <DateField source="BirthDate" label="Birth Date" />
            <TextField source="City" />
            <ReferenceField label="Department" source="WorksForDepartmentId" reference="Department">
                <TextField source="DepartmentName" />
            </ReferenceField>
            <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="Id" />  {/* Showing primary key at the end */}
        </Datagrid>
    </List>
);

// Employee Show
export const EmployeeShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <TextField source="Title" />
            <DateField source="BirthDate" label="Birth Date" />
            <TextField source="City" />
            <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="Id" /> // Primary Key field
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Audit">
                <ReferenceManyField reference="EmployeeAudit" target="EmployeeId" addLabel={false}>
                    <Datagrid rowClick="show">
                        <TextField source="LastName" />
                        <TextField source="Title" />
                        <DateField source="CreatedOn" label="Created On" />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
            <Tab label="Territories">
                <ReferenceManyField reference="EmployeeTerritory" target="EmployeeId" addLabel={false}>
                    <Datagrid rowClick="show">
                        <TextField source="TerritoryDescription" label="Description" />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Employee Create
export const EmployeeCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="LastName" />
            <TextInput source="FirstName" />
            <TextInput source="Title" />
            <DateTimeInput source="BirthDate" label="Birth Date" />
            <TextInput source="City" />
            <NumberInput source="Salary" label="Salary" />
        </SimpleForm>
    </Create>
);

// Employee Edit
export const EmployeeEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="LastName" />
            <TextInput source="FirstName" />
            <TextInput source="Title" />
            <DateTimeInput source="BirthDate" label="Birth Date" />
            <TextInput source="City" />
            <NumberInput source="Salary" label="Salary" />
            <ReferenceInput label="Department" source="WorksForDepartmentId" reference="Department">
                <SelectInput optionText="DepartmentName" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);