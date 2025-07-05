import React from 'react';
import { 
    Card, 
    CardContent, 
    Typography, 
    Box, 
    Grid, 
    Paper,
    List,
    ListItem,
    ListItemText,
    Chip
} from '@mui/material';

const LandingPage = () => {
    return (
        <Box sx={{ p: 3 }}>
            {/* Dashboard iframe at the top */}
            <Card sx={{ mb: 4 }}>
                <CardContent>
                    <Typography variant="h5" gutterBottom>
                        Dashboard Overview
                    </Typography>
                    <Box sx={{ 
                        border: '1px solid #ddd', 
                        borderRadius: 1,
                        overflow: 'hidden',
                        height: 250
                    }}>
                        <iframe 
                            id="iframeTargetDashboard" 
                            src="http://localhost:5656/dashboard" 
                            style={{
                                flex: 1,
                                border: 'none',
                                width: '100%',
                                height: '100%'
                            }}
                            title="API Logic Server Dashboard"
                        />
                    </Box>
                </CardContent>
            </Card>

            {/* Architecture Overview */}
            <Typography variant="h3" component="h1" gutterBottom align="center" sx={{ mb: 4 }}>
                GenAI-Logic Architecture
            </Typography>

            <Typography variant="h6" paragraph align="center" sx={{ mb: 4, color: 'text.secondary' }}>
                Complete Microservice Automation - From Database to Running System
            </Typography>

            {/* Key Features Grid */}
            <Grid container spacing={3} sx={{ mb: 4 }}>
                <Grid item xs={12} md={6} lg={3}>
                    <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                        <Typography variant="h2" sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}>
                            🔌
                        </Typography>
                        <Typography variant="h6" gutterBottom>
                            Self-Serve API
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            JSON:API with filtering, sorting, pagination, and related data access
                        </Typography>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                        <Typography variant="h2" sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}>
                            📊
                        </Typography>
                        <Typography variant="h6" gutterBottom>
                            Admin App
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Multi-page, multi-table with automatic joins for business collaboration
                        </Typography>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                        <Typography variant="h2" sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}>
                            ⚡
                        </Typography>
                        <Typography variant="h6" gutterBottom>
                            Business Logic
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Spreadsheet-like rules for multi-table derivations and constraints
                        </Typography>
                    </Paper>
                </Grid>

                <Grid item xs={12} md={6} lg={3}>
                    <Paper sx={{ p: 3, textAlign: 'center', height: '100%' }}>
                        <Typography variant="h2" sx={{ fontSize: 48, color: 'primary.main', mb: 2 }}>
                            🔐
                        </Typography>
                        <Typography variant="h6" gutterBottom>
                            Security
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                            Authentication and row-level authorization with role-based access
                        </Typography>
                    </Paper>
                </Grid>
            </Grid>

            {/* Architecture Layers */}
            <Grid container spacing={3}>
                <Grid item xs={12} lg={8}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                Architecture Layers
                            </Typography>
                            
                            <Box sx={{ mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    🗄️ Data Layer
                                </Typography>
                                <Typography variant="body2" paragraph>
                                    SQLAlchemy models automatically created from your database schema.
                                    Supports SQLite, PostgreSQL, MySQL, SQL Server, Oracle and more.
                                </Typography>
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    ⚡ Logic Layer
                                </Typography>
                                <Typography variant="body2" paragraph>
                                    Declarative business rules that are 40X more concise than code.
                                    Automatic dependency ordering and optimization.  Extensible with Python.
                                </Typography>
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    🔌 API Layer
                                </Typography>
                                <Typography variant="body2" paragraph>
                                    REST and JSON:API endpoints with Swagger documentation.
                                    Self-serve capabilities for ad-hoc integration.
                                </Typography>
                            </Box>

                            <Box sx={{ mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    📊 UI Layer
                                </Typography>
                                <Typography variant="body2" paragraph>
                                    Multi-page Admin App with automatic joins and responsive design.
                                    React-based reference implementation included.
                                </Typography>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>

                <Grid item xs={12} lg={4}>
                    <Card>
                        <CardContent>
                            <Typography variant="h5" gutterBottom>
                                Key Benefits
                            </Typography>
                            
                            <List dense>
                                <ListItem>
                                    <ListItemText 
                                        primary="⚡ Instant Working Software"
                                        secondary="From database to running system in minutes"
                                    />
                                </ListItem>
                                
                                <ListItem>
                                    <ListItemText 
                                        primary="🔧 Fully Customizable"
                                        secondary="Extensible with Python, React, and standard tools"
                                    />
                                </ListItem>
                                
                                <ListItem>
                                    <ListItemText 
                                        primary="🔗 Integration Ready"
                                        secondary="B2B APIs, messaging, and microservice patterns"
                                    />
                                </ListItem>
                            </List>

                            <Box sx={{ mt: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Technologies
                                </Typography>
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                                    <Chip label="Python" size="small" />
                                    <Chip label="SQLAlchemy" size="small" />
                                    <Chip label="Flask" size="small" />
                                    <Chip label="React" size="small" />
                                    <Chip label="Material-UI" size="small" />
                                    <Chip label="JSON:API" size="small" />
                                    <Chip label="Swagger" size="small" />
                                </Box>
                            </Box>
                        </CardContent>
                    </Card>
                </Grid>
            </Grid>

            {/* Quick Links */}
            <Card sx={{ mt: 4 }}>
                <CardContent>
                    <Typography variant="h5" gutterBottom>
                        Quick Links
                    </Typography>
                    <Grid container spacing={2}>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h6">
                                    <a href="http://localhost:5656/" target="_blank" rel="noopener noreferrer">
                                        Admin App
                                    </a>
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Multi-page business user interface
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h6">
                                    <a href="http://localhost:5656/api" target="_blank" rel="noopener noreferrer">
                                        API Explorer
                                    </a>
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Swagger documentation and testing
                                </Typography>
                            </Box>
                        </Grid>
                        <Grid item xs={12} sm={6} md={3}>
                            <Box sx={{ textAlign: 'center' }}>
                                <Typography variant="h6">
                                    <a href="https://apilogicserver.github.io/Docs/" target="_blank" rel="noopener noreferrer">
                                        Documentation
                                    </a>
                                </Typography>
                                <Typography variant="body2" color="text.secondary">
                                    Complete guides and tutorials
                                </Typography>
                            </Box>
                        </Grid>
                    </Grid>
                </CardContent>
            </Card>
        </Box>
    );
};

export default LandingPage;
