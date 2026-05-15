import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PieceHomeComponent } from './home/Piece-home.component';
import { PieceNewComponent } from './new/Piece-new.component';
import { PieceDetailComponent } from './detail/Piece-detail.component';

const routes: Routes = [
  {path: '', component: PieceHomeComponent},
  { path: 'new', component: PieceNewComponent },
  { path: ':local_piece_oid_nbr', component: PieceDetailComponent,
    data: {
      oPermission: {
        permissionId: 'Piece-detail-permissions'
      }
    }
  },{
    path: ':local_piece_oid_nbr/ShipmentParty', loadChildren: () => import('../ShipmentParty/ShipmentParty.module').then(m => m.ShipmentPartyModule),
    data: {
        oPermission: {
            permissionId: 'ShipmentParty-detail-permissions'
        }
    }
}
];

export const PIECE_MODULE_DECLARATIONS = [
    PieceHomeComponent,
    PieceNewComponent,
    PieceDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PieceRoutingModule { }