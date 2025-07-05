// Begin constant imports (always included)
import React from 'react';
import { Admin, Resource, Loading } from 'react-admin';
import { jsonapiClient } from './rav4-jsonapi-client/ra-jsonapi-client';
import { createTheme } from '@mui/material/styles';
import { useConf, loadHomeConf } from './Config';
import LandingPage from './LandingPage';
import CustomLayout from './CustomLayout';
// End constant imports

// Import each resource
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
import { CategoryList, CategoryShow, CategoryCreate, CategoryEdit } from './Category';
import { DepartmentList, DepartmentShow, DepartmentCreate, DepartmentEdit } from './Department';
import { EmployeeList, EmployeeShow, EmployeeCreate, EmployeeEdit } from './Employee';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './Order';
import { OrderDetailList, OrderDetailShow, OrderDetailCreate, OrderDetailEdit } from './OrderDetail';
import { ProductList, ProductShow, ProductCreate, ProductEdit } from './Product';
import { SupplierList, SupplierShow, SupplierCreate, SupplierEdit } from './Supplier';
import { ShipperList, ShipperShow, ShipperCreate, ShipperEdit } from './Shipper';
import { RegionList, RegionShow, RegionCreate, RegionEdit } from './Region';
import { TerritoryList, TerritoryShow, TerritoryCreate, TerritoryEdit } from './Territory';
import { UnionList, UnionShow, UnionCreate, UnionEdit } from './Union';

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
        <Admin 
            dataProvider={dataProvider} 
            theme={theme}
            dashboard={LandingPage}
            layout={CustomLayout}
        >
            <Resource
                name="Customer"
                list={CustomerList}
                show={CustomerShow}
                edit={CustomerEdit}
                create={CustomerCreate}
            />
            <Resource
                name="Category"
                list={CategoryList}
                show={CategoryShow}
                edit={CategoryEdit}
                create={CategoryCreate}
            />
            <Resource
                name="Department"
                list={DepartmentList}
                show={DepartmentShow}
                edit={DepartmentEdit}
                create={DepartmentCreate}
            />
            <Resource
                name="Employee"
                list={EmployeeList}
                show={EmployeeShow}
                edit={EmployeeEdit}
                create={EmployeeCreate}
            />
            <Resource
                name="Order"
                list={OrderList}
                show={OrderShow}
                edit={OrderEdit}
                create={OrderCreate}
            />
            <Resource
                name="OrderDetail"
                list={OrderDetailList}
                show={OrderDetailShow}
                edit={OrderDetailEdit}
                create={OrderDetailCreate}
            />
            <Resource
                name="Product"
                list={ProductList}
                show={ProductShow}
                edit={ProductEdit}
                create={ProductCreate}
            />
            <Resource
                name="Supplier"
                list={SupplierList}
                show={SupplierShow}
                edit={SupplierEdit}
                create={SupplierCreate}
            />
            <Resource
                name="Shipper"
                list={ShipperList}
                show={ShipperShow}
                edit={ShipperEdit}
                create={ShipperCreate}
            />
            <Resource
                name="Region"
                list={RegionList}
                show={RegionShow}
                edit={RegionEdit}
                create={RegionCreate}
            />
            <Resource
                name="Territory"
                list={TerritoryList}
                show={TerritoryShow}
                edit={TerritoryEdit}
                create={TerritoryCreate}
            />
            <Resource
                name="Union"
                list={UnionList}
                show={UnionShow}
                edit={UnionEdit}
                create={UnionCreate}
            />
        </Admin>
    );
};

export default App;