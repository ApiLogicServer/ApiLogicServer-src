import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './File-card.component.html',
  styleUrls: ['./File-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.File-card]': 'true'
  }
})

export class FileCardComponent {


}