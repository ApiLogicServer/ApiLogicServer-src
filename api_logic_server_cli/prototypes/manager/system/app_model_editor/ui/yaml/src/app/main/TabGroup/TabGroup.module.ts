import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {TABGROUP_MODULE_DECLARATIONS, TabGroupRoutingModule} from  './TabGroup-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    TabGroupRoutingModule
  ],
  declarations: TABGROUP_MODULE_DECLARATIONS,
  exports: TABGROUP_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class TabGroupModule { }