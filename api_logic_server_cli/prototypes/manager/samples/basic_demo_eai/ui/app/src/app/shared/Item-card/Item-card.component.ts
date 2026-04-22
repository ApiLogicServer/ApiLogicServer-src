import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Item-card.component.html',
  styleUrls: ['./Item-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Item-card]': 'true'
  }
})

export class ItemCardComponent {


}