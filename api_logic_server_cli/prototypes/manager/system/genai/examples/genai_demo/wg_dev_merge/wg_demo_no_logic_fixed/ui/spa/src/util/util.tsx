import { useRoutes } from 'react-router-dom';
import { Box, CircularProgress, Typography } from '@mui/material';

const listRoutes = (routes, basePath = '') => {
    routes.forEach(route => {
        const fullPath = `${basePath}${route.path}`;
        console.log(fullPath);

        if (route.children) {
            listRoutes(route.children, fullPath);
        }
    });
};


export const getAppId = () => {
    const hash = window.location.hash;
    let appId = sessionStorage.getItem('appId') || localStorage.getItem('appId') || '';
    if (hash.includes('?')) {
        const queryString = hash.split('?')[1];
        const params = new URLSearchParams(queryString);
        appId = params.get("appId") || appId;
    }
    return appId;
}


export const setAppId = (appId: string) => {
    sessionStorage.setItem('appId', appId)
    localStorage.setItem('appId', appId)
}


export const Loading = () => {
    return (
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" height="100vh">
            <CircularProgress />
            <Typography variant="h6" style={{ marginTop: '20px' }}>
                Loading...
            </Typography>
        </Box>
    );
}

