import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {ENTITY_MODULE_DECLARATIONS, EntityRoutingModule} from  './Entity-routing.module';
import { OFileManagerModule } from 'ontimize-web-ngx-filemanager';
@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    EntityRoutingModule,
    OFileManagerModule
  ],
  declarations: ENTITY_MODULE_DECLARATIONS,
  exports: ENTITY_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class EntityModule { }