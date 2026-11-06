// begin MANDATORY imports (always generated EXACTLY)
import React, { useState } from 'react';
import { List, FunctionField, Datagrid, TextField, EmailField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button, Card, CardContent, CardActions, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useRecordContext, useRedirect, Link, required, useListContext } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
// end mandatory imports

const ProductFilter = (props) => (
  <Filter {...props}>
    <TextInput label="Search" source="name" alwaysOn />
  </Filter>
);

// Product Card Component
const ProductCard = ({ record }) => (
  <Card sx={{ m: 1, minWidth: 300, maxWidth: 345 }}>
    <CardContent>
      <Typography gutterBottom variant="h6" component="div">
        {record.name}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Unit Price: {new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(record.unit_price)}
      </Typography>
    </CardContent>
    <CardActions>
      <ShowButton record={record} size="small" />
      <EditButton record={record} size="small" />
      <DeleteButton record={record} size="small" />
    </CardActions>
  </Card>
);

// Custom Grid View Component
const ProductGrid = () => {
  const { data, isLoading } = useListContext();
  
  if (isLoading) return <div>Loading...</div>;
  
  return (
    <Grid container spacing={2} sx={{ p: 2 }}>
      {data?.map(record => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={record.id}>
          <ProductCard record={record} />
        </Grid>
      ))}
    </Grid>
  );
};

// View Toggle Component
const ViewToggle = ({ view, setView }) => (
  <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
    <ToggleButtonGroup
      value={view}
      exclusive
      onChange={(event, newView) => {
        if (newView !== null) {
          setView(newView);
        }
      }}
      aria-label="view toggle"
      size="small"
    >
      <ToggleButton value="list" aria-label="list view">
        <ViewListIcon />
      </ToggleButton>
      <ToggleButton value="cards" aria-label="card view">
        <ViewModuleIcon />
      </ToggleButton>
    </ToggleButtonGroup>
  </Box>
);

// Product List
export const ProductList = (props) => {
  const [view, setView] = useState('list'); // Default to list view
  
  return (
    <List 
      filters={<ProductFilter />} 
      {...props} 
      sort={{ field: 'name', order: 'ASC' }} 
      pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}
      actions={
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <CreateButton />
          <ViewToggle view={view} setView={setView} />
        </Box>
      }
    >
      {view === 'list' ? (
        <Datagrid rowClick="show">
          <TextField source="name" label="Name" />
          <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
        </Datagrid>
      ) : (
        <ProductGrid />
      )}
    </List>
  );
};

// Product Show
export const ProductShow = (props) => {
  return (
    <Show {...props}>
      <SimpleShowLayout>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Product Information
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Name">
                  <TextField source="name" />
                </Labeled>
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Box sx={{ p: 1 }}>
                <Labeled label="Unit Price">
                  <NumberField source="unit_price" options={{ style: 'currency', currency: 'USD' }} />
                </Labeled>
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleShowLayout>
      <TabbedShowLayout>
        <Tab label="Items">
          <ReferenceManyField reference="Item" target="product_id" addLabel={false} pagination={<Pagination />}>
            <Datagrid rowClick="show">
              <TextField source="id" label="Item ID" />
              <TextField source="quantity" label="Quantity" />
              <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
              <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
              <EditButton />
              <DeleteButton />
            </Datagrid>
          </ReferenceManyField>
          <AddItemButton />
        </Tab>
      </TabbedShowLayout>
    </Show>
  );
};

// Custom Add Item Button
const AddItemButton = () => {
  const record = useRecordContext();
  const redirect = useRedirect();

  const handleClick = () => {
    redirect(`/Item/create?source=${encodeURIComponent(JSON.stringify({ product_id: record?.id }))}`);
  };

  return (
    <Button
      variant="contained"
      color="primary"
      startIcon={<AddIcon />}
      onClick={handleClick}
      sx={{ mt: 2 }}
    >
      Add New Item
    </Button>
  );
};

// Product Create
export const ProductCreate = (props) => {
  return (
    <Create {...props}>
      <SimpleForm>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Create New Product
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <TextInput source="name" label="Name" fullWidth validate={required()} />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <NumberInput source="unit_price" label="Unit Price" fullWidth />
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleForm>
    </Create>
  );
};

// Product Edit
export const ProductEdit = (props) => {
  return (
    <Edit {...props} redirect={false}>
      <SimpleForm>
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
            Edit Product
          </Typography>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <TextInput source="name" label="Name" fullWidth validate={required()} />
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Box sx={{ p: 1 }}>
                <NumberInput source="unit_price" label="Unit Price" fullWidth />
              </Box>
            </Grid>
          </Grid>
        </Box>
      </SimpleForm>
    </Edit>
  );
};

export default {
  list: ProductList,
  show: ProductShow,
  create: ProductCreate,
  edit: ProductEdit,
};