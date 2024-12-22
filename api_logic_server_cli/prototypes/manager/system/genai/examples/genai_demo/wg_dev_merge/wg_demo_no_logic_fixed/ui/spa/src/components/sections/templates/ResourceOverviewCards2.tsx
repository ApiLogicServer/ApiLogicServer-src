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
  Grid
} from '@mui/material';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const LandingPage = () => {
  const dataProvider = useDataProvider();
  const [resourceData, setResourceData] = useState({});
  const [dialogData, setDialogData] = useState(null);
  const resourceNames = Object.keys(getConf().resources || {}).filter(resourceName => !resourceName.startsWith('SPA'));
  console.log("Resource Names", resourceNames);
  
  const fetchResources = async () => {
    const requests = resourceNames.map(resourceName => {
      return dataProvider.getList(resourceName, {
        pagination: { page: 1, perPage: 5 },
        meta: { include: ['+all'] }
      });
    });
    const responses = await Promise.all(requests);
    const data = resourceNames.reduce((acc, resourceName, index) => {
      acc[resourceName] = responses[index].data;
      return acc;
    }, {});
    setResourceData(data);
  };

  useEffect(() => {
    fetchResources();
  }, []);

  const handleCardClick = (resourceType, item) => {
    setDialogData({ resourceType, data: item });
  };

  const handleCloseDialog = () => {
    setDialogData(null);
  };

  const renderResourceAttributes = (resourceType, item) => {
    const attributes = {}
    
    for(let [name, value] of Object.entries(item)){

      if(!['id', 'ja_type', 'attributes', 'relationships', 'meta'].includes(name) && typeof value !== 'object' && !Array.isArray(value)){
        attributes[name] = value;
      }
    }
    
    console.log("Resource Attributes", attributes);
    return Object.entries(attributes).map(([name, value]) => (
      <ListItem key={name}>
        <ListItemText primary={`${name}: ${value}`} />
      </ListItem>
    ));
  };

  const renderRelatedResources = (relationships) => {
    if (!relationships) return null;
    return Object.keys(relationships).map(relationshipName => {
      const relationship = relationships[relationshipName];
      if (!relationship.data) return null;
      if (Array.isArray(relationship.data)) {
        return (
          <div key={relationshipName}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              {relationship.data.map(item => (
                <ListItem key={item.id}>
                  <ListItemText primary={item.type} secondary={`ID: ${item.id}`} />
                </ListItem>
              ))}
            </List>
          </div>
        );
      } else {
        return (
          <div key={relationshipName}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              <ListItem>
                <ListItemText primary={relationship.data.type} secondary={`ID: ${relationship.data.id}`} />
              </ListItem>
            </List>
          </div>
        );
      }
    });
  };

  return (
    <div style={{ padding: '16px' }}>
      <Typography variant="h4" gutterBottom>Resource Overview</Typography>
      <Grid container spacing={2}>
        {resourceNames.map(resourceName => (
          (resourceData[resourceName] || []).map(item => (
            <Grid item key={item.id} xs={12} sm={6} md={4} lg={3}>
              <Card>
                <CardActionArea onClick={() => handleCardClick(resourceName, item)}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom>{resourceName}</Typography>
                    <List>
                      {renderResourceAttributes(resourceName, item)}
                    </List>
                  </CardContent>
                </CardActionArea>
              </Card>
            </Grid>
          ))
        ))}
      </Grid>
      <Dialog open={!!dialogData} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>Resource Details</DialogTitle>
        <DialogContent>
          {dialogData && (
            <div>
              <Typography variant="h5" gutterBottom>{dialogData.resourceType}</Typography>
              <List>
                {renderResourceAttributes(dialogData.resourceType, dialogData.data)}
              </List>
              {renderRelatedResources(dialogData.data.relationships)}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LandingPage;