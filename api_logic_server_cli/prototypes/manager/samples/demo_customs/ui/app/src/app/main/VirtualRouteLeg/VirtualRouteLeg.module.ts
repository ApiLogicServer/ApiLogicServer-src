import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {VIRTUALROUTELEG_MODULE_DECLARATIONS, VirtualRouteLegRoutingModule} from  './VirtualRouteLeg-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    VirtualRouteLegRoutingModule
  ],
  declarations: VIRTUALROUTELEG_MODULE_DECLARATIONS,
  exports: VIRTUALROUTELEG_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class VirtualRouteLegModule { }