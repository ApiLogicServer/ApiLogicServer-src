import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    ReferenceField,
    Show,
    SimpleShowLayout,
    Create,
    SimpleForm,
    TextInput,
    Edit,
    Pagination,
    Filter,
} from 'react-admin';

// Filters for list screens
const RegionFilters = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput label="Region Description" source="RegionDescription" alwaysOn />
    </Filter>
);

// Custom pagination component
const RegionPagination = props => <Pagination rowsPerPageOptions={[5, 10, 25]} {...props} />;

// Region List Component
export const RegionList = props => (
    <List {...props} filters={<RegionFilters />} pagination={<RegionPagination />} perPage={7}>
        <Datagrid rowClick="show">
            <TextField source="RegionDescription" label="Region Description" sortable />
            <TextField source="Id" label="Region ID" sortable={false} />
        </Datagrid>
    </List>
);

// Region Show Component
export const RegionShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="RegionDescription" label="Region Description" />
            <TextField source="Id" label="Region ID" />
        </SimpleShowLayout>
    </Show>
);

// Region Create Component
export const RegionCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="RegionDescription" label="Region Description" />
        </SimpleForm>
    </Create>
);

// Region Edit Component
export const RegionEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="RegionDescription" label="Region Description" />
            <TextField source="Id" label="Region ID" disabled />
        </SimpleForm>
    </Edit>
);