import React, { useEffect, useState } from 'react';
import { Container, CircularProgress } from '@mui/material';
import HighLight from './sections/HighLight.tsx';
import AIQuery from './aiWebdev/AIQuery.tsx';
import SpApp from './SpApp.tsx';
import ErrorBoundary from './ErrorBoundary';
import { AppProvider, useAppContext } from '../AppProvider';
import { clearSpa } from '../Config.ts';

const Layout = () => {
    const [loading, setLoading] = useState(true);
    const hash = document.location.hash;

    useEffect(() => {
        const timer = setTimeout(() => {
            setLoading(false);
        }, 2000);

        return () => clearTimeout(timer);
    }, []);

    if (hash.startsWith("#/dev")) {
        return (
            <AppProvider>
                <Container 
                    id={"main"} 
                    sx={{ margin: '0px', width: "100%", verticalAlign : "top", 
                            position: 'absolute', top: 0, left: 0, 
                            border: "1px solid none"}} 
                    maxWidth={"xl"}>
                
                    <AIQuery />
                    <ErrorBoundary>
                        <HighLight />
                    </ErrorBoundary>
                </Container>
            </AppProvider>
        );
    }

    if (sessionStorage.getItem('raSpa') === 'true' || document.location.pathname.includes('/spa-dev')) {
        return <SpApp />;
    }

    return (
        <>
            {loading ? <CircularProgress /> : <NoSpa />}
        </>
    );
};

const NoSpa = () => {

    const [ msg, setMsg ] = useState<any>( <CircularProgress />);
    useEffect(() => {
        clearSpa();
        document.location.href = document.location.href.split('#')[0];
        setTimeout(() => {
            setMsg('No SPA, Redirecting to main page...');
        }, 1000);
    }, []);

    return <>{msg}</>
}

export default Layout;