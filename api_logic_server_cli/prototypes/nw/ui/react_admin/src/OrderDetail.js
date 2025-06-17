// `OrderDetail.js`

import React from 'react';
import {
    List,
    Datagrid,
    TextField,
    NumberField,
    DateField,
    FunctionField,
    Show,
    SimpleShowLayout,
    TabbedShowLayout,
    Tab,
    ReferenceField,
    TextInput,
    NumberInput,
    ReferenceInput,
    SelectInput,
    DateTimeInput,
    BooleanInput,
    SimpleForm,
    Create,
    Edit,
    Filter,
    Pagination,
    BooleanField,
} from 'react-admin';

// Filters for the OrderDetail list, allowing users to search and sort.
const OrderDetailFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <ReferenceInput label="Product" source="ProductId" reference="Product" allowEmpty>
            <SelectInput optionText="ProductName" />
        </ReferenceInput>
        <ReferenceInput label="Order" source="OrderId" reference="Order" allowEmpty>
            <SelectInput optionText="Id" />
        </ReferenceInput>
    </Filter>
);

// Main list view with sorting, filtering, and pagination.
export const OrderDetailList = (props) => (
    <List
        {...props}
        filters={<OrderDetailFilter />}
        perPage={7} // Shows 7 per page as specified
        sort={{ field: 'Id', order: 'ASC' }}
        pagination={<Pagination />}
    >
        <Datagrid rowClick="show">
            <TextField source="Id" />
            <ReferenceField label="Product" source="ProductId" reference="Product">
                <TextField source="ProductName" />
            </ReferenceField>
            <ReferenceField label="Order" source="OrderId" reference="Order">
                <TextField source="Id" />
            </ReferenceField>
            <NumberField source="UnitPrice" />
            <NumberField source="Quantity" />
            <NumberField source="Discount" />
            <NumberField source="Amount" />
            <DateField source="ShippedDate" />
        </Datagrid>
    </List>
);

// The Create view for OrderDetail with inline validation and auto-complete dropdowns for related references.
export const OrderDetailCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <ReferenceInput source="ProductId" reference="Product">
                <SelectInput optionText="ProductName" />
            </ReferenceInput>
            <ReferenceInput source="OrderId" reference="Order" disabled>
                <SelectInput optionText="Id" />
            </ReferenceInput>
            <NumberInput source="Quantity" />
            <NumberInput source="Discount" />
        </SimpleForm>
    </Create>
);

// The Edit view for OrderDetail with form fields for updating exiting records.
export const OrderDetailEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextField source="Id" />
            <ReferenceInput source="ProductId" reference="Product">
                <SelectInput optionText="ProductName" />
            </ReferenceInput>
            <ReferenceInput source="OrderId" reference="Order" disabled>
                <SelectInput optionText="Id" />
            </ReferenceInput>
            <NumberInput source="Quantity" />
            <NumberInput source="Discount" />
            <DateTimeInput source="ShippedDate" disabled />
        </SimpleForm>
    </Edit>
);

// The Show view for detailed display of OrderDetail and related records.
export const OrderDetailShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="Id" />
            <ReferenceField label="Product" source="ProductId" reference="Product">
                <TextField source="ProductName" />
            </ReferenceField>
            <ReferenceField label="Order" source="OrderId" reference="Order">
                <TextField source="Id" />
            </ReferenceField>
            <NumberField source="UnitPrice" />
            <NumberField source="Quantity" />
            <NumberField source="Discount" />
            <NumberField source="Amount" />
            <DateField source="ShippedDate" />
        </SimpleShowLayout>
    </Show>
);