import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'ShipmentCommodity-new',
  templateUrl: './ShipmentCommodity-new.component.html',
  styleUrls: ['./ShipmentCommodity-new.component.scss']
})
export class ShipmentCommodityNewComponent {
  @ViewChild("ShipmentCommodityForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}