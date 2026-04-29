import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {SPECIALHANDLING_MODULE_DECLARATIONS, SpecialHandlingRoutingModule} from  './SpecialHandling-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    SpecialHandlingRoutingModule
  ],
  declarations: SPECIALHANDLING_MODULE_DECLARATIONS,
  exports: SPECIALHANDLING_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class SpecialHandlingModule { }