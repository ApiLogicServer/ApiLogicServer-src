// begin MANDATORY imports (always generated EXACTLY)
import React from 'react';
import { List, FunctionField, Datagrid, TextField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button } from '@mui/material';
import { useRecordContext, useRedirect, Link, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
// end mandatory imports

export const ProductList = (props) => (
    <List {...props} sort={{ field: 'name', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
        <Datagrid rowClick="show">
            <TextField source="name" label="Name" />
            <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
        </Datagrid>
    </List>
);

// Product Show
export const ProductShow = (props) => (
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
                <Divider sx={{ my: 2 }} />
            </Box>
            <ReferenceManyField reference="Item" target="product_id" addLabel={false} pagination={<Pagination />}>
                <Datagrid rowClick="show">
                    <TextField source="id" label="Item ID" />
                    <NumberField source="quantity" label="Quantity" />
                    <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
                    <EditButton />
                    <DeleteButton />
                </Datagrid>
            </ReferenceManyField>
            <AddItemButton />
        </SimpleShowLayout>
    </Show>
);

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
export const ProductCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Product
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="name" label="Name" fullWidth />
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

// Product Edit
export const ProductEdit = (props) => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Product
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="name" label="Name" fullWidth />
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

export default {
    list: ProductList,
    show: ProductShow,
    create: ProductCreate,
    edit: ProductEdit,
};