import React from 'react';
import {
  List,
  Datagrid,
  TextField,
  NumberField,
  ReferenceField,
  Show,
  SimpleShowLayout,
  TabbedShowLayout,
  Tab,
  TextInput,
  NumberInput,
  ReferenceManyField,
  ReferenceInput,
  SelectInput,
  Create,
  SimpleForm,
  Edit,
  Filter,
} from 'react-admin';

// Filters for Category List
//theme color;
const CategoryFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
    <TextInput label="Category Name" source="CategoryName_ColumnName" />
    <TextInput label="Description" source="Description" />
  </Filter>
);

// Category List
export const CategoryList = (props) => (
  <List filters={<CategoryFilter />} {...props} perPage={7}>
    <Datagrid rowClick="show">
      <TextField source="CategoryName_ColumnName" label="Category Name" />
      <TextField source="Description" />
    </Datagrid>
  </List>
);

// Category Show
export const CategoryShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="CategoryName_ColumnName" label="Category Name" />
      <TextField source="Description" />
      <NumberField source="Id" label="ID" />
      <ReferenceManyField reference="Product" target="CategoryId" label="Products">
        <TabbedShowLayout>
          <Tab label="Products">
            <Datagrid rowClick="show">
              <TextField source="ProductName" label="Product Name" />
              <NumberField source="UnitPrice" label="Unit Price" />
            </Datagrid>
          </Tab>
        </TabbedShowLayout>
      </ReferenceManyField>
    </SimpleShowLayout>
  </Show>
);

// Category Create
export const CategoryCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="CategoryName_ColumnName" label="Category Name" />
      <TextInput multiline source="Description" />
    </SimpleForm>
  </Create>
);

// Category Edit
export const CategoryEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="CategoryName_ColumnName" label="Category Name" />
      <TextInput multiline source="Description" />
    </SimpleForm>
  </Edit>
);
