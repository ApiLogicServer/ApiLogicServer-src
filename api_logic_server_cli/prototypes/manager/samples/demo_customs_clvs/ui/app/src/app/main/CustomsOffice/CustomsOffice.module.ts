import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {CUSTOMSOFFICE_MODULE_DECLARATIONS, CustomsOfficeRoutingModule} from  './CustomsOffice-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    CustomsOfficeRoutingModule
  ],
  declarations: CUSTOMSOFFICE_MODULE_DECLARATIONS,
  exports: CUSTOMSOFFICE_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class CustomsOfficeModule { }