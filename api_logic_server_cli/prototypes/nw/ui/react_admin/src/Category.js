```jsx
import React from 'react';
import {
    List, Datagrid, TextField, ReferenceField,
    Show, TabbedShowLayout, Tab, SimpleShowLayout,
    TextInput, ReferenceManyField, Pagination,
    Filter, Create, Edit, SimpleForm, SelectInput, ReferenceInput
} from 'react-admin';

// Define the filters for the Category List
const CategoryFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput label="Category Name" source="CategoryName" />
        <TextInput label="Description" source="Description" />
    </Filter>
);

// Pagination configuration
const CategoryPagination = props => <Pagination rowsPerPageOptions={[7]} {...props} />;

// List view for Categories
export const CategoryList = (props) => (
    <List {...props} filters={<CategoryFilter />} pagination={<CategoryPagination />}>
        <Datagrid rowClick="show">
            <TextField source="CategoryName" label="Category Name" />
            <TextField source="Description" label="Description" />
            <TextField source="Client_id" label="Client" />
        </Datagrid>
    </List>
);

// Show view for a single Category
export const CategoryShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="CategoryName" label="Category Name" />
            <TextField source="Description" label="Description" />
            <TextField source="Client_id" label="Client" />
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Related Resources">
                <ReferenceManyField
                    label="Products"
                    reference="Product"
                    target="CategoryId"
                >
                    <Datagrid rowClick="show">
                        <TextField source="ProductName" label="Product Name" />
                    </Datagrid>
                </ReferenceManyField>
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Create view for a Category
export const CategoryCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="CategoryName" label="Category Name" />
            <TextInput source="Description" label="Description" />
            <ReferenceInput label="Client" source="Client_id" reference="Client">
                <SelectInput optionText="name" />
            </ReferenceInput>
        </SimpleForm>
    </Create>
);

// Edit view for a Category
export const CategoryEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="CategoryName" label="Category Name" />
            <TextInput source="Description" label="Description" />
            <ReferenceInput label="Client" source="Client_id" reference="Client">
                <SelectInput optionText="name" />
            </ReferenceInput>
        </SimpleForm>
    </Edit>
);
```