import { Component, Injector, ViewChild } from '@angular/core';
import { NavigationService, OFormComponent } from 'ontimize-web-ngx';

@Component({
  selector: 'Piece-new',
  templateUrl: './Piece-new.component.html',
  styleUrls: ['./Piece-new.component.scss']
})
export class PieceNewComponent {
  @ViewChild("PieceForm") form: OFormComponent;
  onInsertMode() {
    const default_values = {'split_seq_nbr': '0'}
    this.form.setFieldValues(default_values);
  }
  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
}