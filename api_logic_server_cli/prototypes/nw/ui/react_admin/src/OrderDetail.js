import React from 'react';
import {
  List,SelectInput,
  FunctionField,
  Datagrid,
  TextField,
  NumberField,
  ReferenceField,
  Show,
  TabbedShowLayout,
  Tab,
  SimpleShowLayout,
  TextInput,
  NumberInput,
  ReferenceInput,
  Create,
  SimpleForm,
  Edit,
  Filter,
  Pagination,
  BooleanField
} from 'react-admin';

// Filter component for OrderDetail
const OrderDetailFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search by ID" source="Id" alwaysOn />
    <ReferenceInput label="Order" source="OrderId" reference="Order" allowEmpty>
      <NumberInput />
    </ReferenceInput>
    <ReferenceInput label="Product" source="ProductId" reference="Product" allowEmpty>
      <NumberInput />
    </ReferenceInput>
  </Filter>
);

// List component for OrderDetail
export const OrderDetailList = (props) => (
  <List {...props} filters={<OrderDetailFilter />} perPage={7} pagination={Pagination} sort={{ field: 'Id', order: 'ASC' }}>
    <Datagrid rowClick="show">
      <TextField source="Id" />
      <ReferenceField label="Order" source="OrderId" reference="Order">
        <TextField source="ShipName" />
      </ReferenceField>
      <ReferenceField label="Product" source="ProductId" reference="Product">
        <TextField source="ProductName" />
      </ReferenceField>
      <FunctionField label="Quantity" source="Quantity" render={record => `${record.Quantity}`} />
      <FunctionField label="Unit Price" source="UnitPrice" render={record => `$${record.UnitPrice}`} />
      <FunctionField label="Discount" source="Discount" render={record => `${record.Discount * 100}%`} />
      <FunctionField label="Amount" source="Amount" render={record => `$${record.Amount}`} />
    </Datagrid>
  </List>
);

// Show component for OrderDetail
export const OrderDetailShow = (props) => (
  <Show {...props}>
    <TabbedShowLayout>
      <Tab label="Details">
        <SimpleShowLayout>
          <TextField source="Id" />
          <ReferenceField label="Order" source="OrderId" reference="Order">
            <TextField source="ShipName" />
          </ReferenceField>
          <ReferenceField label="Product" source="ProductId" reference="Product">
            <TextField source="ProductName" />
          </ReferenceField>
          <NumberField label="Quantity" source="Quantity" />
          <NumberField label="Unit Price" source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
          <NumberField label="Discount" source="Discount" />
          <NumberField label="Amount" source="Amount" options={{ style: 'currency', currency: 'USD' }} />
        </SimpleShowLayout>
      </Tab>
    </TabbedShowLayout>
  </Show>
);

// Create component for OrderDetail
export const OrderDetailCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <ReferenceInput label="Order" source="OrderId" reference="Order">
        <SelectInput optionText="ShipName" />
      </ReferenceInput>
      <ReferenceInput label="Product" source="ProductId" reference="Product">
        <SelectInput optionText="ProductName" />
      </ReferenceInput>
      <NumberInput source="Quantity" />
      <NumberInput source="UnitPrice" />
      <NumberInput source="Discount" />
    </SimpleForm>
  </Create>
);

// Edit component for OrderDetail
export const OrderDetailEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <ReferenceInput label="Order" source="OrderId" reference="Order">
        <SelectInput optionText="ShipName" />
      </ReferenceInput>
      <ReferenceInput label="Product" source="ProductId" reference="Product">
        <SelectInput optionText="ProductName" />
      </ReferenceInput>
      <NumberInput source="Quantity" />
      <NumberInput source="UnitPrice" />
      <NumberInput source="Discount" />
      <NumberField source="Amount" disabled />
    </SimpleForm>
  </Edit>
);
