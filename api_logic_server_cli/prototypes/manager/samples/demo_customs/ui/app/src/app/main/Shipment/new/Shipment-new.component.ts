import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'Shipment-new',
  templateUrl: './Shipment-new.component.html',
  styleUrls: ['./Shipment-new.component.scss']
})
export class ShipmentNewComponent {
  @ViewChild("ShipmentForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'duty_credit_card_flg': "'N'", 'rod_flg': "'N'", 'trprt_credit_card_flg': "'N'", 'eci_flg': "'N'", 'ci_image_flg': "'N'", 'duplicate_shipment_record_flg': "'N'", 'oga_shipment_flg': "'N'", 'active_flg': "'Y'"}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}