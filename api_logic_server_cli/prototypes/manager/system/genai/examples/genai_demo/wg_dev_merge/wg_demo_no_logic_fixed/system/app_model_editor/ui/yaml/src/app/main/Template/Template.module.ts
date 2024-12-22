import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {TEMPLATE_MODULE_DECLARATIONS, TemplateRoutingModule} from  './Template-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    TemplateRoutingModule
  ],
  declarations: TEMPLATE_MODULE_DECLARATIONS,
  exports: TEMPLATE_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class TemplateModule { }