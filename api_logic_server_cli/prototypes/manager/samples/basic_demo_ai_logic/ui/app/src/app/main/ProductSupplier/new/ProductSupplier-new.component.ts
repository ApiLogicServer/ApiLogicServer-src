import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'ProductSupplier-new',
  templateUrl: './ProductSupplier-new.component.html',
  styleUrls: ['./ProductSupplier-new.component.scss']
})
export class ProductSupplierNewComponent {
  @ViewChild("ProductSupplierForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}