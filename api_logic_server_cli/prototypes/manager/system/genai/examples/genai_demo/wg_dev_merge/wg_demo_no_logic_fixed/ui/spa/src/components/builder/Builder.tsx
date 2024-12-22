import React, { useEffect, useState } from 'react';
import { Box, Container, Toolbar, Typography, TextField, Button } from '@mui/material';
import { MenuItem, FormControl, Select, InputLabel, Paper } from '@mui/material';
import { styled } from '@mui/system';
import { useConf } from '../../Config.ts';
import { useDataProvider } from 'react-admin';
import { LiveProvider, LiveEditor, LivePreview } from "react-live";

// const LodgingComponent = ({ data }) => {
//     return <Container>
//             <Paper style={{ padding: 16, marginBottom: 16 }}>
//                 <Typography variant="h4">{data.name}</Typography>
//                 <Typography variant="subtitle1">Type: {data.ja_type}</Typography>
//                 <Typography variant="body1">Capacity: {data.capacity}</Typography>
//                 <Typography variant="body1">Town: {data.town.name}</Typography>
//                 <Typography variant="body2">Location: {data.town.location}</Typography>
//             </Paper>
//         </Container>

// };

// const SupplierOrderComponent = ({ data }) => {
//     return (
//         <Container>
//             <Paper style={{ padding: 16, marginBottom: 16 }}>
//                 <Typography variant="h4">Order Details</Typography>
//                 <Typography variant="subtitle1">Order ID: {data.id}</Typography>
//                 <Typography variant="subtitle1">Order Type: {data.ja_type}</Typography>
//                 <Typography variant="subtitle1">Order Date: {data.order_date}</Typography>
//                 <Typography variant="subtitle1">Quantity Ordered: {data.quantity_ordered}</Typography>
                
//                 <Typography variant="h5" style={{ marginTop: 16 }}>Ingredient Details</Typography>
//                 <Typography variant="subtitle1">Ingredient ID: {data.ingredient.id}</Typography>
//                 <Typography variant="subtitle1">Ingredient Name: {data.ingredient.name}</Typography>
                
//                 <Typography variant="h5" style={{ marginTop: 16 }}>Supplier Details</Typography>
//                 <Typography variant="subtitle1">Supplier ID: {data.supplier.id}</Typography>
//                 <Typography variant="subtitle1">Supplier Name: {data.supplier.name}</Typography>
//                 <Typography variant="subtitle1">Supplier Contact: {data.supplier.contact_info}</Typography>
//             </Paper>
//         </Container>
//     );
// };

const SectionBox = styled(Box)(({ theme }) => ({
    my: theme.spacing(4),
    minHeight: '80vh',
}));


const GenericSection = ({ resourceName }: {  resourceName: string }) => {

    const dataProvider = useDataProvider();
    const conf = useConf();
    const [ items, setItems ] = useState<any[]>([]);

    useEffect(() => {
        dataProvider.getList(resourceName, {
            pagination: { page: 1, perPage: 100 }
        })
        .then(response => {
            setItems(response?.data || [] );
            
        })
        .catch(error => {
            console.error("Error fetching page:", error);
        });
    },[resourceName])

    if(!conf.resources){
        return <span>No resources</span>
    }

    console.log("Resource", resourceName);
    console.log("Items", items);
    const label = conf.resources[resourceName].user_key || resourceName;

    return (
      <SectionBox>
        <Typography variant="h6">{resourceName}</Typography>
        {items.map((item: any) => (
            <Typography key={item.id} variant="body1">
                <b>{item[label] || item.name || item.id}</b>
                <code>{JSON.stringify(item, null,4)}</code>
                
            </Typography>
        ))} 
        
      </SectionBox>
    );
};


const ResourceSelector = ({ setSelectedResource }: { setSelectedResource: any }) => {
    const conf = useConf();
    const [resourceName, setResourceName] = React.useState('');
    const [templateName, setTemplateName] = React.useState('');
    const resources = conf.resources || {};
    const resourceNames = Object.entries(resources).filter(([key, value]) => !value.hidden).map(([key, value]) => key);
    const templateNames = [ "Gallery", "List", "Tiles", "Table", "Form", "Markdown" ];

    const handleChangeResource = (event: { target: { value: React.SetStateAction<string>; }; }) => {
        setSelectedResource(event.target.value);
        setResourceName(event.target.value);
    };

    const handleChangeTemplate = (event: { target: { value: React.SetStateAction<string>; }; }) => {
        //setSelectedResource(event.target.value);
        setTemplateName(event.target.value);
    };

    return <>
        <FormControl variant="outlined" sx={{width: "20em"}}>

            <InputLabel id="resource-select-label">Resource</InputLabel>
            <Select
                labelId="resource-select-label"
                id="resource-select"
                value={resourceName}
                onChange={handleChangeResource}
                label="Resource"
            >
                {resourceNames.map((name, index) => (
                    <MenuItem key={index} value={name}>
                        {name}
                    </MenuItem>
                ))}
            </Select>
        </FormControl>

        <FormControl variant="outlined" sx={{width: "20em", paddingLeft: "1em"}}>
            <InputLabel id="Template-select-label">Template</InputLabel>
            <Select
                labelId="Template-select-label"
                id="template-select"
                value={templateName}
                onChange={handleChangeTemplate}
                label="Resource"
            >
                {templateNames.map((name, index) => (
                    <MenuItem key={index} value={name}>
                        {name}
                    </MenuItem>
                ))}
            </Select>

        </FormControl>
        </>

}

const Builder = () => {

    const [ selectedResource, setSelectedResource ] = useState<string | null>(null);
    
    return <>
        <ResourceSelector setSelectedResource={setSelectedResource}  />
        <hr/>
        {
            selectedResource && <GenericSection resourceName={selectedResource}/>
        }
        <hr/>
        <Button variant="outlined" onClick={() => alert('TBD')}>Save Section</Button>
        </>
}

export default Builder;
