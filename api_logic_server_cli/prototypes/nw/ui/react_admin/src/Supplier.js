import React from 'react';
import { List, Show, SimpleShowLayout, Datagrid, TextField, NumberField, ReferenceField, Filter, TextInput, ShowController, Tab, TabbedShowLayout, NumberInput, Edit, SimpleForm, Create, ReferenceInput, SelectInput, EditButton, SimpleList } from 'react-admin';

// Filters applied to the supplier list
const SupplierFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
        <TextInput label="Search by Country" source="Country" />
    </Filter>
);

// Listing Suppliers
export const SupplierList = (props) => (
    <List {...props} filters={<SupplierFilter />} pagination={false}>
        <Datagrid rowClick="show">
            <TextField source="id" label="ID" />
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="ContactName" label="Contact Name" />
            <TextField source="ContactTitle" label="Contact Title" />
            <TextField source="City" label="City" />
            <TextField source="Country" label="Country" />
            <EditButton />
        </Datagrid>
    </List>
);

// Show Supplier
export const SupplierShow = (props) => (
    <ShowController {...props}>
        {(controllerProps) => (
            <Show {...controllerProps}>
                <SimpleShowLayout>
                    <TextField source="CompanyName" label="Company Name" />
                    <TextField source="ContactName" label="Contact Name" />
                    <TextField source="ContactTitle" label="Contact Title" />
                    <TextField source="Address" label="Address" />
                    <TextField source="City" label="City" />
                    <TextField source="Region" label="Region" />
                    <TextField source="PostalCode" label="Postal Code" />
                    <TextField source="Country" label="Country" />
                    <TextField source="Phone" label="Phone" />
                    <TextField source="Fax" label="Fax" />
                    <TextField source="HomePage" label="Homepage" />
                    <TextField source="id" label="ID" />
                </SimpleShowLayout>
            </Show>
        )}
    </ShowController>
);

// Create a new Supplier
export const SupplierCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="ContactName" label="Contact Name" />
            <TextInput source="ContactTitle" label="Contact Title" />
            <TextInput source="Address" label="Address" />
            <TextInput source="City" label="City" />
            <TextInput source="Region" label="Region" />
            <TextInput source="PostalCode" label="Postal Code" />
            <TextInput source="Country" label="Country" />
            <TextInput source="Phone" label="Phone" />
            <TextInput source="Fax" label="Fax" />
            <TextInput source="HomePage" label="Homepage" />
        </SimpleForm>
    </Create>
);

// Edit an existing Supplier
export const SupplierEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="ContactName" label="Contact Name" />
            <TextInput source="ContactTitle" label="Contact Title" />
            <TextInput source="Address" label="Address" />
            <TextInput source="City" label="City" />
            <TextInput source="Region" label="Region" />
            <TextInput source="PostalCode" label="Postal Code" />
            <TextInput source="Country" label="Country" />
            <TextInput source="Phone" label="Phone" />
            <TextInput source="Fax" label="Fax" />
            <TextInput source="HomePage" label="Homepage" />
        </SimpleForm>
    </Edit>
);
