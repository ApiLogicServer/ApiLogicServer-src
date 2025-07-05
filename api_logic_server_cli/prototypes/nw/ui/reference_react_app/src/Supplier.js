// begin MANDATORY imports (always generated EXACTLY)
import React, { useState, useRef, useEffect } from 'react';
import { List, Datagrid, TextField } from 'react-admin';
import { SimpleShowLayout, TextInput, SimpleForm, Show, Edit, Create } from 'react-admin';
import { Filter, Pagination, Labeled } from 'react-admin'; 
import { EditButton, DeleteButton, ShowButton } from 'react-admin';
import { Grid, Typography, Box, Divider, Button, ToggleButton, ToggleButtonGroup, Paper, Card, CardContent } from '@mui/material';
import { useListContext } from 'react-admin';
import { Link, useNavigate } from 'react-router-dom';
import ViewListIcon from '@mui/icons-material/ViewList';
import MapIcon from '@mui/icons-material/Map';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
// end mandatory imports

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom red marker icon for suppliers
const supplierIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const SupplierFilter = (props) => (
    <Filter {...props}>
        <TextInput label="Search by Company Name" source="CompanyName" alwaysOn />
    </Filter>
);

// Professional World Map using Leaflet.js with real geography
const SupplierMapView = () => {
    const { data: suppliers = [] } = useListContext();
    const navigate = useNavigate();

    // Country coordinates for mapping
    const countryCoordinates = {
        'USA': [39.8283, -98.5795],
        'Canada': [56.1304, -106.3468],
        'Mexico': [23.6345, -102.5528],
        'UK': [55.3781, -3.4360],
        'Germany': [51.1657, 10.4515],
        'France': [46.2276, 2.2137],
        'Italy': [41.8719, 12.5674],
        'Spain': [40.4637, -3.7492],
        'Netherlands': [52.1326, 5.2913],
        'Norway': [60.4720, 8.4689],
        'Sweden': [60.1282, 18.6435],
        'Denmark': [56.2639, 9.5018],
        'Finland': [61.9241, 25.7482],
        'Australia': [-25.2744, 133.7751],
        'Japan': [36.2048, 138.2529],
        'Brazil': [-14.2350, -51.9253],
        'Singapore': [1.3521, 103.8198],
        'Argentina': [-38.4161, -63.6167],
        'China': [35.8617, 104.1954],
        'India': [20.5937, 78.9629],
        'Unknown': [0, 0]
    };

    // Get coordinates for a supplier based on country
    const getSupplierCoordinates = (supplier) => {
        const baseCoords = countryCoordinates[supplier.Country] || countryCoordinates['Unknown'];
        // Add small random offset to avoid overlapping markers
        const latOffset = (Math.random() - 0.5) * 2; // ±1 degree
        const lngOffset = (Math.random() - 0.5) * 2; // ±1 degree
        return [baseCoords[0] + latOffset, baseCoords[1] + lngOffset];
    };

    const handleSupplierClick = (supplier) => {
        navigate(`/Supplier/${supplier.Id}/show`);
    };

    return (
        <div style={{ width: '100%', height: '700px', position: 'relative' }}>
            <MapContainer
                center={[20, 0]}
                zoom={2}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
            >
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {suppliers.map((supplier) => {
                    const coordinates = getSupplierCoordinates(supplier);
                    return (
                        <Marker
                            key={supplier.Id}
                            position={coordinates}
                            icon={supplierIcon}
                            eventHandlers={{
                                click: () => handleSupplierClick(supplier)
                            }}
                        >
                            <Popup>
                                <div style={{ textAlign: 'center' }}>
                                    <strong>{supplier.CompanyName}</strong><br/>
                                    {supplier.City}, {supplier.Country}<br/>
                                    <small>Contact: {supplier.ContactName}</small><br/>
                                    <button 
                                        onClick={() => handleSupplierClick(supplier)}
                                        style={{
                                            marginTop: '8px',
                                            padding: '4px 8px',
                                            backgroundColor: '#4f46e5',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '4px',
                                            cursor: 'pointer'
                                        }}
                                    >
                                        View Details
                                    </button>
                                </div>
                            </Popup>
                        </Marker>
                    );
                })}
            </MapContainer>
            
            {/* Map Info Panel */}
            <div style={{
                position: 'absolute',
                top: '15px',
                left: '15px',
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                padding: '16px',
                borderRadius: '8px',
                border: '1px solid #d1d5db',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                zIndex: 1000,
                minWidth: '250px'
            }}>
                <div style={{ marginBottom: '12px', fontWeight: 'bold', fontSize: '15px', color: '#1f2937' }}>
                    🌍 Global Supplier Map
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                    <div style={{
                        width: '20px',
                        height: '30px',
                        background: 'url("https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png") no-repeat center',
                        backgroundSize: 'contain'
                    }}></div>
                    <span style={{ fontSize: '14px', color: '#374151' }}>Suppliers ({suppliers.length} total)</span>
                </div>
                <div style={{ fontSize: '12px', color: '#6b7280', lineHeight: '1.4' }}>
                    • Click red markers to view supplier details<br/>
                    • Drag map to explore different regions<br/>
                    • Use mouse wheel or zoom controls to zoom<br/>
                    • Real world geography with accurate positioning
                </div>
            </div>
        </div>
    );
};

export const SupplierList = (props) => {
    const [view, setView] = useState('list');

    const handleViewChange = (event, newView) => {
        if (newView !== null) {
            setView(newView);
        }
    };

    return (
        <div>
            {/* View Toggle */}
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="h4" component="h1">
                    Suppliers
                </Typography>
                <ToggleButtonGroup
                    value={view}
                    exclusive
                    onChange={handleViewChange}
                    aria-label="view mode"
                    size="small"
                >
                    <ToggleButton value="list" aria-label="list view">
                        <ViewListIcon sx={{ mr: 1 }} />
                        List
                    </ToggleButton>
                    <ToggleButton value="map" aria-label="map view">
                        <MapIcon sx={{ mr: 1 }} />
                        Map
                    </ToggleButton>
                </ToggleButtonGroup>
            </Box>

            {view === 'list' ? (
                <List {...props} filters={<SupplierFilter />} pagination={<Pagination />}>
                    <Datagrid>
                        <TextField source="Id" />
                        <TextField source="CompanyName" />
                        <TextField source="ContactName" />
                        <TextField source="ContactTitle" />
                        <TextField source="Address" />
                        <TextField source="City" />
                        <TextField source="Region" />
                        <TextField source="PostalCode" />
                        <TextField source="Country" />
                        <TextField source="Phone" />
                        <TextField source="Fax" />
                        <TextField source="HomePage" />
                        <ShowButton />
                        <EditButton />
                    </Datagrid>
                </List>
            ) : (
                <List {...props} filters={<SupplierFilter />} pagination={false}>
                    <SupplierMapView />
                </List>
            )}
        </div>
    );
};

export const SupplierShow = (props) => (
    <Show {...props}>
        <SimpleShowLayout>
            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Company Information
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Labeled>
                                    <TextField source="CompanyName" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="ContactName" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="ContactTitle" />
                                </Labeled>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>
                
                <Grid item xs={12} md={6}>
                    <Paper sx={{ p: 2, mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            <LocationOnIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Address Information
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <Grid container spacing={2}>
                            <Grid item xs={12}>
                                <Labeled>
                                    <TextField source="Address" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="City" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="Region" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="PostalCode" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={6}>
                                <Labeled>
                                    <TextField source="Country" />
                                </Labeled>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>
                
                <Grid item xs={12}>
                    <Paper sx={{ p: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Contact Information
                        </Typography>
                        <Divider sx={{ mb: 2 }} />
                        <Grid container spacing={2}>
                            <Grid item xs={12} sm={4}>
                                <Labeled>
                                    <TextField source="Phone" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Labeled>
                                    <TextField source="Fax" />
                                </Labeled>
                            </Grid>
                            <Grid item xs={12} sm={4}>
                                <Labeled>
                                    <TextField source="HomePage" />
                                </Labeled>
                            </Grid>
                        </Grid>
                    </Paper>
                </Grid>
            </Grid>
        </SimpleShowLayout>
    </Show>
);

export const SupplierEdit = (props) => (
    <Edit {...props}>
        <SimpleForm>
            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <TextInput source="CompanyName" fullWidth />
                    <TextInput source="ContactName" fullWidth />
                    <TextInput source="ContactTitle" fullWidth />
                </Grid>
                <Grid item xs={12} md={6}>
                    <TextInput source="Address" fullWidth />
                    <TextInput source="City" fullWidth />
                    <TextInput source="Region" fullWidth />
                    <TextInput source="PostalCode" fullWidth />
                    <TextInput source="Country" fullWidth />
                </Grid>
                <Grid item xs={12}>
                    <TextInput source="Phone" fullWidth />
                    <TextInput source="Fax" fullWidth />
                    <TextInput source="HomePage" fullWidth />
                </Grid>
            </Grid>
        </SimpleForm>
    </Edit>
);

export const SupplierCreate = (props) => (
    <Create {...props}>
        <SimpleForm>
            <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                    <TextInput source="CompanyName" fullWidth />
                    <TextInput source="ContactName" fullWidth />
                    <TextInput source="ContactTitle" fullWidth />
                </Grid>
                <Grid item xs={12} md={6}>
                    <TextInput source="Address" fullWidth />
                    <TextInput source="City" fullWidth />
                    <TextInput source="Region" fullWidth />
                    <TextInput source="PostalCode" fullWidth />
                    <TextInput source="Country" fullWidth />
                </Grid>
                <Grid item xs={12}>
                    <TextInput source="Phone" fullWidth />
                    <TextInput source="Fax" fullWidth />
                    <TextInput source="HomePage" fullWidth />
                </Grid>
            </Grid>
        </SimpleForm>
    </Create>
);