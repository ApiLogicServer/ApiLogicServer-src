import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {CCPCUSTOMER_MODULE_DECLARATIONS, CcpCustomerRoutingModule} from  './CcpCustomer-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    CcpCustomerRoutingModule
  ],
  declarations: CCPCUSTOMER_MODULE_DECLARATIONS,
  exports: CCPCUSTOMER_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CcpCustomerModule { }