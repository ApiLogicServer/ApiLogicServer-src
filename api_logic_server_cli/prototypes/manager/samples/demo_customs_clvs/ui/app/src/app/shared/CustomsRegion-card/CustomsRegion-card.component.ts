import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './CustomsRegion-card.component.html',
  styleUrls: ['./CustomsRegion-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.CustomsRegion-card]': 'true'
  }
})

export class CustomsRegionCardComponent {


}