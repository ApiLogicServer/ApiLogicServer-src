import React, { useState } from 'react';
import { List, FunctionField, Datagrid, TextField, DateField, NumberField, ReferenceField, ReferenceManyField, Show, TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput, ReferenceInput, SelectInput, Create, SimpleForm, Edit, Filter, Pagination, BooleanField, BooleanInput, TopToolbar, Button, useListContext } from 'react-admin';  // mandatory import
import { ToggleButton, ToggleButtonGroup, Box, Card, CardContent, CardActions, Typography } from '@mui/material';
import { ViewList, ViewModule } from '@mui/icons-material';

// Filters for the list view
const CustomerFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="q" alwaysOn />
        <TextInput label="Company Name" source="CompanyName" />
        <TextInput label="Contact Name" source="ContactName" />
        <TextInput label="City" source="City" />
        <TextInput label="Country" source="Country" />
    </Filter>
);

// Card view component for customers
const CustomerCard = ({ record, ...props }) => (
    <Card sx={{ margin: 1, minWidth: 300, maxWidth: 350 }}>
        <CardContent>
            <Typography variant="h6" component="div" gutterBottom>
                {record.CompanyName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                Contact: {record.ContactName}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                {record.Address && `${record.Address}, `}{record.City}
                {record.Region && `, ${record.Region}`}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                {record.Country}
            </Typography>
            {record.Phone && (
                <Typography variant="body2" color="text.secondary">
                    Phone: {record.Phone}
                </Typography>
            )}
            {record.Balance && (
                <Typography variant="body2" color="text.primary" sx={{ mt: 1, fontWeight: 'bold' }}>
                    Balance: ${record.Balance.toLocaleString()}
                </Typography>
            )}
        </CardContent>
        <CardActions>
            <Button 
                size="small" 
                onClick={() => window.location.href = `#/Customer/${record.Id}/show`}
            >
                View Details
            </Button>
            <Button 
                size="small" 
                onClick={() => window.location.href = `#/Customer/${record.Id}`}
            >
                Edit
            </Button>
        </CardActions>
    </Card>
);

// Custom list actions with view toggle
const CustomerListActions = ({ viewMode, setViewMode }) => (
    <TopToolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <ToggleButtonGroup
                value={viewMode}
                exclusive
                onChange={(event, newView) => {
                    if (newView !== null) {
                        setViewMode(newView);
                    }
                }}
                aria-label="view mode"
                size="small"
            >
                <ToggleButton value="list" aria-label="list view">
                    <ViewList />
                </ToggleButton>
                <ToggleButton value="cards" aria-label="card view">
                    <ViewModule />
                </ToggleButton>
            </ToggleButtonGroup>
        </Box>
    </TopToolbar>
);

// Custom card grid component that uses react-admin's data context
const CustomerCardGrid = () => {
    const { data, isLoading } = useListContext();
    
    if (isLoading) return <div>Loading...</div>;
    
    return (
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, padding: 2 }}>
            {data && data.map((record) => (
                <CustomerCard key={record.Id} record={record} />
            ))}
        </Box>
    );
};

export const CustomerList = (props) => {
    const [viewMode, setViewMode] = useState('list');

    return (
        <List 
            filters={<CustomerFilter />} 
            {...props} 
            perPage={viewMode === 'cards' ? 12 : 7} 
            pagination={<Pagination />}
            actions={<CustomerListActions viewMode={viewMode} setViewMode={setViewMode} />}
        >
            {viewMode === 'list' ? (
                <Datagrid rowClick="show">
                    <TextField source="CompanyName" label="Company Name" />
                    <TextField source="ContactName" label="Contact Name" />
                    <TextField source="Address" label="Address" />
                    <TextField source="City" label="City" />
                    <TextField source="Country" label="Country" />
                    <TextField source="Phone" label="Phone" />
                    <TextField source="Fax" label="Fax" />
                    <NumberField source="Id" label="Customer ID"/>
                </Datagrid>
            ) : (
                <CustomerCardGrid />
            )}
        </List>
    );
};

export const CustomerShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <TextField source="CompanyName" label="Company Name" />
            <TextField source="ContactName" label="Contact Name" />
            <TextField source="ContactTitle" label="Contact Title" />
            <TextField source="Address" label="Address" />
            <TextField source="City" label="City" />
            <TextField source="Region" label="Region" />
            <TextField source="PostalCode" label="Postal Code" />
            <TextField source="Country" label="Country" />
            <TextField source="Phone" label="Phone" />
            <TextField source="Fax" label="Fax" />
            <NumberField source="Balance" options={{ style: 'currency', currency: 'USD' }} label="Balance" />
            <NumberField source="CreditLimit" options={{ style: 'currency', currency: 'USD' }} label="Credit Limit" />
            <NumberField source="OrderCount" label="Order Count" />
            <NumberField source="UnpaidOrderCount" label="Unpaid Orders" />
            <NumberField source="Id" label="Customer ID" />
            
            <TabbedShowLayout>
                <Tab label="Orders">
                    <ReferenceManyField
                        label="Orders"
                        reference="Order"
                        target="CustomerId"
                        perPage={7}
                    >
                        <Datagrid rowClick="show">
                            <TextField source="ShipName" label="Ship Name" />
                            <DateField source="OrderDate" label="Order Date" />
                            <DateField source="ShippedDate" label="Shipped Date" />
                            <NumberField source="AmountTotal" label="Total Amount" options={{ style: 'currency', currency: 'USD' }}/>
                            <BooleanField source="Ready" label="Ready" />
                            <NumberField source="Id" label="Order ID" />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </SimpleShowLayout>
    </Show>
);

export const CustomerCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="ContactName" label="Contact Name" />
            <TextInput source="ContactTitle" label="Contact Title" />
            <TextInput source="Address" label="Address" />
            <TextInput source="City" label="City" />
            <TextInput source="Region" label="Region" />
            <TextInput source="PostalCode" label="Postal Code" />
            <TextInput source="Country" label="Country" />
            <TextInput source="Phone" label="Phone" />
            <TextInput source="Fax" label="Fax" />
            <NumberInput source="Balance" label="Balance" />
            <NumberInput source="CreditLimit" label="Credit Limit" />
        </SimpleForm>
    </Create>
);

export const CustomerEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <TextInput source="CompanyName" label="Company Name" />
            <TextInput source="ContactName" label="Contact Name" />
            <TextInput source="ContactTitle" label="Contact Title" />
            <TextInput source="Address" label="Address" />
            <TextInput source="City" label="City" />
            <TextInput source="Region" label="Region" />
            <TextInput source="PostalCode" label="Postal Code" />
            <TextInput source="Country" label="Country" />
            <TextInput source="Phone" label="Phone" />
            <TextInput source="Fax" label="Fax" />
            <NumberInput source="Balance" label="Balance" />
            <NumberInput source="CreditLimit" label="Credit Limit" />
            <NumberField source="Id" label="Customer ID" />
        </SimpleForm>
    </Edit>
);