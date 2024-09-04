import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './User-card.component.html',
  styleUrls: ['./User-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.User-card]': 'true'
  }
})

export class UserCardComponent {


}