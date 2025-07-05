// begin MANDATORY imports (always generated)
import React, { useState } from 'react';
import { List, FunctionField, Datagrid, TextField, EmailField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { TabbedShowLayout, Tab, SimpleShowLayout, TextInput, NumberInput, DateTimeInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, BooleanField, BooleanInput, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button, Card, CardContent, CardActions, ToggleButton, ToggleButtonGroup, Avatar } from '@mui/material';
import { useRecordContext, useRedirect, Link, required, useListContext } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewModuleIcon from '@mui/icons-material/ViewModule';
import PersonIcon from '@mui/icons-material/Person';
import WorkIcon from '@mui/icons-material/Work';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import EmailIcon from '@mui/icons-material/Email';
// end mandatory imports

const EmployeeFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search" source="LastName" alwaysOn />
    </Filter>
);

// Employee Card View Component
const EmployeeCard = ({ record }) => (
    <Card sx={{ 
        minWidth: 300, 
        maxWidth: 350, 
        height: 320,
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
            {/* Employee Photo */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                {record.PhotoPath ? (
                    <Avatar 
                        src={record.PhotoPath} 
                        alt={`${record.FirstName} ${record.LastName}`}
                        sx={{ width: 80, height: 80 }}
                    />
                ) : (
                    <Avatar sx={{ width: 80, height: 80, bgcolor: 'primary.main' }}>
                        <PersonIcon sx={{ fontSize: 40 }} />
                    </Avatar>
                )}
            </Box>
            
            <Typography variant="h6" component="div" sx={{ 
                mb: 2, 
                fontWeight: 'bold',
                color: 'primary.main',
                textAlign: 'center',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap'
            }}>
                {record.FirstName} {record.LastName}
            </Typography>
            
            <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                <WorkIcon color="action" fontSize="small" />
                <Typography variant="body2" color="text.secondary">
                    {record.Title || 'No title'}
                </Typography>
            </Box>
            
            <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                <AttachMoneyIcon color="action" fontSize="small" />
                <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                    {record.Salary ? `$${record.Salary.toLocaleString()}` : 'No salary info'}
                </Typography>
            </Box>
            
            {record.Email && (
                <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
                    <EmailIcon color="action" fontSize="small" />
                    <Typography variant="body2" color="text.secondary" sx={{
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap'
                    }}>
                        {record.Email}
                    </Typography>
                </Box>
            )}
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

// Employee Grid View Component
const EmployeeGridView = () => {
    const { data, isLoading } = useListContext();
    
    if (isLoading) return <div>Loading...</div>;
    
    return (
        <Grid container spacing={2} sx={{ mt: 1 }}>
            {data?.map(record => (
                <Grid item key={record.id} xs={12} sm={6} md={4} lg={3}>
                    <EmployeeCard record={record} />
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

// Employee List
export const EmployeeList = (props) => {
    const [viewMode, setViewMode] = useState('list');

    return (
        <>
            <ViewToggle viewMode={viewMode} setViewMode={setViewMode} />
            <List filters={<EmployeeFilter />} {...props} sort={{ field: 'LastName', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
                {viewMode === 'list' ? (
                    <Datagrid rowClick="show">
                        <TextField source="LastName" label="Last Name" />
                        <TextField source="FirstName" label="First Name" />
                        <EmailField source="Email" label="Email" />
                        <NumberField source="Salary" label="Salary" options={{ style: 'currency', currency: 'USD'}} />
                        <ReferenceField source="WorksForDepartmentId" reference="Department" label="Department">
                            <TextField source="DepartmentName" />
                        </ReferenceField>
                        <EditButton />
                        <DeleteButton />
                        <ShowButton />
                    </Datagrid>
                ) : (
                    <EmployeeGridView />
                )}
            </List>
        </>
    );
};

// Custom Photo Display Component
const EmployeePhotoDisplay = () => {
    const record = useRecordContext();
    
    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
            {record?.PhotoPath ? (
                <Avatar 
                    src={record.PhotoPath} 
                    alt={`${record.FirstName} ${record.LastName}`}
                    sx={{ width: 120, height: 120 }}
                />
            ) : (
                <Avatar sx={{ width: 120, height: 120, bgcolor: 'primary.main' }}>
                    <PersonIcon sx={{ fontSize: 60 }} />
                </Avatar>
            )}
        </Box>
    );
};

// Custom Photo Field Component  
const PhotoField = () => {
    const record = useRecordContext();
    
    return (
        <Box sx={{ mt: 1 }}>
            {record?.PhotoPath ? (
                <img 
                    src={record.PhotoPath} 
                    alt={`${record.FirstName} ${record.LastName}`}
                    style={{ 
                        width: '60px', 
                        height: '60px', 
                        borderRadius: '50%',
                        objectFit: 'cover',
                        border: '2px solid #ddd'
                    }}
                />
            ) : (
                <Avatar sx={{ width: 60, height: 60, bgcolor: 'grey.300' }}>
                    <PersonIcon />
                </Avatar>
            )}
        </Box>
    );
};

// Employee Show
export const EmployeeShow = (props) => {
    return (
        <Show {...props}>
            <SimpleShowLayout>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Employee Information
                    </Typography>
                    
                    {/* Employee Photo Section */}
                    <EmployeePhotoDisplay />
                    
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Last Name">
                                    <TextField source="LastName" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="First Name">
                                    <TextField source="FirstName" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Title">
                                    <TextField source="Title" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Salary">
                                    <NumberField source="Salary" options={{ style: 'currency', currency: 'USD'}} />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Email">
                                    <EmailField source="Email" />
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Department">
                                    <ReferenceField source="WorksForDepartmentId" reference="Department">
                                        <TextField source="DepartmentName" />
                                    </ReferenceField>
                                </Labeled>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ p: 1 }}>
                                <Labeled label="Hire Date">
                                    <DateField source="HireDate" />
                                </Labeled>
                            </Box>
                        </Grid>
                    </Grid>
                    <Divider sx={{ my: 2 }} />
                </Box>
            </SimpleShowLayout>
            <TabbedShowLayout>
                <Tab label="Audit Logs">
                    <ReferenceManyField reference="EmployeeAudit" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="Audit ID" />
                            <TextField source="LastName" label="Last Name" />
                            <TextField source="FirstName" label="First Name" />
                            <DateField source="CreatedOn" label="Created On" />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                <Tab label="Territories">
                    <ReferenceManyField reference="EmployeeTerritory" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <NumberField source="TerritoryId" label="Territory ID" />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
                <Tab label="Order History">
                    <ReferenceManyField reference="Order" target="EmployeeId" addLabel={false} pagination={<Pagination />}> 
                        <Datagrid rowClick="show">
                            <TextField source="Id" label="Order ID" />
                            <DateField source="OrderDate" label="Order Date" />
                            <NumberField source="AmountTotal" label="Total Amount" options={{ style: 'currency', currency: 'USD'}} />
                            <EditButton />
                            <DeleteButton />
                        </Datagrid>
                    </ReferenceManyField>
                </Tab>
            </TabbedShowLayout>
        </Show>
    );
};

// Employee Create
export const EmployeeCreate = (props) => {
    return (
        <Create {...props}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Create New Employee
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Email" label="Email" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="WorksForDepartmentId" reference="Department" fullWidth>
                                    <SelectInput optionText="DepartmentName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Create>
    );
};

// Employee Edit
export const EmployeeEdit = (props) => {
    return (
        <Edit {...props} redirect={false}>
            <SimpleForm>
                <Box sx={{ mb: 3 }}>
                    <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                        Edit Employee
                    </Typography>
                    <Grid container spacing={3} sx={{ mb: 2 }}>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="LastName" label="Last Name" fullWidth validate={required()} />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="FirstName" label="First Name" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <TextInput source="Email" label="Email" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <NumberInput source="Salary" label="Salary" fullWidth />
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={4}>
                            <Box sx={{ p: 1 }}>
                                <ReferenceInput source="WorksForDepartmentId" reference="Department" fullWidth>
                                    <SelectInput optionText="DepartmentName" validate={required()} />
                                </ReferenceInput>
                            </Box>
                        </Grid>
                    </Grid>
                </Box>
            </SimpleForm>
        </Edit>
    );
};

export default {
    list: EmployeeList,
    show: EmployeeShow,
    create: EmployeeCreate,
    edit: EmployeeEdit,
};