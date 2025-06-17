```jsx
import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    ReferenceField,
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    Create,
    SimpleForm,
    ReferenceInput,
    SelectInput,
    TextInput,
    Edit
} from 'react-admin';
import { Card, CardContent } from '@mui/material';

// List view for EmployeeTerritory
export const EmployeeTerritoryList = (props) => (
    <List {...props}  perPage={7} title="Employee Territories">
        <Datagrid rowClick="show">
            <TextField source="Id" label="ID" />
            <ReferenceField source="TerritoryId" reference="Territory" label="Territory Description">
                <TextField source="TerritoryDescription" />
            </ReferenceField>
            <ReferenceField source="EmployeeId" reference="Employee" label="Employee Last Name">
                <TextField source="LastName" />
            </ReferenceField>
        </Datagrid>
    </List>
);

// Show view for EmployeeTerritory
export const EmployeeTerritoryShow = (props) => (
    <Show {...props} title="Employee Territory">
        <SimpleShowLayout>
            <TextField source="Id" label="ID" />
            <ReferenceField source="TerritoryId" reference="Territory" label="Territory Description">
                <TextField source="TerritoryDescription" />
            </ReferenceField>
            <ReferenceField source="EmployeeId" reference="Employee" label="Employee Last Name">
                <TextField source="LastName" />
            </ReferenceField>

            {/* Tabs for related data */}
            <Card>
                <CardContent>
                    <TabbedShowLayout>
                        <Tab label="Territory">
                            <ReferenceField source="TerritoryId" reference="Territory" label="Territory Description">
                                <TextField source="TerritoryDescription" />
                            </ReferenceField>
                        </Tab>
                        <Tab label="Employee">
                            <ReferenceField source="EmployeeId" reference="Employee" label="Employee Last Name">
                                <TextField source="LastName" />
                            </ReferenceField>
                        </Tab>
                    </TabbedShowLayout>
                </CardContent>
            </Card>
        </SimpleShowLayout>
    </Show>
);

// Create view for EmployeeTerritory
export const EmployeeTerritoryCreate = (props) => (
    <Create {...props} title="Create a new Employee Territory">
        <SimpleForm>
            <ReferenceInput source="TerritoryId" reference="Territory" label="Territory Description">
                <SelectInput optionText="TerritoryDescription" />
            </ReferenceInput>
            <ReferenceInput source="EmployeeId" reference="Employee" label="Employee Last Name">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
            <TextInput source="Id" disabled label="ID" />
        </SimpleForm>
    </Create>
);

// Edit view for EmployeeTerritory
export const EmployeeTerritoryEdit = (props) => (
    <Edit {...props} title="Edit Employee Territory">
        <SimpleForm>
            <TextInput source="Id" disabled label="ID" />
            <ReferenceInput source="TerritoryId" reference="Territory" label="Territory Description">
                <SelectInput optionText="TerritoryDescription" />
            </ReferenceInput>
            <ReferenceInput source="EmployeeId" reference="Employee" label="Employee Last Name">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);
```
