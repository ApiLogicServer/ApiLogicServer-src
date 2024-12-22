import React, { useState, useEffect } from 'react';
import {
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  List,
  ListItem,
  ListItemText,
  Divider,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  TableHead
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
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
          <ListItem key={attr.name} style={{ padding: '4px 0' }}>
            <ListItemText
              primary={<span><strong>{attr.label || attr.name}:</strong> {relatedData[attr.name]}</span>}
            />
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
      <ListItem key={attr.name} style={{ padding: '4px 0' }}>
        <ListItemText
          primary={<span><strong>{attr.label || attr.name}:</strong> {resourceData[attr.name]}</span>}
        />
      </ListItem>
    ));

  const relatedItems = (tabGroups || []).map(({ name }) => {
    const relatedData = resourceData[name];
    if (!relatedData) return null;

    if (Array.isArray(relatedData)) {
      return (
        <div key={name}>
          <Typography variant="subtitle1" style={{ marginTop: '16px' }}>{name}</Typography>
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
        <Typography variant="subtitle1" style={{ marginTop: '16px' }}>{name}</Typography>
        <RelatedDataInstance relatedData={relatedData} />
      </div>
    );
  });

  return (
    <Dialog open={open} onClose={onClose} fullWidth>
      <DialogTitle>{resourceData.name || 'Resource Details'} Details</DialogTitle>
      <DialogContent>
        <List>{attributeItems}</List>
        <Divider style={{ margin: '20px 0' }} />
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
      const resourceNames = Object.keys(conf.resources).filter(name => !name.startsWith('SPA'));
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

  const openDialog = data => {
    setDialogData(data);
  };

  const closeDialog = () => {
    setDialogData(null);
  };

  return (
    <div style={{ padding: '16px' }}>
      <Typography variant="h4" gutterBottom>
        Resource Overview
      </Typography>
      {Object.entries(resources).map(([resourceType, resourceData]) => (
        <Accordion key={resourceType}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}> 
            <Typography variant="h5">{resourceType}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <TableContainer component={Paper}>
              <Table aria-label="resource table">
                <TableHead>
                  <TableRow>
                    {getConf().resources[resourceType].attributes.filter(attr => attr.name !== 'id').map(attr => (
                      <TableCell key={attr.name} style={{ fontWeight: 'bold' }}>{attr.label || attr.name}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {resourceData.map(data => (
                    <TableRow key={data.id} hover onClick={() => openDialog(data)} style={{ cursor: 'pointer' }}>
                      {getConf().resources[resourceType].attributes.filter(attr => attr.name !== 'id').map(attr => (
                        <TableCell key={attr.name}>{data[attr.name] || 'N/A'}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </AccordionDetails>
        </Accordion>
      ))}
      {dialogData && (
        <ResourceDialog open={!!dialogData} onClose={closeDialog} resourceData={dialogData} />
      )}
    </div>
  );
};

export default LandingPage;