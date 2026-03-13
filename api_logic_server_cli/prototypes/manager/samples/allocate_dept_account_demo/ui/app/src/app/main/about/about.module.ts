import { NgModule } from '@angular/core';
import { OntimizeWebModule } from 'ontimize-web-ngx';

import { SharedModule } from '../../shared/shared.module';
import { AboutRoutingModule } from './about-routing.module';
import { AboutComponent } from './about.component';

@NgModule({
  imports: [
    SharedModule,
    OntimizeWebModule,
    AboutRoutingModule
  ],
  declarations: [
    AboutComponent
  ]
})
export class AboutModule { }
