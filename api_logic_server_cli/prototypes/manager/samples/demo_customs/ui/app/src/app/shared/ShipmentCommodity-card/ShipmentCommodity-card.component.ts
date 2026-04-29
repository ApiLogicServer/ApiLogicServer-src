import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './ShipmentCommodity-card.component.html',
  styleUrls: ['./ShipmentCommodity-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.ShipmentCommodity-card]': 'true'
  }
})

export class ShipmentCommodityCardComponent {


}