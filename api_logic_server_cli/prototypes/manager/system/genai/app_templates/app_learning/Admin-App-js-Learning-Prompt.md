App Wiring
Sample code for react App.js (follow these guidelines EXACTLY):

// begin constant imports (always included) -- generate this code EXACTLY
import React from 'react';
import { Admin, Resource, Loading } from 'react-admin';  // val? loading
import { jsonapiClient } from "./rav4-jsonapi-client/ra-jsonapi-client";
import { createTheme } from '@mui/material/styles';
import { useConf, loadHomeConf } from "./Config";  // val ??
// end constant imports

// import each resource, e.g.
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
...

const theme = createTheme({
    palette: {
        primary: { main: '#1976d2' },    // Material-UI default blue
        secondary: { main: '#1565c0' },  // A darker blue, or choose another color
    },
    typography: { fontSize: 14 },
});

const App = () => {
  const [conf, setConf] = React.useState({});
  
  React.useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('loading HomeConf-1')
        const conf = await loadHomeConf()
        setConf(conf)
        setLoading(false);
        console.log('AppConf0: ', conf);
      } catch (error) {
        console.error('Error fetching data:', error);
        sessionStorage.removeItem("raSpa");
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Loading loadingPrimary="Loading..." loadingSecondary="Please wait" />;
  }
  const dataProvider = jsonapiClient(conf.api_root, { conf: {} }, null);

  return (
        // register each resource (do NOT generate {dataProvider(conf.api_root)}...
        <Admin dataProvider={dataProvider} theme={theme}>
            <Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
...
        </Admin>
    );
};

export default App;
Response Format
Format the response as a JSResponseFormat:

class JSResponseFormat(BaseModel): # must match system/genai/prompt_inserts/response_format.prompt code : str # generated javascript code (only)