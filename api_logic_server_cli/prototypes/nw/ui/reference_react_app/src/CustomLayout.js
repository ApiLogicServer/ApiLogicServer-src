import React from 'react';
import { Layout, AppBar } from 'react-admin';
import { Typography } from '@mui/material';

const CustomAppBar = (props) => (
    <AppBar {...props}>
        <Typography variant="h6" color="inherit" sx={{ flex: 1 }}>
            API Logic Server - Northwind Sample
        </Typography>
    </AppBar>
);

const CustomLayout = (props) => (
    <Layout 
        {...props} 
        appBar={CustomAppBar}
    />
);

export default CustomLayout;
