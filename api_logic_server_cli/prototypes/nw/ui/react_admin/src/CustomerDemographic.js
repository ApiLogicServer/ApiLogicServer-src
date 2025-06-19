import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    Show,
    SimpleShowLayout,
    Edit,
    SimpleForm,
    TextInput,
    Create,
    Filter,
    Pagination,
} from 'react-admin';

const CustomerDemographicFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput label="Customer Description" source="CustomerDesc" />
    </Filter>
);

export const CustomerDemographicList = (props) => (
    <List filters={<CustomerDemographicFilter />} pagination={<Pagination perPage={7} />} {...props}>
        <Datagrid rowClick="show">
            <TextField source="Id" label="ID" />
            <TextField source="CustomerDesc" label="Customer Description" />
        </Datagrid>
    </List>
);

export const CustomerDemographicShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="Id" label="ID" />
            <TextField source="CustomerDesc" label="Customer Description" />
        </SimpleShowLayout>
    </Show>
);

export const CustomerDemographicCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="Id" label="ID" />
            <TextInput source="CustomerDesc" label="Customer Description" />
        </SimpleForm>
    </Create>
);

export const CustomerDemographicEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="Id" label="ID" disabled />
            <TextInput source="CustomerDesc" label="Customer Description" />
        </SimpleForm>
    </Edit>
);