import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './YamlFiles-card.component.html',
  styleUrls: ['./YamlFiles-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.YamlFiles-card]': 'true'
  }
})

export class YamlFilesCardComponent {


}