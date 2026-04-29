import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './VirtualRouteLeg-card.component.html',
  styleUrls: ['./VirtualRouteLeg-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.VirtualRouteLeg-card]': 'true'
  }
})

export class VirtualRouteLegCardComponent {


}