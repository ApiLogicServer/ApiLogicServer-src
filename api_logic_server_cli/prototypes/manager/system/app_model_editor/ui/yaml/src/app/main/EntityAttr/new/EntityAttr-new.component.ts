import { Component, Injector } from '@angular/core';
import { NavigationService } from 'ontimize-web-ngx';

@Component({
  selector: 'EntityAttr-new',
  templateUrl: './EntityAttr-new.component.html',
  styleUrls: ['./EntityAttr-new.component.scss']
})
export class EntityAttrNewComponent {
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}