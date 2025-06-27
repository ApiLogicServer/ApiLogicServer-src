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

export const OrderDetailList = (props) => {
    return (
        <List {...props} sort={{ field: 'Id', order: 'ASC' }}>
            <Datagrid rowClick="show">
                <TextField source="Id" label="ID" />
                <ReferenceField source="ProductId" reference="Product" label="Product">
                    <TextField source="ProductName" />
                </ReferenceField>
                <ReferenceField source="OrderId" reference="Order" label="Order">
                    <TextField source="Id" />
                </ReferenceField>
                <NumberField source="UnitPrice" label="Unit Price" options={{ style: 'currency', currency: 'USD' }} />
                <NumberField source="Quantity" label="Quantity" />
                <NumberField source="Discount" label="Discount" />
                <NumberField source="Amount" label="Amount" options={{ style: 'currency', currency: 'USD' }} />
                <DateField source="ShippedDate" label="Shipped Date" />
                <EditButton />
                <DeleteButton />
            </Datagrid>
        </List>
    );
};

// Order Detail Show
export const OrderDetailShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Order Detail
                    </Typography>
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="ID">
                                    <TextField source="Id" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Product">
                                    <ReferenceField source="ProductId" reference="Product">
                                        <TextField source="ProductName" />
                                    </ReferenceField>
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Order">
                                    <ReferenceField source="OrderId" reference="Order">
                                        <TextField source="Id" />
                                    </ReferenceField>
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Unit Price">
                                    <NumberField source="UnitPrice" options={{ style: 'currency', currency: 'USD' }} />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Quantity">
                                    <NumberField source="Quantity" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Discount">
                                    <NumberField source="Discount" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Amount">
                                    <NumberField source="Amount" options={{ style: 'currency', currency: 'USD' }} />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Shipped Date">
                                    <DateField source="ShippedDate" />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleShowLayout>
        </Show>
    );
};

// Order Detail Create
export const OrderDetailCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Order Detail
                    </Typography>
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="ProductId" reference="Product" fullWidth>
                                    <SelectInput optionText="ProductName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="OrderId" reference="Order" fullWidth>
                                    <SelectInput optionText="Id" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Quantity" validate={required()} fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Discount" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Order Detail Edit
export const OrderDetailEdit = (props) => {
    return (
        <Edit {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Order Detail
                    </Typography>
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="ProductId" reference="Product" fullWidth>
                                    <SelectInput optionText="ProductName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="OrderId" reference="Order" fullWidth>
                                    <SelectInput optionText="Id" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Quantity" validate={required()} fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Discount" fullWidth />
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: OrderDetailList,
    show: OrderDetailShow,
    create: OrderDetailCreate,
    edit: OrderDetailEdit,
};