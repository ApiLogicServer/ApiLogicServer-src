import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './ProductSupplier-card.component.html',
  styleUrls: ['./ProductSupplier-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.ProductSupplier-card]': 'true'
  }
})

export class ProductSupplierCardComponent {


}