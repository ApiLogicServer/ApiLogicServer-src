// Importing necessary components and modules from react-admin and material-ui
import React from 'react';
import { List, Datagrid, TextField, NumberField, Show, SimpleShowLayout, Create, SimpleForm, Edit, TextInput, ReferenceField, TabbedShowLayout, Tab, ReferenceInput, SelectInput, Pagination, Filter } from 'react-admin';

// Filter component for the Shipper resource
type FilterProps = {
    [key: string]: any,
};
const ShipperFilter = (props: FilterProps) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
    </Filter>
);

// List view for Shipper resource with pagination, sorting, and filtering
export const ShipperList = (props: any) => (
    <List {...props} filters={<ShipperFilter />} perPage={7} pagination={<Pagination />}>
        <Datagrid rowClick="show">
            <TextField source="CompanyName" label="Company Name" sortable={true} />
            <TextField source="Phone" label="Phone" />
            <NumberField source="Id" label="ID" />
        </Datagrid>
    </List>
);

// Show view for Shipper resource with fields organized in a simple layout
export const ShipperShow = (props: any) => (
    <Show {...props} title="Shipper Details">
        <SimpleShowLayout>
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="Phone" label="Phone" />
            <NumberField source="Id" label="ID" />
            {/* Example for future tabbed relation */}
            {/*<TabbedShowLayout>
                <Tab label="Related Resource Example">
                    <ReferenceField label="Custom Label" source="relationSource" reference="RelatedResource">
                        <TextField source="fieldName" />
                    </ReferenceField>
                </Tab>
            </TabbedShowLayout>*/}
        </SimpleShowLayout>
    </Show>
);

// Create view for adding a new Shipper
export const ShipperCreate = (props: any) => (
    <Create {...props} title="Create a new Shipper">
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="Phone" label="Phone" />
        </SimpleForm>
    </Create>
);

// Edit view for editing a Shipper
export const ShipperEdit = (props: any) => (
    <Edit {...props} title="Edit Shipper">
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="Phone" label="Phone" />
            <NumberField source="Id" label="ID" />
        </SimpleForm>
    </Edit>
);