import {CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { OntimizeWebModule } from 'ontimize-web-ngx';
import { SharedModule } from '../../shared/shared.module';
import  {ENTITYATTR_MODULE_DECLARATIONS, EntityAttrRoutingModule} from  './EntityAttr-routing.module';

@NgModule({

  imports: [
    SharedModule,
    CommonModule,
    OntimizeWebModule,
    EntityAttrRoutingModule
  ],
  declarations: ENTITYATTR_MODULE_DECLARATIONS,
  exports: ENTITYATTR_MODULE_DECLARATIONS,
  schemas: [CUSTOM_ELEMENTS_SCHEMA]
})
export class EntityAttrModule { }