// begin MANDATORY imports (always generated EXACTLY)
import React, { useState } from 'react';
import { List, Datagrid, TextField, DateField, NumberField } from 'react-admin';
import { ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput } from 'react-admin';
import { SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button, Card, CardContent, CardActions, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { useRecordContext, useRedirect, useListContext, required } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import PersonIcon from '@mui/icons-material/Person';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
// end mandatory imports

const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
        <BooleanInput label="Email Opt Out" source="email_opt_out" />
    </Filter>
);

// Customer Card View Component
const CustomerCard = ({ record }) => (
    <Card sx={{ 
        minWidth: 300, 
        maxWidth: 350, 
        height: 280,
        margin: 1, 
        display: 'flex', 
        flexDirection: 'column',
        transition: 'transform 0.2s, box-shadow 0.2s',
        '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: 3
        }
    }}>
        <CardContent sx={{ flexGrow: 1, pb: 1 }}>
            <Typography variant="h6" component="div" sx={{ 
                mb: 2, 
                fontWeight: 'bold',
                color: 'primary.main',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
            }}>
                {record.CompanyName}
            </Typography>
            
            <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                <PersonIcon color="action" fontSize="small" />
                <Typography variant="body2" color="text.secondary">
                    {record.ContactName || 'No contact name'}
                </Typography>
            </Box>
            
            <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationOnIcon color="action" fontSize="small" />
                <Typography variant="body2" color="text.secondary">
                    {record.City ? `${record.City}, ${record.Country || ''}` : record.Country || 'No location'}
                </Typography>
            </Box>
            
            <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AccountBalanceWalletIcon color="action" fontSize="small" />
                <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                    {record.Balance ? `$${record.Balance.toLocaleString()}` : '$0.00'}
                </Typography>
            </Box>
        </CardContent>
        
        <CardActions sx={{ pt: 0, pb: 2, px: 2, justifyContent: 'space-between' }}>
            <ShowButton record={record} size="small" />
            <Box>
                <EditButton record={record} size="small" sx={{ mr: 1 }} />
                <DeleteButton record={record} size="small" />
            </Box>
        </CardActions>
    </Card>
);

// Customer Grid View Component
const CustomerGridView = () => {
    const { data, isLoading } = useListContext();
    
    if (isLoading) return <div>Loading...</div>;
    
    return (
        <Grid container spacing={2} sx={{ mt: 1 }}>
            {data?.map(record => (
                <Grid item key={record.id} xs={12} sm={6} md={4} lg={3}>
                    <CustomerCard record={record} />
                </Grid>
            ))}
        </Grid>
    );
};

// View Toggle Component
const ViewToggle = ({ viewMode, setViewMode }) => (
    <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(event, newViewMode) => {
                if (newViewMode !== null) {
                    setViewMode(newViewMode);
                }
            }}
            aria-label="view mode"
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

// Customer List
export const CustomerList = (props) => {
    const [viewMode, setViewMode] = useState('list');
    
    return (
        <List 
            filters={<CustomerFilter />} 
            {...props} 
            sort={{ field: 'CompanyName', order: 'ASC' }} 
            pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}
        >
            <ViewToggle viewMode={viewMode} setViewMode={setViewMode} />
            {viewMode === 'list' ? (
                <Datagrid rowClick="show">
                    <TextField source="CompanyName" label="Company Name" />
                    <TextField source="ContactName" label="Contact Name" />
                    <TextField source="City" label="City" />
                    <TextField source="Country" label="Country" />
                    <NumberField source="Balance" label="Balance" options={{ style: 'currency', currency: 'USD' }} />
                    <EditButton />
                    <DeleteButton />
                </Datagrid>
            ) : (
                <CustomerGridView />
            )}
        </List>
    );
};

// Customer Show
export const CustomerShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Customer Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Company Name">
                                <TextField source="CompanyName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Balance">
                                <NumberField source="Balance" options={{ style: 'currency', currency: 'USD' }} />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Contact Name">
                                <TextField source="ContactName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Contact Title">
                                <TextField source="ContactTitle" />
                            </Labeled>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
        </SimpleShowLayout>
        <TabbedShowLayout>
            <Tab label="Orders">
                <ReferenceManyField reference="Order" target="CustomerId" addLabel={false} pagination={<Pagination />}>
                    <Datagrid rowClick="show">
                        <TextField source="Id" label="Order ID" />
                        <TextField source="ShipName" label="Ship Name" />
                        <DateField source="OrderDate" label="Order Date" />
                        <NumberField source="AmountTotal" label="Amount Total" options={{ style: 'currency', currency: 'USD' }} />
                        <DateField source="ShippedDate" label="Shipped Date" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
                <AddOrderButton />
            </Tab>
        </TabbedShowLayout>
    </Show>
);

// Custom Add Order Button
const AddOrderButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Order/create?source=${encodeURIComponent(JSON.stringify({ CustomerId: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add New Order
        </Button>
    );
};

// Customer Create
export const CustomerCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Customer
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="CompanyName" label="Company Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactName" label="Contact Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="Balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Create>
);

// Customer Edit
export const CustomerEdit = (props) => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Customer
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="CompanyName" label="Company Name" fullWidth validate={required()} />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactName" label="Contact Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="Balance" label="Balance" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="ContactTitle" label="Contact Title" fullWidth />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Edit>
);

const CustomerResource = {
    list: CustomerList,
    show: CustomerShow,
    create: CustomerCreate,
    edit: CustomerEdit,
};

export default CustomerResource;