// begin MANDATORY imports (always generated)
import React, { useState } from 'react';
import { List, Datagrid, TextField, DateField, NumberField } from 'react-admin';
import { ReferenceField, ReferenceManyField } from 'react-admin';
import { SimpleShowLayout, TextInput, NumberInput } from 'react-admin';
import { ReferenceInput, SelectInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Pagination, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, CreateButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button, ToggleButton, ToggleButtonGroup, Paper, Collapse, IconButton, Tabs, Tab as MuiTab } from '@mui/material';
import { useRecordContext, useRedirect, useGetList } from 'react-admin';
import AddIcon from '@mui/icons-material/Add';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import ViewListIcon from '@mui/icons-material/ViewList';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
// end mandatory imports

// Expandable Tree Node Component
const ExpandableTreeNode = ({ department, allDepartments, onDepartmentClick, level = 0 }) => {
    const [expanded, setExpanded] = useState(false);
    
    // Get children for this department - children have this department as their parent
    const children = allDepartments?.filter(dept => 
        dept.DepartmentId && parseInt(dept.DepartmentId) === parseInt(department.id)
    ) || [];
    
    const hasChildren = children.length > 0;
    
    const handleToggle = () => {
        if (hasChildren) {
            setExpanded(!expanded);
        }
    };
    
    return (
        <Box>
            {/* Department Row */}
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                {/* Expand/Collapse Icon */}
                <IconButton
                    size="small"
                    onClick={handleToggle}
                    sx={{ 
                        width: 24, 
                        height: 24, 
                        mr: 0.5,
                        visibility: hasChildren ? 'visible' : 'hidden'
                    }}
                >
                    {expanded ? <ExpandMoreIcon fontSize="small" /> : <ChevronRightIcon fontSize="small" />}
                </IconButton>
                
                {/* Department Button */}
                <Button
                    variant="text"
                    onClick={() => onDepartmentClick(department)}
                    sx={{ 
                        textAlign: 'left',
                        textTransform: 'none',
                        fontWeight: level === 0 ? 'bold' : 'normal',
                        justifyContent: 'flex-start',
                        p: 0.5,
                        color: level === 0 ? 'text.primary' : level === 1 ? 'text.secondary' : 'text.disabled',
                        fontSize: level === 0 ? '1rem' : level === 1 ? '0.9rem' : '0.85rem',
                        minWidth: 'auto',
                        flex: 1
                    }}
                >
                    {level === 0 ? '📁' : level === 1 ? '📄' : '📃'} {department.DepartmentName}
                </Button>
            </Box>
            
            {/* Children (with collapse animation) */}
            {hasChildren && (
                <Collapse in={expanded}>
                    <Box sx={{ ml: 3 }}>
                        {children.map(child => (
                            <ExpandableTreeNode
                                key={child.id}
                                department={child}
                                allDepartments={allDepartments}
                                onDepartmentClick={onDepartmentClick}
                                level={level + 1}
                            />
                        ))}
                    </Box>
                </Collapse>
            )}
        </Box>
    );
};

// Department Tree View Component
const DepartmentTreeView = ({ onDepartmentClick }) => {
    const { data: allDepartments, isLoading, error } = useGetList('Department', {
        pagination: { page: 1, perPage: 1000 },
        sort: { field: 'DepartmentName', order: 'ASC' }
    });

    if (isLoading) return <div>Loading departments...</div>;
    if (error) return <div>Error loading departments: {error.message}</div>;

    // Get root departments (those with no parent)
    const rootDepartments = allDepartments?.filter(d => !d.DepartmentId || d.DepartmentId === null) || [];

    return (
        <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
                Department Hierarchy
            </Typography>
            {rootDepartments.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                    No departments found
                </Typography>
            ) : (
                <Box>
                    {rootDepartments.map(rootDept => (
                        <ExpandableTreeNode
                            key={rootDept.id}
                            department={rootDept}
                            allDepartments={allDepartments}
                            onDepartmentClick={onDepartmentClick}
                            level={0}
                        />
                    ))}
                </Box>
            )}
        </Paper>
    );
};

// Enhanced Department List with View Toggle
export const DepartmentList = (props) => {
    const [viewMode, setViewMode] = useState('list');
    const [selectedDepartment, setSelectedDepartment] = useState(null);
    
    const handleViewChange = (event, newView) => {
        if (newView !== null) {
            setViewMode(newView);
        }
    };

    const handleDepartmentClick = (department) => {
        setSelectedDepartment(department);
    };

    if (viewMode === 'tree') {
        return (
            <Box sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h4">Departments</Typography>
                    <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                        <CreateButton />
                        <ToggleButtonGroup
                            value={viewMode}
                            exclusive
                            onChange={handleViewChange}
                            size="small"
                        >
                            <ToggleButton value="list">
                                <ViewListIcon sx={{ mr: 1 }} />
                                List
                            </ToggleButton>
                            <ToggleButton value="tree">
                                <AccountTreeIcon sx={{ mr: 1 }} />
                                Tree
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </Box>
                </Box>
                
                <Grid container spacing={2} sx={{ height: 'calc(100vh - 200px)' }}>
                    <Grid item xs={12} md={selectedDepartment ? 6 : 12}>
                        <DepartmentTreeView onDepartmentClick={handleDepartmentClick} />
                    </Grid>
                    {selectedDepartment && (
                        <Grid item xs={12} md={6}>
                            <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h6">
                                        {selectedDepartment.DepartmentName}
                                    </Typography>
                                    <Button
                                        variant="outlined"
                                        onClick={() => setSelectedDepartment(null)}
                                        size="small"
                                    >
                                        Close
                                    </Button>
                                </Box>
                                <DepartmentDetails department={selectedDepartment} />
                            </Paper>
                        </Grid>
                    )}
                </Grid>
            </Box>
        );
    }

    return (
        <Box sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h4">Departments</Typography>
                <ToggleButtonGroup
                    value={viewMode}
                    exclusive
                    onChange={handleViewChange}
                    size="small"
                >
                    <ToggleButton value="list">
                        <ViewListIcon sx={{ mr: 1 }} />
                        List
                    </ToggleButton>
                    <ToggleButton value="tree">
                        <AccountTreeIcon sx={{ mr: 1 }} />
                        Tree
                    </ToggleButton>
                </ToggleButtonGroup>
            </Box>
            <List {...props} sort={{ field: 'DepartmentName', order: 'ASC' }} pagination={<Pagination rowsPerPageOptions={[5, 10, 25]} showFirstLastButtons />}>
                <Datagrid rowClick="show">
                    <TextField source="DepartmentName" label="Department Name" />
                    <NumberField source="SecurityLevel" label="Security Level" />
                    <ReferenceField source="DepartmentId" reference="Department" label="Parent Department">
                        <TextField source="DepartmentName" />
                    </ReferenceField>
                </Datagrid>
            </List>
        </Box>
    );
};

// Department Details Component (for the split view)
const DepartmentDetails = ({ department }) => {
    const [tabValue, setTabValue] = useState(0);
    
    const { data: allDepartments } = useGetList('Department', {
        pagination: { page: 1, perPage: 1000 },
        sort: { field: 'DepartmentName', order: 'ASC' }
    });

    const { data: employees } = useGetList('Employee', {
        filter: { WorksForDepartmentId: department.id },
        pagination: { page: 1, perPage: 100 },
        sort: { field: 'LastName', order: 'ASC' }
    });

    // Filter sub-departments on the client side (fix the ID comparison)
    const subDepartments = allDepartments?.filter(dept => 
        dept.DepartmentId && parseInt(dept.DepartmentId) === parseInt(department.id)
    ) || [];

    // Find parent department if exists (fix the ID comparison)
    const parentDepartment = department.DepartmentId ? 
        allDepartments?.find(dept => parseInt(dept.id) === parseInt(department.DepartmentId)) : null;

    const handleTabChange = (event, newValue) => {
        setTabValue(newValue);
    };

    return (
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            {/* Department Information Header */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Department Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                Department Name
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                                {department.DepartmentName}
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                Security Level
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                                {department.SecurityLevel}
                            </Typography>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                Parent Department
                            </Typography>
                            <Typography variant="body1" sx={{ fontWeight: 'medium' }}>
                                {parentDepartment ? parentDepartment.DepartmentName : 'No Parent'}
                            </Typography>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>

            {/* Tabbed Content */}
            <Box sx={{ flexGrow: 1 }}>
                <Tabs value={tabValue} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <MuiTab label={`Sub-Departments (${subDepartments.length})`} />
                    <MuiTab label={`Employees (${employees?.length || 0})`} />
                </Tabs>
                
                {/* Tab Panels */}
                {tabValue === 0 && (
                    <Box sx={{ p: 2, height: 'calc(100% - 48px)', overflow: 'auto' }}>
                        {subDepartments.length === 0 ? (
                            <Typography variant="body2" color="text.secondary">
                                No sub-departments found
                            </Typography>
                        ) : (
                            <Box>
                                {subDepartments.map(subDept => (
                                    <Paper key={subDept.id} sx={{ p: 2, mb: 1 }}>
                                        <Grid container spacing={2}>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" color="text.secondary">Department Name</Typography>
                                                <Typography variant="body1">{subDept.DepartmentName}</Typography>
                                            </Grid>
                                            <Grid item xs={6}>
                                                <Typography variant="body2" color="text.secondary">Security Level</Typography>
                                                <Typography variant="body1">{subDept.SecurityLevel}</Typography>
                                            </Grid>
                                        </Grid>
                                    </Paper>
                                ))}
                            </Box>
                        )}
                    </Box>
                )}

                {tabValue === 1 && (
                    <Box sx={{ p: 2, height: 'calc(100% - 48px)', overflow: 'auto' }}>
                        {!employees || employees.length === 0 ? (
                            <Typography variant="body2" color="text.secondary">
                                No employees found
                            </Typography>
                        ) : (
                            <EmployeeGrid employees={employees} />
                        )}
                    </Box>
                )}
            </Box>
        </Box>
    );
};

// Employee Grid Component (for displaying employees in table format)
const EmployeeGrid = ({ employees }) => {
    const redirect = useRedirect();

    const handleEmployeeClick = (employee) => {
        redirect(`/Employee/${employee.id}/show`);
    };

    return (
        <Paper sx={{ width: '100%', overflow: 'hidden' }}>
            <Box sx={{ 
                display: 'grid', 
                gridTemplateColumns: '2fr 2fr 1.5fr 1fr', 
                gap: 0,
                '& > div': {
                    p: 1,
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                    borderRight: '1px solid',
                    borderRightColor: 'divider',
                }
            }}>
                {/* Header Row */}
                <Box sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>
                    <Typography variant="body2" color="text.secondary">Name</Typography>
                </Box>
                <Box sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>
                    <Typography variant="body2" color="text.secondary">Title</Typography>
                </Box>
                <Box sx={{ fontWeight: 'bold', bgcolor: 'grey.100' }}>
                    <Typography variant="body2" color="text.secondary">Hire Date</Typography>
                </Box>
                <Box sx={{ fontWeight: 'bold', bgcolor: 'grey.100', borderRight: 'none' }}>
                    <Typography variant="body2" color="text.secondary">Salary</Typography>
                </Box>

                {/* Data Rows */}
                {employees.map(employee => (
                    <React.Fragment key={employee.id}>
                        <Box 
                            sx={{ 
                                cursor: 'pointer',
                                '&:hover': { bgcolor: 'action.hover' },
                                transition: 'background-color 0.2s'
                            }}
                            onClick={() => handleEmployeeClick(employee)}
                        >
                            <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                                {employee.FirstName} {employee.LastName}
                            </Typography>
                        </Box>
                        <Box 
                            sx={{ 
                                cursor: 'pointer',
                                '&:hover': { bgcolor: 'action.hover' },
                                transition: 'background-color 0.2s'
                            }}
                            onClick={() => handleEmployeeClick(employee)}
                        >
                            <Typography variant="body2">
                                {employee.Title || 'N/A'}
                            </Typography>
                        </Box>
                        <Box 
                            sx={{ 
                                cursor: 'pointer',
                                '&:hover': { bgcolor: 'action.hover' },
                                transition: 'background-color 0.2s'
                            }}
                            onClick={() => handleEmployeeClick(employee)}
                        >
                            <Typography variant="body2">
                                {employee.HireDate ? new Date(employee.HireDate).toLocaleDateString() : 'N/A'}
                            </Typography>
                        </Box>
                        <Box 
                            sx={{ 
                                cursor: 'pointer',
                                '&:hover': { bgcolor: 'action.hover' },
                                transition: 'background-color 0.2s',
                                borderRight: 'none'
                            }}
                            onClick={() => handleEmployeeClick(employee)}
                        >
                            <Typography variant="body2">
                                {employee.Salary ? `$${employee.Salary.toLocaleString()}` : 'N/A'}
                            </Typography>
                        </Box>
                    </React.Fragment>
                ))}
            </Box>
        </Paper>
    );
};

// Department Show
export const DepartmentShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Department Information
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Department Name">
                                <TextField source="DepartmentName" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Security Level">
                                <NumberField source="SecurityLevel" />
                            </Labeled>
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ p: 1 }}>
                            <Labeled label="Parent Department">
                                <ReferenceField source="DepartmentId" reference="Department" emptyText="No Parent">
                                    <TextField source="DepartmentName" />
                                </ReferenceField>
                            </Labeled>
                        </Box>
                    </Grid>
                </Grid>
                <Divider sx={{ my: 2 }} />
            </Box>
            
            {/* Sub-Departments */}
            <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 2 }}>Sub-Departments</Typography>
                <ReferenceManyField reference="Department" target="DepartmentId" addLabel={false} pagination={<Pagination />}>
                    <Datagrid rowClick="show">
                        <TextField source="DepartmentName" label="Department Name" />
                        <NumberField source="SecurityLevel" label="Security Level" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
                <AddSubDepartmentButton />
            </Box>
            
            {/* Employees */}
            <Box>
                <Typography variant="h6" sx={{ mb: 2 }}>Employee List</Typography>
                <ReferenceManyField reference="Employee" target="OnLoanDepartmentId" addLabel={false} pagination={<Pagination />}>
                    <Datagrid rowClick="show">
                        <TextField source="LastName" label="Last Name" />
                        <TextField source="FirstName" label="First Name" />
                        <DateField source="HireDate" label="Hire Date" />
                        <EditButton />
                        <DeleteButton />
                    </Datagrid>
                </ReferenceManyField>
            </Box>
        </SimpleShowLayout>
    </Show>
);

// Custom Add Sub-Department Button
const AddSubDepartmentButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Department/create?source=${encodeURIComponent(JSON.stringify({ DepartmentId: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add Sub-Department
        </Button>
    );
};

// Custom Add Employee Button
const AddEmployeeButton = () => {
    const record = useRecordContext();
    const redirect = useRedirect();
    
    const handleClick = () => {
        redirect(`/Employee/create?source=${encodeURIComponent(JSON.stringify({ OnLoanDepartmentId: record?.id }))}`);
    };

    return (
        <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleClick}
            sx={{ mt: 2 }}
        >
            Add New Employee
        </Button>
    );
};

// Department Create
export const DepartmentCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Create New Department
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="DepartmentName" label="Department Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="SecurityLevel" label="Security Level" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <ReferenceInput source="DepartmentId" reference="Department" label="Parent Department">
                                <SelectInput optionText="DepartmentName" />
                            </ReferenceInput>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Create>
);

// Department Edit
export const DepartmentEdit = (props) => (
    <Edit {...props} redirect={false}>
        <SimpleForm>
            <Box sx={{ mb: 3 }}>
                <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 'bold' }}>
                    Edit Department
                </Typography>
                <Grid container spacing={3} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <TextInput source="DepartmentName" label="Department Name" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <NumberInput source="SecurityLevel" label="Security Level" fullWidth />
                        </Box>
                    </Grid>
                    <Grid item xs={12} sm={6} md={4}>
                        <Box sx={{ p: 1 }}>
                            <ReferenceInput source="DepartmentId" reference="Department" label="Parent Department">
                                <SelectInput optionText="DepartmentName" />
                            </ReferenceInput>
                        </Box>
                    </Grid>
                </Grid>
            </Box>
        </SimpleForm>
    </Edit>
);

const DepartmentResource = {
    list: DepartmentList,
    show: DepartmentShow,
    create: DepartmentCreate,
    edit: DepartmentEdit,
};

export default DepartmentResource;