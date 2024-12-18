import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './OrderItem-card.component.html',
  styleUrls: ['./OrderItem-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.OrderItem-card]': 'true'
  }
})

export class OrderItemCardComponent {


}