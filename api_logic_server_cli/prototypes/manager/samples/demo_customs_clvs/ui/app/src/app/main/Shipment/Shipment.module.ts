import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {SHIPMENT_MODULE_DECLARATIONS, ShipmentRoutingModule} from  './Shipment-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    ShipmentRoutingModule
  ],
  declarations: SHIPMENT_MODULE_DECLARATIONS,
  exports: SHIPMENT_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ShipmentModule { }