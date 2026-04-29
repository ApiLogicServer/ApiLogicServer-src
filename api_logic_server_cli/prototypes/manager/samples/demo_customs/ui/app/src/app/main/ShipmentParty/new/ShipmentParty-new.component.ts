import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'ShipmentParty-new',
  templateUrl: './ShipmentParty-new.component.html',
  styleUrls: ['./ShipmentParty-new.component.scss']
})
export class ShipmentPartyNewComponent {
  @ViewChild("ShipmentPartyForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'additional_contact_flg': "'N'"}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}