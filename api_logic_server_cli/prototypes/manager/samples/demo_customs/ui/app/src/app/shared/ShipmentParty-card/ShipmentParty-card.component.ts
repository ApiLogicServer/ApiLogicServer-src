import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './ShipmentParty-card.component.html',
  styleUrls: ['./ShipmentParty-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.ShipmentParty-card]': 'true'
  }
})

export class ShipmentPartyCardComponent {


}