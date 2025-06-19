// Order.js
import React from 'react';
import { List, Datagrid, TextField, DateField, NumberField, ReferenceField, ReferenceManyField, Show, TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput, ReferenceInput, SelectInput, Create, SimpleForm, Edit, Filter, Pagination, BooleanField, BooleanInput } from 'react-admin';

// Order Filter
const OrderFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput source="ShipName" />
    </Filter>
);

// Order List
export const OrderList = props => (
    <List {...props} filters={<OrderFilter />} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} />}>
        <Datagrid rowClick="show">
            <TextField source="ShipName" label="Ship Name" />
            <DateField source="OrderDate" />
            <ReferenceField source="CustomerId" reference="Customer"><TextField source="CompanyName" /></ReferenceField>
            <ReferenceField source="EmployeeId" reference="Employee"><TextField source="LastName" /></ReferenceField>
            <NumberField source="Freight" options={{ style: 'currency', currency: 'USD' }} />
            <BooleanField source="Ready" />
            <NumberField source="Id" />
        </Datagrid>
    </List>
);

// Order Show
export const OrderShow = props => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="ShipName" />
            <DateField source="OrderDate" />
            <ReferenceField source="CustomerId" reference="Customer"><TextField source="CompanyName" /></ReferenceField>
            <ReferenceField source="EmployeeId" reference="Employee"><TextField source="LastName" /></ReferenceField>
            <NumberField source="AmountTotal" label="Total Amount" options={{ style: 'currency', currency: 'USD' }} />
            <TextField source="ShipAddress" />
            <TextField source="ShipCity" />
            <TextField source="ShipCountry" />
            <BooleanField source="Ready" />
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Order Details">
                <ReferenceManyField reference="OrderDetail" target="OrderId">
                    <Datagrid>
                        <ReferenceField source="ProductId" reference="Product"><TextField source="ProductName" /></ReferenceField>
                        <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
                        <NumberField source="Quantity" />
                        <NumberField source="Discount" />
                        <NumberField source="Amount" options={{ style: 'currency', currency: 'USD' }} />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Order Create
export const OrderCreate = props => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="ShipName" />
            <DateTimeInput source="OrderDate" />
            <ReferenceInput label="Customer" source="CustomerId" reference="Customer">
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
            <NumberInput source="AmountTotal" />
            <TextInput source="ShipAddress" />
            <TextInput source="ShipCity" />
            <TextInput source="ShipCountry" />
            <BooleanInput source="Ready" />
        </SimpleForm>
    </Create>
);

// Order Edit
export const OrderEdit = props => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="ShipName" />
            <DateTimeInput source="OrderDate" />
            <ReferenceInput label="Customer" source="CustomerId" reference="Customer">
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
            <ReferenceInput label="Employee" source="EmployeeId" reference="Employee">
                <SelectInput optionText="LastName" />
            </ReferenceInput>
            <NumberInput source="AmountTotal" />
            <TextInput source="ShipAddress" />
            <TextInput source="ShipCity" />
            <TextInput source="ShipCountry" />
            <BooleanInput source="Ready" />
        </SimpleForm>
    </Edit>
);