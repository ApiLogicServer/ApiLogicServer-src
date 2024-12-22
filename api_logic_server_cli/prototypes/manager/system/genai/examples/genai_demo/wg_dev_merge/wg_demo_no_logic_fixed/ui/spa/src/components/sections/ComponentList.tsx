import React, { useState, useEffect } from 'react';
import { Button, List, ListItem, ListItemText, Typography, Box, Grid, CircularProgress } from '@mui/material';
import { useDataProvider } from 'react-admin';
import { useAppContext } from '../../AppProvider';
import { useRefresh } from 'react-admin';
import Notify from '../../util/Notify';

const ComponentList = ({type}: {type: string}) => {
    /*
    type can be either "prompt" or "template"
    */
    const dataProvider = useDataProvider();
    const [items, setItems] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const { appVersion, setAppVersion } = useAppContext() || {};
    const [ log, setLog ] = useState('');
    const [ showLog, setShowLog ] = useState(false);
    const refresh = useRefresh();

    const fetchData = () => {
        setLoading(true);
        dataProvider.getList("SPAComponent", {
            pagination: { page: 1, perPage: 100 },
            filter: { 'Type': type }
        })
        .then(response => {
            setItems(response?.data || []);
            setLoading(false);
        })
        .catch(error => {
            console.error("Error fetching page:", error);
            setLoading(false);
        });
    };

    useEffect(() => {
        fetchData();
    }, []);

    const doShowLog = (message) => {
        setLog(message);
        setShowLog(true);
        setTimeout(() => {
            setShowLog(false);
        }, 1000);
    }

    const handleApplyClick = (item) => {
        console.log('Applying update:', item);
        dataProvider.execute('SPAComponent', 'apply', { id: item.id })
        .then(() => {
            setAppVersion && setAppVersion((appVersion || 0) +1);
            console.log('Update applied:', appVersion, item);
            refresh();
            doShowLog('Update applied');
        })
        .catch(error => {
            console.error('Error applying update:', error);
            alert('Error applying update');
        });
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${date.getMonth() + 1}/${date.getDate()} ${hours}:${minutes}`;
    };

    if(loading) {
        return <CircularProgress />;
    }

    if(!items?.length) {
        return <Typography>No {type}s found</Typography>;
    }

    return (
        <div>
            { showLog && <Notify open={showLog} message={log} />}
            
            <List>
                {items.map(item => (
                    <ListItem key={item.id} sx={{ borderBottom: '1px solid #ddd' }}>
                        <Grid container spacing={2} alignItems="center">
                            <Grid item xs>
                                <ListItemText
                                    secondary={
                                        <>
                                            <Typography variant="body2">
                                                {type === "prompt" ? item.prompt : item.name}
                                            </Typography>
                                            <Typography variant="caption" color="textSecondary" sx={{ color: "#ccc" }}>
                                                {formatDate(item.created_at)}
                                            </Typography>
                                        </>
                                    }
                                />
                            </Grid>
                            <Grid item>
                                <Button
                                    disabled={item.code ? false : true}
                                    variant="outlined"
                                    onClick={() => handleApplyClick(item)}
                                    sx={{ width: '6em' }} // Set a fixed width for the button
                                >
                                    Apply
                                </Button>
                                
                            </Grid>
                        </Grid>
                    </ListItem>
                ))}
            </List>
           
        </div>
    );
}

export default ComponentList;