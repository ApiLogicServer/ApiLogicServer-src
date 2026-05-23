import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'CustomsOffice-new',
  templateUrl: './CustomsOffice-new.component.html',
  styleUrls: ['./CustomsOffice-new.component.scss']
})
export class CustomsOfficeNewComponent {
  @ViewChild("CustomsOfficeForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'clvs_release': '0', 'sufferance_warehouse': '0'}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}