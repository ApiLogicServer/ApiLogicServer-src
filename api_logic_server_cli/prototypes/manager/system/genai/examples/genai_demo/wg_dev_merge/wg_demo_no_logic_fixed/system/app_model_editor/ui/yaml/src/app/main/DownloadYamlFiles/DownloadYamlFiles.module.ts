import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {DOWNLOAD_YAMLFILES_MODULE_DECLARATIONS, DownloadYamlFilesRoutingModule} from  './DownloadYamlFiles-routing.module';
//import { OFileManagerModule } from 'ontimize-web-ngx-filemanager';
@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    DownloadYamlFilesRoutingModule
  ],
  declarations: DOWNLOAD_YAMLFILES_MODULE_DECLARATIONS,
  exports: DOWNLOAD_YAMLFILES_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class DownloadYamlFilesModule { }