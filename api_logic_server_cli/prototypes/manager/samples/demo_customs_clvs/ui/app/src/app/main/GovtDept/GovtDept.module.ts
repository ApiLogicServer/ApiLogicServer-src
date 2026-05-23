import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {GOVTDEPT_MODULE_DECLARATIONS, GovtDeptRoutingModule} from  './GovtDept-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    GovtDeptRoutingModule
  ],
  declarations: GOVTDEPT_MODULE_DECLARATIONS,
  exports: GOVTDEPT_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class GovtDeptModule { }