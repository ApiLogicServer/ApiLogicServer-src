// import React, { useEffect, useState } from 'react';
// import { Box, Container, Toolbar, Typography, TextField, Button } from '@mui/material';
// import { styled } from '@mui/system';
// //import { useConf } from '../../Config.ts';
// //import { useDataProvider } from 'react-admin';
// import {ISection, IPageData} from '../../interfaces.tsx';
// import { MenuItem, FormControl, Select, InputLabel } from '@mui/material';



// const SectionBox = styled(Box)(({ theme }) => ({
//     my: theme.spacing(4),
//     minHeight: '80vh',
// }));


// const GenericSection = ({ resourceName }: {  resourceName: string }) => {
//     return <></>
//     // const dataProvider = useDataProvider();
//     // const conf = useConf();
//     // const [ items, setItems ] = useState<any[]>([]);

//     // useEffect(() => {
//     //     dataProvider.getList(resourceName, {
//     //         pagination: { page: 1, perPage: 100 }
//     //     })
//     //     .then(response => {
//     //         setItems(response?.data || [] );
            
//     //     })
//     //     .catch(error => {
//     //         console.error("Error fetching page:", error);
//     //     });
//     // },[resourceName])

//     // console.log("Resource", resourceName);
//     // console.log("Items", items);

//     // return (
//     //   <SectionBox>
//     //     <Typography variant="h6">{resourceName}</Typography>
//     //     {items.map((item: any) => (
//     //         <Typography key={item.id} variant="body1">
//     //             <b>{item.name || item.id}</b>
//     //             {/*JSON.stringify(item)*/}
//     //         </Typography>
//     //     ))} 
        
//     //   </SectionBox>
//     // );
// };


// const ResourceSelector = ({ setSelectedResource }: { setSelectedResource: any }) => {
//     const conf = {}//useConf();
//     const [resourceName, setResourceName] = React.useState('');
//     const resources = conf.resources || {};
//     const resourceNames = Object.entries(resources).filter(([key, value]) => !value.hidden).map(([key, value]) => key);

//     const handleChange = (event) => {
//         setSelectedResource(event.target.value);
//         setResourceName(event.target.value);
//     };

//     return (
//         <FormControl variant="outlined" fullWidth>
//             <InputLabel id="resource-select-label">Resource</InputLabel>
//             <Select
//                 labelId="resource-select-label"
//                 id="resource-select"
//                 value={resourceName}
//                 onChange={handleChange}
//                 label="Resource"
//             >
//                 {resourceNames.map((name, index) => (
//                     <MenuItem key={index} value={name}>
//                         {name}
//                     </MenuItem>
//                 ))}
//             </Select>
//         </FormControl>
//     );

// }

// export const TestSection = ({section}: {section: ISection}) => {

//     const [ selectedResource, setSelectedResource ] = useState<string | null>(null);
    
//     return <>
//         <div id={section.id} style={{position: "relative", top: "-4.1em", border: "none", display:"block"}} > </div>
//         <ResourceSelector setSelectedResource={setSelectedResource}  />
//         {
//             selectedResource && <GenericSection resourceName={selectedResource}/>
//         }
//         <hr/>
//         </>
// }
