import React from 'react';
import { Admin, Resource } from 'react-admin';
import { createTheme } from '@mui/material/styles';
// import data provider
import { dataProvider } from './dataProvider';

// Import all resource components
import { CustomerList, CustomerShow, CustomerCreate, CustomerEdit } from './Customer';
import { OrderList, OrderShow, OrderCreate, OrderEdit } from './Order';
import { ProductList, ProductShow, ProductCreate, ProductEdit } from './Product';
import { CategoryList, CategoryShow, CategoryCreate, CategoryEdit } from './Category';
import { EmployeeList, EmployeeShow, EmployeeCreate, EmployeeEdit } from './Employee';
import { DepartmentList, DepartmentShow, DepartmentCreate, DepartmentEdit } from './Department';
import { SupplierList, SupplierShow, SupplierCreate, SupplierEdit } from './Supplier';
import { ShipperList, ShipperShow, ShipperCreate, ShipperEdit } from './Shipper';
import { TerritoryList, TerritoryShow, TerritoryCreate, TerritoryEdit } from './Territory';
import { CustomerDemographicList, CustomerDemographicShow, CustomerDemographicCreate, CustomerDemographicEdit } from './CustomerDemographic';
import { EmployeeAuditList, EmployeeAuditShow, EmployeeAuditCreate, EmployeeAuditEdit } from './EmployeeAudit';
import { EmployeeTerritoryList, EmployeeTerritoryShow, EmployeeTerritoryCreate, EmployeeTerritoryEdit } from './EmployeeTerritory';
import { LocationList, LocationShow, LocationCreate, LocationEdit } from './Location';
import { OrderDetailList, OrderDetailShow, OrderDetailCreate, OrderDetailEdit } from './OrderDetail';
import { RegionList, RegionShow, RegionCreate, RegionEdit } from './Region';
import { SampleDBVersionList, SampleDBVersionShow, SampleDBVersionCreate, SampleDBVersionEdit } from './SampleDBVersion';
import { UnionList, UnionShow, UnionCreate, UnionEdit } from './Union';

const theme = createTheme({
    palette: {
        primary: { main: '#1976d2' },
        secondary: { main: '#1565c0' },
    },
    typography: { fontSize: 14 },
});

const App = () => {
  return (
    <Admin dataProvider={dataProvider} theme={theme}>
      <Resource name="Customer" list={CustomerList} show={CustomerShow} edit={CustomerEdit} create={CustomerCreate} />
      <Resource name="Order" list={OrderList} show={OrderShow} edit={OrderEdit} create={OrderCreate} />
      <Resource name="Product" list={ProductList} show={ProductShow} edit={ProductEdit} create={ProductCreate} />
      <Resource name="Category" list={CategoryList} show={CategoryShow} edit={CategoryEdit} create={CategoryCreate} />
      <Resource name="Employee" list={EmployeeList} show={EmployeeShow} edit={EmployeeEdit} create={EmployeeCreate} />
      <Resource name="Department" list={DepartmentList} show={DepartmentShow} edit={DepartmentEdit} create={DepartmentCreate} />
      <Resource name="Supplier" list={SupplierList} show={SupplierShow} edit={SupplierEdit} create={SupplierCreate} />
      <Resource name="Shipper" list={ShipperList} show={ShipperShow} edit={ShipperEdit} create={ShipperCreate} />
      <Resource name="Territory" list={TerritoryList} show={TerritoryShow} edit={TerritoryEdit} create={TerritoryCreate} />
      <Resource name="CustomerDemographic" list={CustomerDemographicList} show={CustomerDemographicShow} edit={CustomerDemographicEdit} create={CustomerDemographicCreate} />
      <Resource name="EmployeeAudit" list={EmployeeAuditList} show={EmployeeAuditShow} edit={EmployeeAuditEdit} create={EmployeeAuditCreate} />
      <Resource name="EmployeeTerritory" list={EmployeeTerritoryList} show={EmployeeTerritoryShow} edit={EmployeeTerritoryEdit} create={EmployeeTerritoryCreate} />
      <Resource name="Location" list={LocationList} show={LocationShow} edit={LocationEdit} create={LocationCreate} />
      <Resource name="OrderDetail" list={OrderDetailList} show={OrderDetailShow} edit={OrderDetailEdit} create={OrderDetailCreate} />
      <Resource name="Region" list={RegionList} show={RegionShow} edit={RegionEdit} create={RegionCreate} />
      <Resource name="SampleDBVersion" list={SampleDBVersionList} show={SampleDBVersionShow} edit={SampleDBVersionEdit} create={SampleDBVersionCreate} />
      <Resource name="Union" list={UnionList} show={UnionShow} edit={UnionEdit} create={UnionCreate} />
    </Admin>
  );
};

export default App;