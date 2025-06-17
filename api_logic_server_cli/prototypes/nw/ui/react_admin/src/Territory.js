import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    NumberField,
    NumberInput,
    TextInput,
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    Create,
    SimpleForm,
    Edit,
    ReferenceManyField,
    ReferenceInput,
    SelectInput,
    Filter,
    Pagination
} from 'react-admin';

// Define filters for Territories list which include search capabilities
const TerritoryFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="TerritoryDescription" alwaysOn />
        <TextInput label="Region" source="RegionId" />
    </Filter>
);

// List component to display Territories
export const TerritoryList = props => (
    <List {...props} filters={<TerritoryFilter />} pagination={<Pagination />}
        sort={{ field: 'TerritoryDescription', order: 'ASC' }}>
        <Datagrid rowClick="show">
            <TextField source="TerritoryDescription" label="Territory Description" />
            <NumberField source="Id" label="ID" />
            <NumberField source="RegionId" label="Region ID" />
        </Datagrid>
    </List>
);

// Show component to display details of a specific Territory
export const TerritoryShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="TerritoryDescription" label="Territory Description" />
            <NumberField source="Id" label="ID" />
            <NumberField source="RegionId" label="Region ID" />

            {/* Related Employee Territories shown in a tabbed layout */}
            <TabbedShowLayout>
                <Tab label="Employee Territories List">
                    <ReferenceManyField reference="EmployeeTerritory" target="TerritoryId" label="Employee Territories">
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="ID" />
                            <NumberField source="EmployeeId" label="Employee ID" />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

// Create component for adding a new territory
export const TerritoryCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="TerritoryDescription" label="Territory Description" />
            <NumberInput source="RegionId" label="Region ID" />
        </SimpleForm>
    </Create>
);

// Edit component for modifying existing territory data
export const TerritoryEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="TerritoryDescription" label="Territory Description" />
            <NumberInput source="RegionId" label="Region ID" />
        </SimpleForm>
    </Edit>
);
