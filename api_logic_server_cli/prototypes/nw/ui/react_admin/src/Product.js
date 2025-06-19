import React from 'react';
import {
    List, Datagrid, TextField, ReferenceField, Show, SimpleShowLayout, TabbedShowLayout, Tab,
    Create, SimpleForm, TextInput, NumberInput, NumberField, DateField, BooleanField, Edit,
    ReferenceManyField, ReferenceInput, SelectInput, Filter, Pagination
} from 'react-admin';

// Filters for the Product List
const ProductFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Product Name" source="ProductName" alwaysOn />
        <ReferenceInput label="Category" source="CategoryId" reference="Category" allowEmpty>
            <SelectInput optionText="CategoryName_ColumnName" />
        </ReferenceInput>
        <ReferenceInput label="Supplier" source="SupplierId" reference="Supplier" allowEmpty>
            <SelectInput optionText="CompanyName" />
        </ReferenceInput>
    </Filter>
);

// List view of Products
export const ProductList = (props) => (
    <List {...props} filters={<ProductFilter />} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} />}>
        <Datagrid rowClick="show">
            <TextField source="ProductName" />
            <ReferenceField source="CategoryId" reference="Category">
                <TextField source="CategoryName_ColumnName" />
            </ReferenceField>
            <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="UnitsInStock" />
            <NumberField source="UnitsOnOrder" />
            <NumberField source="ReorderLevel" />
            <BooleanField source="Discontinued" />
            <TextField source="Id" />
        </Datagrid>
    </List>
);

// Show view of Products
export const ProductShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="ProductName" />
            <ReferenceField source="CategoryId" reference="Category">
                <TextField source="CategoryName_ColumnName" />
            </ReferenceField>
            <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
            <NumberField source="UnitsInStock" />
            <NumberField source="UnitsOnOrder" />
            <NumberField source="ReorderLevel" />
            <BooleanField source="Discontinued" />
            <TextField source="Id" />
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Order Details">
                <ReferenceManyField reference="OrderDetail" target="ProductId" addLabel={false}>
                    <Datagrid>
                        <ReferenceField source="OrderId" reference="Order">
                            <TextField source="Id" />
                        </ReferenceField>
                        <NumberField source="Quantity" />
                        <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
                        <TextField source="Id" />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Create view for Products
export const ProductCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="ProductName" />
            <ReferenceInput source="CategoryId" reference="Category">
                <SelectInput optionText="CategoryName_ColumnName" />
            </ReferenceInput>
            <NumberInput source="UnitPrice" />
            <NumberInput source="UnitsInStock" />
            <NumberInput source="UnitsOnOrder" />
            <NumberInput source="ReorderLevel" />
            <BooleanField source="Discontinued" />
        </SimpleForm>
    </Create>
);

// Edit view for Products
export const ProductEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="ProductName" />
            <ReferenceInput source="CategoryId" reference="Category">
                <SelectInput optionText="CategoryName_ColumnName" />
            </ReferenceInput>
            <NumberInput source="UnitPrice" />
            <NumberInput source="UnitsInStock" />
            <NumberInput source="UnitsOnOrder" />
            <NumberInput source="ReorderLevel" />
            <BooleanField source="Discontinued" />
        </SimpleForm>
    </Edit>
);