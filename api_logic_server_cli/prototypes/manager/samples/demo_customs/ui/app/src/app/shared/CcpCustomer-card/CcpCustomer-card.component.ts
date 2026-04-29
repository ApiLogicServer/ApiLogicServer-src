import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './CcpCustomer-card.component.html',
  styleUrls: ['./CcpCustomer-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.CcpCustomer-card]': 'true'
  }
})

export class CcpCustomerCardComponent {


}