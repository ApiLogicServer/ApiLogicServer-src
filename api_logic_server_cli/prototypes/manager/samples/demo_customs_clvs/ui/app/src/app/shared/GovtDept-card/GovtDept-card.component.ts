import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './GovtDept-card.component.html',
  styleUrls: ['./GovtDept-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.GovtDept-card]': 'true'
  }
})

export class GovtDeptCardComponent {


}