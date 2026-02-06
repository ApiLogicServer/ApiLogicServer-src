import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {PRODUCTSUPPLIER_MODULE_DECLARATIONS, ProductSupplierRoutingModule} from  './ProductSupplier-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    ProductSupplierRoutingModule
  ],
  declarations: PRODUCTSUPPLIER_MODULE_DECLARATIONS,
  exports: PRODUCTSUPPLIER_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ProductSupplierModule { }