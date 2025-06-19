import React from "react";
import {
    List,
    FunctionField,
    Datagrid,
    TextField,
    DateField,
    NumberField,
    ReferenceField,
    ReferenceManyField,
    Show,
    TabbedShowLayout,
    Tab,
    SimpleShowLayout,
    TextInput,
    NumberInput,
    DateTimeInput,
    ReferenceInput,
    SelectInput,
    Create,
    SimpleForm,
    Edit,
    Filter,
    Pagination,
    BooleanField,
    BooleanInput
} from "react-admin";

// Filters for the list view
const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput label="Company Name" source="CompanyName" />
        <TextInput label="Contact Name" source="ContactName" />
        <TextInput label="City" source="City" />
        <TextInput label="Country" source="Country" />
    </Filter>
);

export const CustomerList = (props) => (
    <List filters={<CustomerFilter />} {...props} perPage={7} pagination={<Pagination />}>
        <Datagrid rowClick="show">
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="ContactName" label="Contact Name" />
            <TextField source="Address" label="Address" />
            <TextField source="City" label="City" />
            <TextField source="Country" label="Country" />
            <TextField source="Phone" label="Phone" />
            <TextField source="Fax" label="Fax" />
            <NumberField source="Id" label="Customer ID"/>
        </Datagrid>
    </List>
);

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
            <NumberField source="Balance" options={{ style: 'currency', currency: 'USD' }} label="Balance" />
            <NumberField source="CreditLimit" options={{ style: 'currency', currency: 'USD' }} label="Credit Limit" />
            <NumberField source="OrderCount" label="Order Count" />
            <NumberField source="UnpaidOrderCount" label="Unpaid Orders" />
            <NumberField source="Id" label="Customer ID" />
            
            <TabbedShowLayout>
                <Tab label="Orders">
                    <ReferenceManyField
                        label="Orders"
                        reference="Order"
                        target="CustomerId"
                        perPage={7}
                    >
                        <Datagrid rowClick="show">
                            <TextField source="ShipName" label="Ship Name" />
                            <DateField source="OrderDate" label="Order Date" />
                            <DateField source="ShippedDate" label="Shipped Date" />
                            <NumberField source="AmountTotal" label="Total Amount" options={{ style: 'currency', currency: 'USD' }}/>
                            <BooleanField source="Ready" label="Ready" />
                            <NumberField source="Id" label="Order ID" />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

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
            <NumberInput source="Balance" label="Balance" />
            <NumberInput source="CreditLimit" label="Credit Limit" />
        </SimpleForm>
    </Create>
);

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
            <NumberInput source="Balance" label="Balance" />
            <NumberInput source="CreditLimit" label="Credit Limit" />
            <NumberField source="Id" label="Customer ID" />
        </SimpleForm>
    </Edit>
);