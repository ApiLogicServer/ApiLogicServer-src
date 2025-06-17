// src/Order.js
import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    DateField,
    NumberField,
    BooleanField,
    ReferenceField,
    ReferenceManyField,
    Show,
    TabbedShowLayout,
    Tab,
    SimpleShowLayout,
    SimpleForm,
    TextInput,
    DateTimeInput,
    ReferenceInput,
    SelectInput,
    Create,
    Edit,
    FunctionField,
    Pagination,
    Filter
} from 'react-admin';

const OrderFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search Ship Name" source="ShipName" alwaysOn />
        <TextInput label="Country" source="Country" />
        <DateTimeInput label="Order Date" source="OrderDate" />
    </Filter>
);

export const OrderList = (props) => (
    <List {...props} filters={<OrderFilter />} perPage={7} pagination={<Pagination />}>
        <Datagrid rowClick="show">
            <TextField source="Id" />
            <DateField source="OrderDate" />
            <TextField source="ShipName" />
            <TextField source="ShipAddress" />
            <TextField source="ShipCity" />
            <TextField source="ShipCountry" />
            <BooleanField source="Ready" />
            <ReferenceField label="Customer" source="CustomerId" reference="Customer">
                <FunctionField render={record => record ? `${record.CompanyName}` : ''} />
            </ReferenceField>
        </Datagrid>
    </List>
);

export const OrderShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="Id" />
            <DateField source="OrderDate" />
            <TextField source="ShipName" />
            <TextField source="ShipAddress" />
            <TextField source="ShipCity" />
            <TextField source="ShipCountry" />
            <BooleanField source="Ready" />
            <NumberField source="AmountTotal" options={{ style: 'currency', currency: 'USD' }} />
            <ReferenceField label="Customer" source="CustomerId" reference="Customer">
                <FunctionField render={record => record ? `${record.CompanyName}` : ''} />
            </ReferenceField>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Order Details">
                <ReferenceManyField reference="OrderDetail" target="OrderId" label="Order Detail List">
                    <Datagrid>
                        <ReferenceField source="ProductId" reference="Product">
                            <FunctionField render={record => record ? `${record.ProductName}` : ''} />
                        </ReferenceField>
                        <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
                        <NumberField source="Quantity" />
                        <NumberField source="Discount" options={{ style: 'percent' }} />
                        <NumberField source="Amount" options={{ style: 'currency', currency: 'USD' }} />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

export const OrderCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <ReferenceInput source="CustomerId" reference="Customer" required>
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
            <DateTimeInput source="OrderDate" />
            <TextInput source="ShipName" />
            <TextInput source="ShipAddress" />
            <TextInput source="ShipCity" />
            <TextInput source="ShipCountry" />
            <BooleanField source="Ready" /> # FIXEDME - BooleanField
        </SimpleForm>
    </Create>
);

export const OrderEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <ReferenceInput source="CustomerId" reference="Customer" required>
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
            <DateTimeInput source="OrderDate" />
            <TextInput source="ShipName" />
            <TextInput source="ShipAddress" />
            <TextInput source="ShipCity" />
            <TextInput source="ShipCountry" />
            <BooleanField source="Ready" /> # FIXEDME - BooleanField
        </SimpleForm>
    </Edit>
);