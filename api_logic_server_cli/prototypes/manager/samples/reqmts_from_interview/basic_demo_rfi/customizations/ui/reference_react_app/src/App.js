import React from 'react';
import { Admin, Resource, Loading } from 'react-admin';
import { jsonapiClient } from "./rav4-jsonapi-client/ra-jsonapi-client";
import { createTheme } from '@mui/material/styles';
import { useConf, loadHomeConf } from "./Config";
// Import resource components
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
import { ItemList, ItemShow, ItemCreate, ItemEdit } from './Item';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './Order';
import { ProductList, ProductShow, ProductCreate, ProductEdit } from './Product';
import { SysEmailList, SysEmailShow, SysEmailCreate, SysEmailEdit } from './SysEmail';
import { SysMcpList, SysMcpShow, SysMcpCreate, SysMcpEdit } from './SysMcp';

const theme = createTheme({
    palette: {
        primary: { main: '#1976d2' },
        secondary: { main: '#1565c0' },
    },
    typography: { fontSize: 14 },
});

const App = () => {
  const [conf, setConf] = React.useState({});
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('loading HomeConf-1');
        const confResult = await loadHomeConf();
        setConf(confResult);
        setLoading(false);
        console.log('AppConf0: ', confResult);
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
    <Admin dataProvider={dataProvider} theme={theme}>
      {/* Register resources */}
      <Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
      <Resource name="Item" list={ItemList} show={ItemShow} edit={ItemEdit} create={ItemCreate} />
      <Resource name="Order" list={OrderList} show={OrderShow} edit={OrderEdit} create={OrderCreate} />
      <Resource name="Product" list={ProductList} show={ProductShow} edit={ProductEdit} create={ProductCreate} />
      <Resource name="SysEmail" list={SysEmailList} show={SysEmailShow} edit={SysEmailEdit} create={SysEmailCreate} />
      <Resource name="SysMcp" list={SysMcpList} show={SysMcpShow} edit={SysMcpEdit} create={SysMcpCreate} />
    </Admin>
  );
};

export default App;