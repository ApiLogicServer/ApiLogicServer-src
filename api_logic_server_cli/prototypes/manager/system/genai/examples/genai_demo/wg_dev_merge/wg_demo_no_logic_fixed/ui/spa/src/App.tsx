import React, { useEffect, useState } from 'react';
import { Admin, Resource } from 'react-admin';
import { jsonapiClient } from './rav4-jsonapi-client/ra-jsonapi-client';
import { QueryClient } from 'react-query';
import { loadConf } from './Config';
import Layout from './components/Layout.tsx';
import SpApp from './components/SpApp.tsx';
import ProjectDialog from './components/ProjectDialog.tsx';
import { Loading, getAppId } from './util/util.tsx';

const App = () => {
    const [loading, setLoading] = useState(true);
    const [dataProvider, setDataProvider] = useState<any>(null);
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [appId, setAppId] = useState(getAppId());
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
                refetchOnWindowFocus: false,
            },
        },
    });

    useEffect(() => {
        setLoading(true);
        loadConf()
            .then((apiUrl) => {
                console.log('API URL', apiUrl); // jsonapi url for the backend admin api endpoints
                if(!apiUrl){
                    throw new Error("Failed to load API URL");
                }
                const dataProvider = jsonapiClient(apiUrl, { conf: {} });
                setDataProvider(dataProvider);
            })
            .catch((error) => {
                console.error(error);
                setIsDialogOpen(true);
            })
            .finally(() => {
                setLoading(false);
            });
    }, []);

    if (loading) {
        return <Loading />;
    }

    if(!appId && document.location.origin !== 'g.apifabric.ai' && document.location.href.includes('dev')){
        return (
            <>
                <ProjectDialog />
            </>
        );
    }

    const HighLight = React.lazy(() => import('./components/sections/HighLight.tsx'));

    return (
        <>
            <Admin dataProvider={dataProvider} queryClient={queryClient} layout={Layout} disableTelemetry={true}>
                <Resource name="home" list={SpApp} />
                <Resource name="highlight" list={HighLight} />
            </Admin>
        </>
    );
};

export default App;