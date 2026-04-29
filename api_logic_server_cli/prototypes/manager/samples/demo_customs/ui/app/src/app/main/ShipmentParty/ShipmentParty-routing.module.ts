import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ShipmentPartyHomeComponent } from './home/ShipmentParty-home.component';
import { ShipmentPartyNewComponent } from './new/ShipmentParty-new.component';
import { ShipmentPartyDetailComponent } from './detail/ShipmentParty-detail.component';

const routes: Routes = [
  {path: '', component: ShipmentPartyHomeComponent},
  { path: 'new', component: ShipmentPartyNewComponent },
  { path: ':shipment_party_oid_nbr', component: ShipmentPartyDetailComponent,
    data: {
      oPermission: {
        permissionId: 'ShipmentParty-detail-permissions'
      }
    }
  }
];

export const SHIPMENTPARTY_MODULE_DECLARATIONS = [
    ShipmentPartyHomeComponent,
    ShipmentPartyNewComponent,
    ShipmentPartyDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ShipmentPartyRoutingModule { }