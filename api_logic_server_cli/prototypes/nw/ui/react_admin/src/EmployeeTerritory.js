import React from 'react';
import {
    List,
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    Datagrid,
    TextField,
    ReferenceField,
    NumberField,
    ReferenceManyField,
    TextInput,
    ReferenceInput,
    SelectInput,
    Create,
    SimpleForm,
    Edit,
    Filter
} from 'react-admin';

const EmployeeTerritoryFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Employee" source="EmployeeId" alwaysOn />
        <TextInput label="Territory" source="TerritoryId" alwaysOn />
    </Filter>
);

export const EmployeeTerritoryList = props => (
    <List filters={<EmployeeTerritoryFilter />} {...props} perPage={25} sort={{ field: 'Id', order: 'ASC' }}>
        <Datagrid rowClick="show">
            <TextField source="Id" label="ID" />
            <ReferenceField source="EmployeeId" reference="Employee" label="Employee">
                <TextField source="LastName" />
            </ReferenceField>
            <ReferenceField source="TerritoryId" reference="Territory" label="Territory">
                <TextField source="TerritoryDescription" />
            </ReferenceField>
        </Datagrid>
    </List>
);

export const EmployeeTerritoryShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="Id" label="ID" />
            <ReferenceField source="EmployeeId" reference="Employee" label="Employee">
                <TextField source="LastName" />
            </ReferenceField>
            <ReferenceField source="TerritoryId" reference="Territory" label="Territory">
                <TextField source="TerritoryDescription" />
            </ReferenceField>
            <TabbedShowLayout>
                <Tab label="Details">
                    <ReferenceManyField label="Employee" reference="Employee" target="EmployeeId">
                        <Datagrid>
                            <TextField source="FirstName" label="First Name"/>
                            <TextField source="LastName" label="Last Name"/>
                        </Datagrid>
                    </ReferenceManyField>
                    <ReferenceManyField label="Territory" reference="Territory" target="TerritoryId">
                        <Datagrid>
                            <TextField source="TerritoryDescription" label="Description"/>
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

export const EmployeeTerritoryCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="Id" />
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
            <ReferenceInput label="Territory" source="TerritoryId" reference="Territory">
                <SelectInput optionText="TerritoryDescription" />
            </ReferenceInput>
        </SimpleForm>
    </Create>
);

export const EmployeeTerritoryEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="Id" />
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
            <ReferenceInput label="Territory" source="TerritoryId" reference="Territory">
                <SelectInput optionText="TerritoryDescription" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);