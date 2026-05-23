import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {CONTROLLEDREGULATEDGOOD_MODULE_DECLARATIONS, ControlledRegulatedGoodRoutingModule} from  './ControlledRegulatedGood-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    ControlledRegulatedGoodRoutingModule
  ],
  declarations: CONTROLLEDREGULATEDGOOD_MODULE_DECLARATIONS,
  exports: CONTROLLEDREGULATEDGOOD_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class ControlledRegulatedGoodModule { }