import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './EntityAttr-card.component.html',
  styleUrls: ['./EntityAttr-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.EntityAttr-card]': 'true'
  }
})

export class EntityAttrCardComponent {


}