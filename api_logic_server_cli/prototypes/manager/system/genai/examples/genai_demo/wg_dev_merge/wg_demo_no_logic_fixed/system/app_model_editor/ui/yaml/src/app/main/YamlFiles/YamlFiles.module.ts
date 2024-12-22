import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {YAMLFILES_MODULE_DECLARATIONS, YamlFilesRoutingModule} from  './YamlFiles-routing.module';
//import { OFileManagerModule } from 'ontimize-web-ngx-filemanager';
@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    YamlFilesRoutingModule
  ],
  declarations: YAMLFILES_MODULE_DECLARATIONS,
  exports: YAMLFILES_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class YamlFilesModule { }