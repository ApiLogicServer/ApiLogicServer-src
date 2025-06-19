import {
  List,
  Datagrid,
  TextField,
  NumberField,
  Show,
  TabbedShowLayout,
  Tab,
  SimpleShowLayout,
  TextInput,
  Create,
  SimpleForm,
  Edit,
  Filter,
  Pagination
} from 'react-admin';

// Define a filter component for the Shipper resource
const ShipperFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="q" alwaysOn />
    <TextInput label="Company Name" source="CompanyName" />
  </Filter>
);

// List view for Shipper resource
export const ShipperList = (props) => (
  <List {...props} filters={<ShipperFilter />} pagination={<Pagination rowsPerPage={7} />}>
    <Datagrid rowClick="show">
      <TextField source="CompanyName" label="Company Name"/>
      <TextField source="Phone" label="Phone"/>
      <NumberField source="Id" label="ID"/>
    </Datagrid>
  </List>
);

// Show view for Shipper resource
export const ShipperShow = (props) => (
  <Show {...props}>
    <SimpleShowLayout>
      <TextField source="CompanyName" label="Company Name"/>
      <TextField source="Phone" label="Phone"/>
      <NumberField source="Id" label="ID"/>
    </SimpleShowLayout>
  </Show>
);

// Create view for Shipper resource
export const ShipperCreate = (props) => (
  <Create {...props}>
    <SimpleForm>
      <TextInput source="CompanyName" label="Company Name"/>
      <TextInput source="Phone" label="Phone"/>
    </SimpleForm>
  </Create>
);

// Edit view for Shipper resource
export const ShipperEdit = (props) => (
  <Edit {...props}>
    <SimpleForm>
      <TextInput source="CompanyName" label="Company Name"/>
      <TextInput source="Phone" label="Phone"/>
      <NumberField source="Id" label="ID"/>
    </SimpleForm>
  </Edit>
);