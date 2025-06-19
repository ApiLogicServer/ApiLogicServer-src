import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    DateField,
    ReferenceField,
    Show,
    TabbedShowLayout,
    Tab,
    SimpleShowLayout,
    Filter,
    TextInput,
    Create,
    SimpleForm,
    Edit,
    NumberField,
    DateTimeInput,
    ReferenceInput,
    SelectInput,
    NumberInput
} from 'react-admin';

// Filters for EmployeeAudit List
const EmployeeAuditFilter = props => (
    <Filter {...props}>
        <TextInput label="Search by Last Name" source="LastName" alwaysOn />
        <ReferenceInput label="Employee" source="EmployeeId" reference="Employee" allowEmpty>
            <SelectInput optionText="LastName" />
        </ReferenceInput>
    </Filter>
);

// EmployeeAudit List Component
export const EmployeeAuditList = props => (
    <List filters={<EmployeeAuditFilter />} {...props} perPage={7} sort={{ field: 'LastName', order: 'ASC' }}>
        <Datagrid rowClick="show">
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <TextField source="Title" />
            <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} />
            <DateField source="CreatedOn" label="Created On" />
            <ReferenceField label="Employee" source="EmployeeId" reference="Employee">
                <TextField source="LastName" />
            </ReferenceField>
        </Datagrid>
    </List>
);

// EmployeeAudit Show Component
export const EmployeeAuditShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="LastName" label="Last Name" />
            <TextField source="FirstName" label="First Name" />
            <TextField source="Title" />
            <NumberField source="Salary" options={{ style: 'currency', currency: 'USD' }} label="Salary" />
            <DateField source="CreatedOn" label="Created On" />
            <DateField source="UpdatedOn" label="Updated On" />
            <TextField source="CreatedBy" label="Created By" />
            <TextField source="UpdatedBy" label="Updated By" />

            <TabbedShowLayout>
                <Tab label="Related Employee">
                    <ReferenceField label="Employee" source="EmployeeId" reference="Employee">
                        <TextField source="LastName" />
                    </ReferenceField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

// EmployeeAudit Create Component
export const EmployeeAuditCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="LastName" label="Last Name" />
            <TextInput source="FirstName" label="First Name" />
            <TextInput source="Title" />
            <NumberInput source="Salary" label="Salary" />
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
        </SimpleForm>
    </Create>
);

// EmployeeAudit Edit Component
export const EmployeeAuditEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="LastName" label="Last Name" />
            <TextInput source="FirstName" label="First Name" />
            <TextInput source="Title" />
            <NumberInput source="Salary" label="Salary" />
            <DateTimeInput source="CreatedOn" label="Created On" />
            <DateTimeInput source="UpdatedOn" label="Updated On" />
            <TextInput source="CreatedBy" label="Created By" />
            <TextInput source="UpdatedBy" label="Updated By" />
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);