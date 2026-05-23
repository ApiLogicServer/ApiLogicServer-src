import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'ControlledRegulatedGood-new',
  templateUrl: './ControlledRegulatedGood-new.component.html',
  styleUrls: ['./ControlledRegulatedGood-new.component.scss']
})
export class ControlledRegulatedGoodNewComponent {
  @ViewChild("ControlledRegulatedGoodForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}