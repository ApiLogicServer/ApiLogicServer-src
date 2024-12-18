import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Order-card.component.html',
  styleUrls: ['./Order-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Order-card]': 'true'
  }
})

export class OrderCardComponent {


}