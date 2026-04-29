import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'SpecialHandling-new',
  templateUrl: './SpecialHandling-new.component.html',
  styleUrls: ['./SpecialHandling-new.component.scss']
})
export class SpecialHandlingNewComponent {
  @ViewChild("SpecialHandlingForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}