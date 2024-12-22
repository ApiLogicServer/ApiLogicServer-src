import React, { useState, useEffect } from 'react';
import { Backdrop, CircularProgress, Dialog, DialogActions, DialogContent, DialogTitle, TextField, Button, List, ListItem, ListItemText } from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { loadConf, clearSpa } from '../Config.ts';
import { getAppId, setAppId, Loading } from '../util/util.tsx';
import { jsonapiClient } from '../rav4-jsonapi-client/ra-jsonapi-client.ts';
import { Admin, Resource, Datagrid, TextField as RaTextField, useDataProvider } from 'react-admin';

interface Project {
    id: any;
    name: any;
    running: any;
}

const ProjectList = ({ projects }: { projects: Project[] }) => {
    const dataProvider = useDataProvider();
    const [loading, setLoading] = useState(false);

    const handleSelect = (projectId) => {
        setLoading(true);
        dataProvider.execute('Project', 'run_dev', { id: projectId })
            .then(response => {
                console.log('ProjectSelect:', response.data);
                const appName = projects.find(item => item.id === projectId)?.name;
                if (appName) {
                    sessionStorage.setItem("appName", appName);
                }
                setAppId(projectId);
                document.location.reload();
            })
            .catch(error => {
                console.error('Failed to submit application ID:', error);
            })
            .finally(() => {
                setLoading(false);
            });
    };

    

    const listItemStyle = {
        cursor: 'pointer',
        '&:hover': {
            backgroundColor: 'lightgray',
        },
        padding: '0.1em 1em'
    };

    if (loading) {
        return <Loading />;
    }

    if(projects.length === 0){
        console.log('No projects found');
        clearSpa();
    }

    return <List>
        {projects.map(item => {
            const itemText = (
                <>
                    {item.running ? (
                        <CheckCircleIcon style={{ color: 'green', fontSize: '1em', verticalAlign: 'middle' }} />
                    ) : (
                        <CancelIcon style={{ color: 'black', fontSize: '1em', verticalAlign: 'middle' }} />
                    )}
                    <span style={{ paddingLeft: '0.5em' }}> {item.name}</span>
                </>
            );
            return (
                <ListItem key={item.id} sx={listItemStyle} onClick={() => handleSelect(item.id)}>
                    <ListItemText primary={itemText} />
                </ListItem>
            );
        })}
        {loading && (
            <Backdrop
                sx={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, zIndex: (theme) => theme.zIndex.drawer + 1, color: '#fff' }}
                open={loading}
            >
                <CircularProgress color="inherit" />
            </Backdrop>
        )}
    </List>
}

const ApplicationIdDialog = ({ }) => {
    const [appId, setAppId] = useState('');
    const [projects, setProjects] = useState<{ id: any; name: any }[]>([]);
    const [loading, setLoading] = useState(false);
    const [open, setOpen] = useState(true);
    const dataProvider = useDataProvider();

    const setSaveAppId = (value: string) => {
        setAppId(value);
    };

    const handleDialogClose = (projectId: string) => {
        setSaveAppId(projectId);
        document.location.reload();
    };

    const handleCancel = () => {
        clearSpa();
        document.location.href = document.location.href.split('#')[0];
    };

    useEffect(() => {
        setLoading(true);
        dataProvider.getList('Project', {})
            .then(response => {
                const projects = response.data.map(item => ({
                    id: item.id,
                    running: item.attributes.running,
                    name: item.attributes.name
                }));
                setProjects(projects);
            })
            .catch(error => {
                console.error('Fetch error:', error);
                setLoading(false);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [dataProvider]);

    if (loading) {
        return <Loading />;
    }

    if(!projects?.length){
        return <>No projects found</>
    }

    return (
        <Dialog open={open} onClose={() => handleDialogClose('')}>
            <DialogTitle>Select Project</DialogTitle>
            <DialogContent>
                <TextField
                    autoFocus
                    margin="dense"
                    label="Project Search"
                    type="text"
                    fullWidth
                    value={appId}
                    onChange={(e) => setSaveAppId(e.target.value)}
                />
                <ProjectList projects={projects} />
            </DialogContent>
            <DialogActions>
                <Button onClick={handleDialogClose} color="primary">
                    Close
                </Button>
                <Button onClick={handleCancel} color="secondary">
                    Cancel
                </Button>
            </DialogActions>
        </Dialog>
    );
};

const ApplicationIdDialogApp = () => {
    const [dataProvider, setDataProvider] = useState<any>(null);
    const wg_root = '';
    setAppId('')

    useEffect(() => {
        loadConf('')
        .then((apiUrl) => {
            console.log('API URL', apiUrl);
            if (!apiUrl) {
                throw new Error('Failed to load API URL');
            }
            const dataProvider = jsonapiClient(`${wg_root}/api`, {conf:{}});
            setDataProvider(dataProvider);
        })
        .catch((error) => {
            console.error('ApplicationIdDialogAppError', error);
            clearSpa();
        });
    }, []);

    if (!dataProvider) {
        return <Loading />;
    }

    return (
        <Admin dataProvider={dataProvider} layout={ApplicationIdDialog} disableTelemetry={true}>
            <Resource name="Project" />
        </Admin>
    );
};

export default ApplicationIdDialogApp;