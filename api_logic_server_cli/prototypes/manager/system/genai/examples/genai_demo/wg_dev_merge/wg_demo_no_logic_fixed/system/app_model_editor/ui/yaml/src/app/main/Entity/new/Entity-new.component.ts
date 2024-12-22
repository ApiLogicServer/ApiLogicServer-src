import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'Entity-new',
  templateUrl: './Entity-new.component.html',
  styleUrls: ['./Entity-new.component.scss']
})
export class EntityNewComponent {
  @ViewChild("EntityForm") form: OFormComponent;
  onInsertMode() {
    const defaultValues = {'mode':'tab','menu_group':'data','new_template':'new_template.html','home_template':'home_template.html','detail_template':'detail_template.html'};
    this.form.setFieldValues(defaultValues);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}