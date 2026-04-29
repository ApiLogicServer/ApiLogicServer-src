import { Component, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'transactions-card',
  templateUrl: './Piece-card.component.html',
  styleUrls: ['./Piece-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Piece-card]': 'true'
  }
})

export class PieceCardComponent {


}