// begin MANDATORY imports (always generated EXACTLY)
import React from 'react';
import { List, FunctionField, Datagrid, TextField, EmailField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button } from '@mui/material';
import { useRecordContext, useRedirect, Link, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
// end mandatory imports

const ItemFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by ID" source="id" alwaysOn />
    </Filter>
);

// Item List
export const ItemList = (props) => {
    return (
        <List filters={<ItemFilter />} {...props} sort={{ field: 'id', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
            <Datagrid rowClick="show">
                <TextField source="id" label="Item ID" />
                <NumberField source="quantity" label="Quantity" />
                <NumberField source="amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
                <NumberField source="unit_price" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
                <EditButton />
            </Datagrid>
        </List>
    );
};

// Item Show
export const ItemShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Item Details
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Item ID">
                                    <TextField source="id" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Quantity">
                                    <NumberField source="quantity" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Amount">
                                    <NumberField source="amount" options={{ style: 'currency', currency: 'USD' }} />
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
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Order">
                    <ReferenceField source="order_id" reference="Order" link="show">
                        <TextField source="id" />
                    </ReferenceField>
                </Tab>
                <Tab label="Product">
                    <ReferenceField source="product_id" reference="Product" link="show">
                        <TextField source="name" />
                    </ReferenceField>
                </Tab>
            </TabbedShowLayout>
        </Show>
    );
};

// Item Create
export const ItemCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Item
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="order_id" reference="Order" fullWidth>
                                    <SelectInput optionText="id" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="product_id" reference="Product" fullWidth>
                                    <SelectInput optionText="name" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="quantity" label="Quantity" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="amount" label="Amount" fullWidth />
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

// Item Edit
export const ItemEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Item
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="order_id" reference="Order" fullWidth>
                                    <SelectInput optionText="id" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="product_id" reference="Product" fullWidth>
                                    <SelectInput optionText="name" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="quantity" label="Quantity" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="amount" label="Amount" fullWidth />
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
    list: ItemList,
    show: ItemShow,
    create: ItemCreate,
    edit: ItemEdit,
};