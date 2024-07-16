import { Component, Injector } from '@angular/core';
import { NavigationService } from 'ontimize-web-ngx';

@Component({
  selector: 'YamlFiles-new',
  templateUrl: './YamlFiles-new.component.html',
  styleUrls: ['./YamlFiles-new.component.scss']
})
export class YamlFilesNewComponent {
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}