import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './TabGroup-card.component.html',
  styleUrls: ['./TabGroup-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.TabGroup-card]': 'true'
  }
})

export class TabGroupCardComponent {


}