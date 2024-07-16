import { Component, Injector } from '@angular/core';
import { NavigationService } from 'ontimize-web-ngx';

@Component({
  selector: 'Template-new',
  templateUrl: './Template-new.component.html',
  styleUrls: ['./Template-new.component.scss']
})
export class TemplateNewComponent {
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}