// src/Territory.js
import React from 'react';
import {
    List,
    Show,SelectInput,
    Datagrid,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    TextField,
    ReferenceField,
    FunctionField,
    TextInput,
    ReferenceInput,
    Create,
    Edit,
    SimpleForm,
    Filter,
    NumberField,
    BooleanField,
    ReferenceManyField,
} from 'react-admin';

// Filter component for the Territory list view
const TerritoryFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Description" source="q" alwaysOn />
    </Filter>
);

// TerritoryList component for displaying a list of territories
export const TerritoryList = (props) => (
    <List {...props} filters={<TerritoryFilter />}>
        <Datagrid rowClick="show">
            <TextField source="TerritoryDescription" label="Territory Description" />
            <TextField source="Id" label="ID" />
            <ReferenceField label="Region" source="RegionId" reference="Region">
                <TextField source="RegionDescription" />
            </ReferenceField>
        </Datagrid>
    </List>
);

// TerritoryShow component for displaying territory details
export const TerritoryShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="TerritoryDescription" label="Territory Description" />
            <TextField source="Id" label="ID" />
            <ReferenceField label="Region" source="RegionId" reference="Region">
                <TextField source="RegionDescription" />
            </ReferenceField>
            <ReferenceManyField
                label="Employees in Territory"
                reference="EmployeeTerritory"
                target="TerritoryId"
            >
                <Datagrid rowClick="show">
                    <ReferenceField label="Employee" source="EmployeeId" reference="Employee">
                        <FunctionField render={(record) => `${record.FirstName} ${record.LastName}`} />
                    </ReferenceField>
                </Datagrid>
            </ReferenceManyField>
        </SimpleShowLayout>
    </Show>
);

// TerritoryCreate component for creating new territories
export const TerritoryCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="TerritoryDescription" label="Territory Description" />
            <ReferenceInput label="Region" source="RegionId" reference="Region">
                <SelectInput optionText="RegionDescription" />
            </ReferenceInput>
        </SimpleForm>
    </Create>
);

// TerritoryEdit component for editing existing territories
export const TerritoryEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="TerritoryDescription" label="Territory Description" />
            <ReferenceInput label="Region" source="RegionId" reference="Region">
                <SelectInput optionText="RegionDescription" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);
