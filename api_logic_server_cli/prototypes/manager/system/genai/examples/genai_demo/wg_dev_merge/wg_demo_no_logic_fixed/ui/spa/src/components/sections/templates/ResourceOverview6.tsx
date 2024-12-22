import React, { useState, useEffect } from 'react';
import {
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  List,
  ListItem,
  ListItemText,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Box,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useDataProvider } from 'react-admin';
import { getConf } from '../../Config';

const ResourceTable = () => {
  const dataProvider = useDataProvider();
  const [resourceData, setResourceData] = useState({});
  const [dialogData, setDialogData] = useState(null);
  const resourceNames = Object.keys(getConf().resources || {}).filter(
    resourceName => !resourceName.startsWith('SPA')
  );
  
  const fetchResources = async () => {
    const requests = resourceNames.map(resourceName => {
      return dataProvider.getList(resourceName, {
        pagination: { page: 1, perPage: 5 },
        meta: { include: ['+all'] },
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
  }, [dataProvider]);

  const handleRowClick = (resourceType, item) => {
    setDialogData({ resourceType, data: item });
  };

  const handleCloseDialog = () => {
    setDialogData(null);
  };

  const renderResourceAttributes = (item) => {
    const attributes = {};
    for (let [name, value] of Object.entries(item)) {
      if (!['id', 'ja_type', 'attributes', 'relationships', 'meta', 'type'].includes(name) && typeof value !== 'object' && !Array.isArray(value)) {
        attributes[name] = value;
      }
    }
    return attributes;
  };

  const renderRelatedResources = (relationships) => {
    if (!relationships) return null;
    return Object.keys(relationships).map(relationshipName => {
      const relationship = relationships[relationshipName];
      if (!relationship.data) return null;
      if (Array.isArray(relationship.data)) {
        return (
          <div key={relationshipName} style={{ marginTop: '16px' }}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              {relationship.data.map(item => (
                <ListItem key={item.id}>
                  <ListItemText primary={`ID: ${item.id} (Referenced)`} />
                </ListItem>
              ))}
            </List>
          </div>
        );
      } else {
        return (
          <div key={relationshipName} style={{ marginTop: '16px' }}>
            <Typography variant="h6" gutterBottom>{relationshipName}</Typography>
            <List>
              <ListItem>
                <ListItemText primary={`ID: ${relationship.data.id} (Referenced)`} />
              </ListItem>
            </List>
          </div>
        );
      }
    });
  };

  console.log('resource render')
  return (
    <div style={{ padding: '16px' }}>
      <Typography variant="h4" gutterBottom>Resource Overview</Typography>
      {resourceNames.map(resourceName => (
        <Accordion key={resourceName}>
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            aria-controls={`${resourceName}-content`}
            id={`${resourceName}-header`}
          >
            <Typography variant="h6">{resourceName}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper} style={{ border: '1px solid #ccc' }}>
              <Table style={{ cursor: 'pointer' }}>
                <TableHead>
                  <TableRow>
                    {resourceData[resourceName] &&
                      resourceData[resourceName].length > 0 &&
                      Object.keys(renderResourceAttributes(resourceData[resourceName][0])).map(attr => (
                        <TableCell key={attr}>{attr}</TableCell>
                      ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {resourceData[resourceName]?.map(item => (
                    <TableRow key={item.id} onClick={() => handleRowClick(resourceName, item)}>
                      {Object.values(renderResourceAttributes(item)).map((value, index) => (
                        <TableCell key={index}>{value}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      ))}
      <Dialog open={!!dialogData} onClose={handleCloseDialog} fullWidth maxWidth="md">
        <DialogTitle>Resource Details</DialogTitle>
        <DialogContent>
          {dialogData && (
            <div>
              <Typography variant="h5" gutterBottom>{dialogData.resourceType}</Typography>
              <List>
                {Object.entries(renderResourceAttributes(dialogData.data)).map(([name, value]) => (
                  <ListItem key={name}>
                    <ListItemText primary={`${name}: ${value}`} />
                  </ListItem>
                ))}
              </List>
              {renderRelatedResources(dialogData.data.relationships)}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ResourceTable;
