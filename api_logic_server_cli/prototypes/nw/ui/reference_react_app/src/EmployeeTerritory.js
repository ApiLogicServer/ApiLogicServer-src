// begin MANDATORY imports (always generated EXACTLY)
import React from 'react';
import { List, FunctionField, Datagrid, TextField, EmailField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button } from '@mui/material';
import { useRecordContext, useRedirect, Link, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
// end mandatory imports

const EmployeeTerritoryFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Id" source="Id" alwaysOn />
    </Filter>
);

// EmployeeTerritory List
export const EmployeeTerritoryList = (props) => {
    return (
        <List filters={<EmployeeTerritoryFilter />} {...props} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="Id" label="Employee Territory Id" />
                {/* Reference Fields to display related resources */}
                <ReferenceField source="EmployeeId" reference="Employee">
                    <TextField source="LastName" />
                </ReferenceField>
                <ReferenceField source="TerritoryId" reference="Territory">
                    <TextField source="TerritoryDescription" />
                </ReferenceField>
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// EmployeeTerritory Show
export const EmployeeTerritoryShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <TextField source="Id" label="Employee Territory Id" />
                <ReferenceField source="EmployeeId" reference="Employee">
                    <TextField source="LastName" />
                </ReferenceField>
                <ReferenceField source="TerritoryId" reference="Territory">
                    <TextField source="TerritoryDescription" />
                </ReferenceField>
            </SimpleShowLayout>
        </Show>
    );
};

// EmployeeTerritory Create
export const EmployeeTerritoryCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <ReferenceInput source="EmployeeId" reference="Employee" fullWidth>
                    <SelectInput optionText="LastName" validate={required()} />
                </ReferenceInput>
                <ReferenceInput source="TerritoryId" reference="Territory" fullWidth>
                    <SelectInput optionText="TerritoryDescription" validate={required()} />
                </ReferenceInput>
            </SimpleForm>
        </Create>
    );
};

// EmployeeTerritory Edit
export const EmployeeTerritoryEdit = (props) => {
    return (
        <Edit {...props}>
            <SimpleForm>
                <ReferenceInput source="EmployeeId" reference="Employee" fullWidth>
                    <SelectInput optionText="LastName" validate={required()} />
                </ReferenceInput>
                <ReferenceInput source="TerritoryId" reference="Territory" fullWidth>
                    <SelectInput optionText="TerritoryDescription" validate={required()} />
                </ReferenceInput>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: EmployeeTerritoryList,
    show: EmployeeTerritoryShow,
    create: EmployeeTerritoryCreate,
    edit: EmployeeTerritoryEdit,
};