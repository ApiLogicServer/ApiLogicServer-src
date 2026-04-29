import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'CcpCustomer-new',
  templateUrl: './CcpCustomer-new.component.html',
  styleUrls: ['./CcpCustomer-new.component.scss']
})
export class CcpCustomerNewComponent {
  @ViewChild("CcpCustomerForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}