import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './SysConfig-card.component.html',
  styleUrls: ['./SysConfig-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.SysConfig-card]': 'true'
  }
})

export class SysConfigCardComponent {


}