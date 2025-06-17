import React from 'react';
import { 
    List, 
    Datagrid, 
    TextField, 
    NumberField,
    Show, 
    SimpleShowLayout, 
    TabbedShowLayout, 
    Tab,
    ReferenceManyField,
    TextInput, 
    Edit, 
    SimpleForm,
    Create,
    NumberInput,
    Pagination, 
    Filter, 
    ReferenceField,
    FunctionField
} from 'react-admin';
import { Grid, Box } from '@mui/material';

// Filters for the Customer list
const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company" source="CompanyName" alwaysOn />
        <TextInput label="Search by Contact" source="ContactName" />
    </Filter>
);

// Customer List
export const CustomerList = (props) => (
    <List filters={<CustomerFilter />} pagination={<Pagination />} {...props}>
        <Datagrid rowClick="show">
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="ContactName" label="Contact Name" />
            <NumberField source="Balance" label="Balance" />
            <NumberField source="CreditLimit" label="Credit Limit" />
            <NumberField source="OrderCount" label="Order Count" />
            <NumberField source="UnpaidOrderCount" label="Unpaid Orders" />
            <TextField source="Phone" label="Phone" />
            <NumberField source="Id" label="ID" />
        </Datagrid>
    </List>
);

// Customer Show
export const CustomerShow = (props) => (
    <Show {...props}>
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

            <TabbedShowLayout>
                <Tab label="Placed Order List">
                    <ReferenceManyField
                        reference="Order"
                        target="CustomerId"
                        label="Placed Orders"
                    >
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="Order ID" />
                            <TextField source="OrderDate" label="Order Date" />
                            <TextField source="AmountTotal" label="Total Amount" />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

// Customer Create
export const CustomerCreate = (props) => (
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
        </SimpleForm>
    </Create>
);

// Customer Edit
export const CustomerEdit = (props) => (
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
        </SimpleForm>
    </Edit>
);