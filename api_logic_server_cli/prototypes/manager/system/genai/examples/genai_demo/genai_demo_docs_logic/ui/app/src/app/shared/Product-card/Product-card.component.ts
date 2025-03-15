import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Product-card.component.html',
  styleUrls: ['./Product-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Product-card]': 'true'
  }
})

export class ProductCardComponent {


}