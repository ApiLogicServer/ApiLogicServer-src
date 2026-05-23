import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './ControlledRegulatedGood-card.component.html',
  styleUrls: ['./ControlledRegulatedGood-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.ControlledRegulatedGood-card]': 'true'
  }
})

export class ControlledRegulatedGoodCardComponent {


}