import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Template-card.component.html',
  styleUrls: ['./Template-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Template-card]': 'true'
  }
})

export class TemplateCardComponent {


}