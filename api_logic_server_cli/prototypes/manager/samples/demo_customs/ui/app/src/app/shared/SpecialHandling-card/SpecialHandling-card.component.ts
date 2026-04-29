import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './SpecialHandling-card.component.html',
  styleUrls: ['./SpecialHandling-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.SpecialHandling-card]': 'true'
  }
})

export class SpecialHandlingCardComponent {


}