import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {SYSCONFIG_MODULE_DECLARATIONS, SysConfigRoutingModule} from  './SysConfig-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    SysConfigRoutingModule
  ],
  declarations: SYSCONFIG_MODULE_DECLARATIONS,
  exports: SYSCONFIG_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class SysConfigModule { }