import { NgModule } from '@angular/core';
import { OntimizeWebModule } from 'ontimize-web-ngx';

import { SharedModule } from '../../shared/shared.module';
import { SettingsRoutingModule } from './settings-routing.module';
import { SettingsComponent } from './settings.component';

@NgModule({
  imports: [
    SharedModule,
    OntimizeWebModule,
    SettingsRoutingModule
  ],
  declarations: [
    SettingsComponent
  ]
})
export class SettingsModule { }
