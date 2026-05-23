import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ControlledRegulatedGoodHomeComponent } from './home/ControlledRegulatedGood-home.component';
import { ControlledRegulatedGoodNewComponent } from './new/ControlledRegulatedGood-new.component';
import { ControlledRegulatedGoodDetailComponent } from './detail/ControlledRegulatedGood-detail.component';

const routes: Routes = [
  {path: '', component: ControlledRegulatedGoodHomeComponent},
  { path: 'new', component: ControlledRegulatedGoodNewComponent },
  { path: ':id', component: ControlledRegulatedGoodDetailComponent,
    data: {
      oPermission: {
        permissionId: 'ControlledRegulatedGood-detail-permissions'
      }
    }
  },{
    path: ':controlled_regulated_goods_id/ShipmentCommodity', loadChildren: () => import('../ShipmentCommodity/ShipmentCommodity.module').then(m => m.ShipmentCommodityModule),
    data: {
        oPermission: {
            permissionId: 'ShipmentCommodity-detail-permissions'
        }
    }
}
];

export const CONTROLLEDREGULATEDGOOD_MODULE_DECLARATIONS = [
    ControlledRegulatedGoodHomeComponent,
    ControlledRegulatedGoodNewComponent,
    ControlledRegulatedGoodDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ControlledRegulatedGoodRoutingModule { }