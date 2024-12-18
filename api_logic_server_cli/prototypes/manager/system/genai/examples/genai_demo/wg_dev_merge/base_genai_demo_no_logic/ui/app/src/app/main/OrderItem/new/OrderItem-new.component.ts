import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'OrderItem-new',
  templateUrl: './OrderItem-new.component.html',
  styleUrls: ['./OrderItem-new.component.scss']
})
export class OrderItemNewComponent {
  @ViewChild("OrderItemForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}