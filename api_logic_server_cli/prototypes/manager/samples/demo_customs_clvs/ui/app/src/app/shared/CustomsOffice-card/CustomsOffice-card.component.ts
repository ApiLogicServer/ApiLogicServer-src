import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './CustomsOffice-card.component.html',
  styleUrls: ['./CustomsOffice-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.CustomsOffice-card]': 'true'
  }
})

export class CustomsOfficeCardComponent {


}