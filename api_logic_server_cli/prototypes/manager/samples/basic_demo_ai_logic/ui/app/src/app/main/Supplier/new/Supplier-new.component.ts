import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'Supplier-new',
  templateUrl: './Supplier-new.component.html',
  styleUrls: ['./Supplier-new.component.scss']
})
export class SupplierNewComponent {
  @ViewChild("SupplierForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}