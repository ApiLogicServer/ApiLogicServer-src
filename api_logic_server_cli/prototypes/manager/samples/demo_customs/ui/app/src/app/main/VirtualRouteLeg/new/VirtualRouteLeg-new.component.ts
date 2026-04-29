import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'VirtualRouteLeg-new',
  templateUrl: './VirtualRouteLeg-new.component.html',
  styleUrls: ['./VirtualRouteLeg-new.component.scss']
})
export class VirtualRouteLegNewComponent {
  @ViewChild("VirtualRouteLegForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}