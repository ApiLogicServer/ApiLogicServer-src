import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {SHIPMENTCOMMODITY_MODULE_DECLARATIONS, ShipmentCommodityRoutingModule} from  './ShipmentCommodity-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    ShipmentCommodityRoutingModule
  ],
  declarations: SHIPMENTCOMMODITY_MODULE_DECLARATIONS,
  exports: SHIPMENTCOMMODITY_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ShipmentCommodityModule { }