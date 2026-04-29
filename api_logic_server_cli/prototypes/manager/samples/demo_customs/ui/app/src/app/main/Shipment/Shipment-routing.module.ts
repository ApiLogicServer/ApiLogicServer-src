import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ShipmentHomeComponent } from './home/Shipment-home.component';
import { ShipmentNewComponent } from './new/Shipment-new.component';
import { ShipmentDetailComponent } from './detail/Shipment-detail.component';

const routes: Routes = [
  {path: '', component: ShipmentHomeComponent},
  { path: 'new', component: ShipmentNewComponent },
  { path: ':local_shipment_oid_nbr', component: ShipmentDetailComponent,
    data: {
      oPermission: {
        permissionId: 'Shipment-detail-permissions'
      }
    }
  },{
    path: ':local_shipment_oid_nbr/Piece', loadChildren: () => import('../Piece/Piece.module').then(m => m.PieceModule),
    data: {
        oPermission: {
            permissionId: 'Piece-detail-permissions'
        }
    }
},{
    path: ':local_shipment_oid_nbr/ShipmentCommodity', loadChildren: () => import('../ShipmentCommodity/ShipmentCommodity.module').then(m => m.ShipmentCommodityModule),
    data: {
        oPermission: {
            permissionId: 'ShipmentCommodity-detail-permissions'
        }
    }
},{
    path: ':local_shipment_oid_nbr/ShipmentParty', loadChildren: () => import('../ShipmentParty/ShipmentParty.module').then(m => m.ShipmentPartyModule),
    data: {
        oPermission: {
            permissionId: 'ShipmentParty-detail-permissions'
        }
    }
},{
    path: ':oid_nbr/SpecialHandling', loadChildren: () => import('../SpecialHandling/SpecialHandling.module').then(m => m.SpecialHandlingModule),
    data: {
        oPermission: {
            permissionId: 'SpecialHandling-detail-permissions'
        }
    }
}
];

export const SHIPMENT_MODULE_DECLARATIONS = [
    ShipmentHomeComponent,
    ShipmentNewComponent,
    ShipmentDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ShipmentRoutingModule { }