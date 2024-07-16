import { Component, Injector } from '@angular/core';
import { NavigationService } from 'ontimize-web-ngx';

@Component({
  selector: 'GlobalSetting-new',
  templateUrl: './GlobalSetting-new.component.html',
  styleUrls: ['./GlobalSetting-new.component.scss']
})
export class GlobalSettingNewComponent {
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}