// Region.jsx - This file defines the React Admin components for the Region resource.

import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    Edit,
    Create, Filter,  // FIXEDME missing imports
    SimpleForm,
    TextInput,
    ReferenceManyField
} from 'react-admin'; 

const RegionList = (props) => (
    <List {...props} filters={<RegionFilter />}>
        <Datagrid rowClick="show">
            <TextField source="RegionDescription" label="Region Description" />
            <TextField source="Id" label="ID" />
        </Datagrid>
    </List>
);

const RegionShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="RegionDescription" label="Region Description" />
            <TextField source="Id" label="ID" />
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Related Territories">
                <ReferenceManyField reference="EmployeeTerritory" target="RegionId" label="Employee Territories">
                    <Datagrid rowClick="show">
                        <TextField source="TerritoryDescription" label="Territory Description" />
                        <TextField source="Id" label="ID" />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

const RegionEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="RegionDescription" label="Region Description" />
        </SimpleForm>
    </Edit>
);


const RegionCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="RegionDescription" label="Region Description*" required />
        </SimpleForm>
    </Create>
);

const RegionFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Description" source="RegionDescription" alwaysOn />
    </Filter>
);

export { RegionList, RegionShow, RegionCreate, RegionEdit };