import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'GovtDept-new',
  templateUrl: './GovtDept-new.component.html',
  styleUrls: ['./GovtDept-new.component.scss']
})
export class GovtDeptNewComponent {
  @ViewChild("GovtDeptForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}