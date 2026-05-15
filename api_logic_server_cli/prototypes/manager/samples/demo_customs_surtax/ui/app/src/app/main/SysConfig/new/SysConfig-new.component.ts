import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'SysConfig-new',
  templateUrl: './SysConfig-new.component.html',
  styleUrls: ['./SysConfig-new.component.scss']
})
export class SysConfigNewComponent {
  @ViewChild("SysConfigForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'name': "'system'", 'discount_rate': '0.05', 'tax_rate': '0.10'}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}