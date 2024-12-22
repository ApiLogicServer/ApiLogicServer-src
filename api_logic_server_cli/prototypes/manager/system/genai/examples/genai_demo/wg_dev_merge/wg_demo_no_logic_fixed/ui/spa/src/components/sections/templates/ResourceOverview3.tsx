import React, { useState } from 'react';
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, List, ListItem, ListItemText } from '@mui/material';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const ResourceList = () => {
    const dataProvider = useDataProvider();
    const [dialogOpen, setDialogOpen] = useState(false);
    const [selectedResource, setSelectedResource] = useState(null);
    const [relatedData, setRelatedData] = useState({});

    const handleItemClick = async (resourceName, id) => {
        try {
            const response = await dataProvider.getOne(resourceName, {
                id,
                meta: { include: ['+all'] },
            });
            setSelectedResource(response.data);
            setRelatedData(response.included || {});
            setDialogOpen(true);
        } catch (error) {
            console.error('Error fetching resource:', error);
        }
    };

    const handleDialogClose = () => {
        setDialogOpen(false);
        setSelectedResource(null);
        setRelatedData({});
    };

    const renderRelated = (related) => {
        return related.map(item => (
            <div key={item.id}>
                <p><strong>{item.attributes.name || item.attributes.description}</strong></p>
                {/* Add more attributes as needed */}
            </div>
        ));
    };

    // Example static data; replace with dynamic data fetching and mapping
    const conf = getConf();
    const resources = Object.keys(conf.resources).filter(
        (key) => !['SPAPage', 'SPASection','SPAComponent'].includes(key)
    );

    return (
        <div>
            <List>
                {resources.map(resourceName => (
                    <ListItem key={resourceName} button onClick={() => handleItemClick(resourceName, '1')}>
                        <ListItemText primary={resourceName} />
                    </ListItem>
                ))}
            </List>

            <Dialog open={dialogOpen} onClose={handleDialogClose}>
                <DialogTitle>{selectedResource?.attributes?.name || 'Resource Details'}</DialogTitle>
                <DialogContent>
                    {selectedResource && (
                        <div>
                            <p><strong>Description:</strong> {selectedResource.attributes.description}</p>
                            {Object.entries(relatedData).map(([key, value]) => (
                                <div key={key}>
                                    <h4>{key}</h4>
                                    {renderRelated(value)}
                                </div>
                            ))}
                        </div>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleDialogClose} color="primary">
                        Close
                    </Button>
                </DialogActions>
            </Dialog>
        </div>
    );
};

export default ResourceList;
