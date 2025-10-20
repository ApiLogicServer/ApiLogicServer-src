import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Customer-card.component.html',
  styleUrls: ['./Customer-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Customer-card]': 'true'
  }
})

export class CustomerCardComponent {


}