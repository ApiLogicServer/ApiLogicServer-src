import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {CUSTOMER_MODULE_DECLARATIONS, CustomerRoutingModule} from  './Customer-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    CustomerRoutingModule
  ],
  declarations: CUSTOMER_MODULE_DECLARATIONS,
  exports: CUSTOMER_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CustomerModule { }