import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'YamlFiles-new',
  templateUrl: './YamlFiles-new.component.html',
  styleUrls: ['./YamlFiles-new.component.scss']
})
export class YamlFilesNewComponent {
  @ViewChild('YamlFilesForm') form: OFormComponent
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
  onInsertMode() {
    const default_values = {"name": "app_model.yaml"};
    this.form.setFieldValues(default_values);
  }
}