// App.js
import React from 'react';
import { Admin, Resource, Loading } from 'react-admin';
import { jsonapiClient } from './rav4-jsonapi-client/ra-jsonapi-client';
import { createTheme } from '@mui/material/styles';
import { useConf, loadHomeConf } from './Config';
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './Order';
import { ItemList, ItemShow, ItemCreate, ItemEdit } from './Item';
import { ProductList, ProductShow, ProductCreate, ProductEdit } from './Product';

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
                const conf = await loadHomeConf();
                setConf(conf);
                setLoading(false);
                console.log('AppConf0: ', conf);
            } catch (error) {
                console.error('Error fetching data:', error);
                sessionStorage.removeItem('raSpa');
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
            <Resource
                name="Customer"
                list={CustomerList}
                show={CustomerShow}
                edit={CustomerEdit}
                create={CustomerCreate}
            />
            <Resource
                name="Order"
                list={OrderList}
                show={OrderShow}
                edit={OrderEdit}
                create={OrderCreate}
            />
            <Resource
                name="Item"
                list={ItemList}
                show={ItemShow}
                edit={ItemEdit}
                create={ItemCreate}
            />
            <Resource
                name="Product"
                list={ProductList}
                show={ProductShow}
                edit={ProductEdit}
                create={ProductCreate}
            />
        </Admin>
    );
};

export default App;