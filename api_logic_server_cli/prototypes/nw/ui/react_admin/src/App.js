import React from 'react';
import { Admin, Resource } from 'react-admin';
import { createTheme } from '@mui/material/styles';

// Import DataProvider
import { dataProvider } from './dataProvider';

// Import resource components
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
import { CategoryList, CategoryShow, CategoryCreate, CategoryEdit } from './Category';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './Order';
import { ProductList, ProductShow, ProductCreate, ProductEdit } from './Product';
import { EmployeeList, EmployeeShow, EmployeeCreate, EmployeeEdit } from './Employee';
import { SupplierList, SupplierShow, SupplierCreate, SupplierEdit } from './Supplier';
import { ShipperList, ShipperShow, ShipperCreate, ShipperEdit } from './Shipper';
import { RegionList, RegionShow, RegionCreate, RegionEdit } from './Region';
import { TerritoryList, TerritoryShow, TerritoryCreate, TerritoryEdit } from './Territory';
import { CustomerDemographicList, CustomerDemographicShow, CustomerDemographicCreate, CustomerDemographicEdit } from './CustomerDemographic';
import { EmployeeAuditList, EmployeeAuditShow, EmployeeAuditCreate, EmployeeAuditEdit } from './EmployeeAudit';
import { EmployeeTerritoryList, EmployeeTerritoryShow, EmployeeTerritoryCreate, EmployeeTerritoryEdit } from './EmployeeTerritory';
import { DepartmentList, DepartmentShow, DepartmentCreate, DepartmentEdit } from './Department';
import { UnionList, UnionShow, UnionCreate, UnionEdit } from './Union';
import { LocationList, LocationShow, LocationCreate, LocationEdit } from './Location';
import { OrderDetailList, OrderDetailShow, OrderDetailCreate, OrderDetailEdit } from './OrderDetail';

// Define Material-UI Theme
const theme = createTheme({
    palette: {
        primary: { main: '#1976d2' }, // Material-UI default blue
        secondary: { main: '#1565c0' }, // A darker blue, or choose another color
    },
    typography: { fontSize: 14 },
});

const App = () => {
    return (
        <Admin dataProvider={dataProvider} theme={theme}>
            {/* Register each resource with their components */}
            <Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
            <Resource name="Category" list={CategoryList} show={CategoryShow} edit={CategoryEdit} create={CategoryCreate} />
            <Resource name="Order" list={OrderList} show={OrderShow} edit={OrderEdit} create={OrderCreate} />
            <Resource name="Product" list={ProductList} show={ProductShow} edit={ProductEdit} create={ProductCreate} />
            <Resource name="Employee" list={EmployeeList} show={EmployeeShow} edit={EmployeeEdit} create={EmployeeCreate} />
            <Resource name="Supplier" list={SupplierList} show={SupplierShow} edit={SupplierEdit} create={SupplierCreate} />
            <Resource name="Shipper" list={ShipperList} show={ShipperShow} edit={ShipperEdit} create={ShipperCreate} />
            <Resource name="Region" list={RegionList} show={RegionShow} edit={RegionEdit} create={RegionCreate} />
            <Resource name="Territory" list={TerritoryList} show={TerritoryShow} edit={TerritoryEdit} create={TerritoryCreate} />
            <Resource name="CustomerDemographic" list={CustomerDemographicList} show={CustomerDemographicShow} edit={CustomerDemographicEdit} create={CustomerDemographicCreate} />
            <Resource name="EmployeeAudit" list={EmployeeAuditList} show={EmployeeAuditShow} edit={EmployeeAuditEdit} create={EmployeeAuditCreate} />
            <Resource name="EmployeeTerritory" list={EmployeeTerritoryList} show={EmployeeTerritoryShow} edit={EmployeeTerritoryEdit} create={EmployeeTerritoryCreate} />
            <Resource name="Department" list={DepartmentList} show={DepartmentShow} edit={DepartmentEdit} create={DepartmentCreate} />
            <Resource name="Union" list={UnionList} show={UnionShow} edit={UnionEdit} create={UnionCreate} />
            <Resource name="Location" list={LocationList} show={LocationShow} edit={LocationEdit} create={LocationCreate} />
            <Resource name="OrderDetail" list={OrderDetailList} show={OrderDetailShow} edit={OrderDetailEdit} create={OrderDetailCreate} />
        </Admin>
    );
};

export default App;