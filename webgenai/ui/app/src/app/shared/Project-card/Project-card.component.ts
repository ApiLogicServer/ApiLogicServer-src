import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Project-card.component.html',
  styleUrls: ['./Project-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Project-card]': 'true'
  }
})

export class ProjectCardComponent {


}