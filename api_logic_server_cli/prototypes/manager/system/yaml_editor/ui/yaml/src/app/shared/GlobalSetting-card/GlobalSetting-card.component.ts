import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './GlobalSetting-card.component.html',
  styleUrls: ['./GlobalSetting-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.GlobalSetting-card]': 'true'
  }
})

export class GlobalSettingCardComponent {


}