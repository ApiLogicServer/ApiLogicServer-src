import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {CUSTOMSREGION_MODULE_DECLARATIONS, CustomsRegionRoutingModule} from  './CustomsRegion-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    CustomsRegionRoutingModule
  ],
  declarations: CUSTOMSREGION_MODULE_DECLARATIONS,
  exports: CUSTOMSREGION_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CustomsRegionModule { }