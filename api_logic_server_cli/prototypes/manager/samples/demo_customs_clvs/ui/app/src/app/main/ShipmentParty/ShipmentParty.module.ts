import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {SHIPMENTPARTY_MODULE_DECLARATIONS, ShipmentPartyRoutingModule} from  './ShipmentParty-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    ShipmentPartyRoutingModule
  ],
  declarations: SHIPMENTPARTY_MODULE_DECLARATIONS,
  exports: SHIPMENTPARTY_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ShipmentPartyModule { }