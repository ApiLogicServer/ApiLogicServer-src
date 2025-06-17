import React from 'react';
import {
    List, Datagrid, TextField, ReferenceField, NumberField, BooleanField,
    Show, SimpleShowLayout, TabbedShowLayout, Tab, Create, SimpleForm, Edit, Pagination,
    TextInput, NumberInput, ReferenceInput, SelectInput, Filter
} from 'react-admin';

const ProductFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Product Name" source="ProductName" alwaysOn />
        <NumberInput label="Unit Price" source="UnitPrice" />
        <TextInput label="Category" source="CategoryId" />
        <TextInput label="Supplier" source="SupplierId" />
    </Filter>
);

// List Component
export const ProductList = (props) => (
    <List {...props} filters={<ProductFilter />} pagination={<Pagination rowsPerPageOptions={[7]} />}>
        <Datagrid rowClick="show">
            <TextField source="ProductName" label="Product Name" />
            <TextField source="QuantityPerUnit" label="Quantity Per Unit" />
            <NumberField source="UnitPrice" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="UnitsInStock" label="Units In Stock" />
            <BooleanField source="Discontinued" label="Discontinued" />
            <TextField source="UnitsOnOrder" label="Units On Order" />
            <ReferenceField label="Category" source="CategoryId" reference="Category">
                <TextField source="CategoryName" />
            </ReferenceField>
            <ReferenceField label="Supplier" source="SupplierId" reference="Supplier">
                <TextField source="CompanyName" />
            </ReferenceField>
        </Datagrid>
    </List>
);

// Show Component
export const ProductShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="ProductName" label="Product Name" />
            <TextField source="QuantityPerUnit" label="Quantity Per Unit" />
            <NumberField source="UnitPrice" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="UnitsInStock" label="Units In Stock" />
            <NumberField source="UnitsOnOrder" label="Units On Order" />
            <NumberField source="ReorderLevel" label="Reorder Level" />
            <BooleanField source="Discontinued" label="Discontinued" />
            <ReferenceField label="Category" source="CategoryId" reference="Category">
                <TextField source="CategoryName" />
            </ReferenceField>
            <ReferenceField label="Supplier" source="SupplierId" reference="Supplier">
                <TextField source="CompanyName" />
            </ReferenceField>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Order Details">
                <ReferenceField reference="OrderDetail" source="Id">
                    <TextField source="Id" />
                </ReferenceField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Create Component
export const ProductCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="ProductName" label="Product Name" />
            <TextInput source="QuantityPerUnit" label="Quantity Per Unit" />
            <NumberInput source="UnitPrice" label="Unit Price" />
            <NumberInput source="UnitsInStock" label="Units In Stock" />
            <NumberInput source="UnitsOnOrder" label="Units On Order" />
            <NumberInput source="ReorderLevel" label="Reorder Level" />
            <BooleanField source="Discontinued" label="Discontinued" />  # FIXEDME - BooleanField
            <ReferenceInput label="Category" source="CategoryId" reference="Category">
                <SelectInput optionText="CategoryName" />
            </ReferenceInput>
            <ReferenceInput label="Supplier" source="SupplierId" reference="Supplier">
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
        </SimpleForm>
    </Create>
);

// Edit Component
export const ProductEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="ProductName" label="Product Name" />
            <TextInput source="QuantityPerUnit" label="Quantity Per Unit" />
            <NumberInput source="UnitPrice" label="Unit Price" />
            <NumberInput source="UnitsInStock" label="Units In Stock" />
            <NumberInput source="UnitsOnOrder" label="Units On Order" />
            <NumberInput source="ReorderLevel" label="Reorder Level" />
            <BooleanField source="Discontinued" label="Discontinued" />  # FIXEDME - BooleanField
            <ReferenceInput label="Category" source="CategoryId" reference="Category">
                <SelectInput optionText="CategoryName" />
            </ReferenceInput>
            <ReferenceInput label="Supplier" source="SupplierId" reference="Supplier">
                <SelectInput optionText="CompanyName" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);
