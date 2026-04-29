import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ShipmentCommodityHomeComponent } from './home/ShipmentCommodity-home.component';
import { ShipmentCommodityNewComponent } from './new/ShipmentCommodity-new.component';
import { ShipmentCommodityDetailComponent } from './detail/ShipmentCommodity-detail.component';

const routes: Routes = [
  {path: '', component: ShipmentCommodityHomeComponent},
  { path: 'new', component: ShipmentCommodityNewComponent },
  { path: ':local_shipment_oid_nbr/:sequence_nbr', component: ShipmentCommodityDetailComponent,
    data: {
      oPermission: {
        permissionId: 'ShipmentCommodity-detail-permissions'
      }
    }
  }
];

export const SHIPMENTCOMMODITY_MODULE_DECLARATIONS = [
    ShipmentCommodityHomeComponent,
    ShipmentCommodityNewComponent,
    ShipmentCommodityDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ShipmentCommodityRoutingModule { }