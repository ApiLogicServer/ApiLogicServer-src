import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Supplier-card.component.html',
  styleUrls: ['./Supplier-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Supplier-card]': 'true'
  }
})

export class SupplierCardComponent {


}