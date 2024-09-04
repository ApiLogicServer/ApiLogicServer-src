import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'File-new',
  templateUrl: './File-new.component.html',
  styleUrls: ['./File-new.component.scss']
})
export class FileNewComponent {
  @ViewChild("FileForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'created_at': 'CURRENT_TIMESTAMP'}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}