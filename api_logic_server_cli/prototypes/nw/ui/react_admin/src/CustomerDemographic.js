import React from 'react';
import {
    List,
    Datagrid,
    TextField,  
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    TextInput,
    Create,
    SimpleForm,
    Edit,
    NumberField,
    Filter,
    Pagination
} from 'react-admin';

/**
 * Filters for searching CustomerDemographic entities by Id.
 */
const CustomerDemographicFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Id" source="Id" alwaysOn />
    </Filter>
);

/**
 * List view for CustomerDemographic.
 */
export const CustomerDemographicList = props => (
    <List filters={<CustomerDemographicFilter />} {...props} perPage={7} pagination={<Pagination />}>
        <Datagrid rowClick="show" isRowSelectable={() => false}>
            <TextField label="Id" source="Id" />
            <TextField source="CustomerDesc" />
        </Datagrid>
    </List>
);

/**
 * Show view for CustomerDemographic.
 */
export const CustomerDemographicShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <NumberField source="Id" />
            <TextField source="CustomerDesc" />
        </SimpleShowLayout>
    </Show>
);

/**
 * Form for creating a new CustomerDemographic.
 */
export const CustomerDemographicCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput label="Id (auto-generated)" source="Id" disabled />
            <TextInput source="CustomerDesc" />
        </SimpleForm>
    </Create>
);

/**
 * Form for editing an existing CustomerDemographic.
 */
export const CustomerDemographicEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput label="Id" source="Id" disabled />
            <TextInput source="CustomerDesc" />
        </SimpleForm>
    </Edit>
);