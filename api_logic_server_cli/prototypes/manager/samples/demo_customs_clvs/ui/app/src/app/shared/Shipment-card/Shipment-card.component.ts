import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Shipment-card.component.html',
  styleUrls: ['./Shipment-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Shipment-card]': 'true'
  }
})

export class ShipmentCardComponent {


}