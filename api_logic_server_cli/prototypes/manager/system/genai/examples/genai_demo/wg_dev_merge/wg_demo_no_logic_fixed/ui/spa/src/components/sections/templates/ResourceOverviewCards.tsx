import React, { useState, useEffect } from 'react';
import {
  Typography,
  Card,
  CardContent,
  CardActionArea,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Grid,
  Button
} from '@mui/material';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const RelatedDataInstance = ({ relatedData }) => {
    const conf = getConf();
    const resource = conf.resources && conf.resources[relatedData.type];
    if (!resource) return null;

    return (
        <List>
            {resource.attributes
                .filter(attr => relatedData[attr.name] != null)
                .map(attr => (
                    <ListItem key={attr.name}>
                        <ListItemText primary={`${attr.label || attr.name}: ${relatedData[attr.name]}`} />
                    </ListItem>
                ))}
        </List>
    );
};

const ResourceDialog = ({ open, onClose, resourceData }) => {
    const conf = getConf();
    const resourceConf = conf.resources && conf.resources[resourceData.type];
    if (!resourceConf) return null;

    const { attributes, tab_groups: tabGroups } = resourceConf;

    const attributeItems = attributes
        .filter(attr => resourceData[attr.name] != null)
        .map(attr => (
            <ListItem key={attr.name}>
                <ListItemText primary={`${attr.label || attr.name}: ${resourceData[attr.name]}`} />
            </ListItem>
        ));

    const relatedItems = (tabGroups || []).map(({ name }) => {
        const relatedData = resourceData[name];
        if (!relatedData) return null;

        if (Array.isArray(relatedData)) {
            return (
                <div key={name}>
                    <Typography variant="subtitle1">{name}</Typography>
                    <List>
                        {relatedData.map(item => (
                            <RelatedDataInstance key={item.id} relatedData={item} />
                        ))}
                    </List>
                </div>
            );
        }
        return (
            <div key={name}>
                <Typography variant="subtitle1">{name}</Typography>
                <RelatedDataInstance relatedData={relatedData} />
            </div>
        );
    });

    return (
        <Dialog open={open} onClose={onClose} fullWidth>
            <DialogTitle>{resourceData.name || 'Resource Details'}</DialogTitle>
            <DialogContent>
                <Typography variant="h6">Attributes</Typography>
                <List>{attributeItems}</List>
                <Typography variant="h6">Related Resources</Typography>
                {relatedItems}
            </DialogContent>
        </Dialog>
    );
};

const LandingPage = () => {
    const dataProvider = useDataProvider();
    const [resources, setResources] = useState([]);
    const [dialogData, setDialogData] = useState(null);

    useEffect(() => {
        const fetchResources = async () => {
            const conf = getConf();
            const resourceNames = Object.keys(conf.resources);
            const fetchData = resourceNames.map(name =>
                dataProvider.getList(name, {
                    pagination: { page: 1, perPage: 5 },
                    meta: { include: ['+all'] }
                })
            );
            const results = await Promise.all(fetchData);
            const resourceMap = resourceNames.reduce((acc, name, index) => {
                acc[name] = results[index].data;
                return acc;
            }, {});
            setResources(resourceMap);
        };
        fetchResources();
    }, [dataProvider]);

    const openDialog = (resourceType, data) => {
        setDialogData({ resourceType, data });
    };

    const closeDialog = () => {
        setDialogData(null);
    };

    return (
        <div style={{ padding: '16px' }}>
            <Typography variant="h4" gutterBottom>
                Resource Overview
            </Typography>
            <Grid container spacing={2} direction="column">
                {Object.entries(resources).map(([resourceType, resourceData]) => (
                    <>
                    <Grid item xs={12} sm={6} md={4} key={resourceType}>
                        
                        <Typography variant="h5" gutterBottom>
                        {resourceType}
                        </Typography>
                        
                        {resourceData.map(data => (
                            <Card key={data.id}>
                                <CardActionArea onClick={() => openDialog(resourceType, data)}>
                                    <CardContent>
                                        <Typography variant="h6" gutterBottom>
                                            {data.name || `ID: ${data.id}`}
                                        </Typography>
                                        <List>
                                            {Object.entries(data)
                                                .filter(([key]) => !['id', 'ja_type', 'attributes', 'relationships', 'meta'].includes(key) && typeof data[key] !== 'object')
                                                .map(([key, value]) => (
                                                    <ListItem key={key}>
                                                        <ListItemText primary={`${key}: ${value}`} />
                                                    </ListItem>
                                                ))}
                                        </List>
                                    </CardContent>
                                </CardActionArea>
                            </Card>
                        ))}
                    </Grid>
                    </>
                )
                )}
            </Grid>
            {dialogData && (
                <ResourceDialog open={!!dialogData} onClose={closeDialog} resourceData={dialogData.data} />
            )}
        </div>
    );
};

export default LandingPage;