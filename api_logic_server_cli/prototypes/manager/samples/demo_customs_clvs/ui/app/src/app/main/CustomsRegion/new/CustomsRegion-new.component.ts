import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'CustomsRegion-new',
  templateUrl: './CustomsRegion-new.component.html',
  styleUrls: ['./CustomsRegion-new.component.scss']
})
export class CustomsRegionNewComponent {
  @ViewChild("CustomsRegionForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}