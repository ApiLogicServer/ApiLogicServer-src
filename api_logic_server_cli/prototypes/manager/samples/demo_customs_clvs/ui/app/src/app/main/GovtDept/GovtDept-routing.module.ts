import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GovtDeptHomeComponent } from './home/GovtDept-home.component';
import { GovtDeptNewComponent } from './new/GovtDept-new.component';
import { GovtDeptDetailComponent } from './detail/GovtDept-detail.component';

const routes: Routes = [
  {path: '', component: GovtDeptHomeComponent},
  { path: 'new', component: GovtDeptNewComponent },
  { path: ':id', component: GovtDeptDetailComponent,
    data: {
      oPermission: {
        permissionId: 'GovtDept-detail-permissions'
      }
    }
  },{
    path: ':govt_dept_id/ControlledRegulatedGood', loadChildren: () => import('../ControlledRegulatedGood/ControlledRegulatedGood.module').then(m => m.ControlledRegulatedGoodModule),
    data: {
        oPermission: {
            permissionId: 'ControlledRegulatedGood-detail-permissions'
        }
    }
}
];

export const GOVTDEPT_MODULE_DECLARATIONS = [
    GovtDeptHomeComponent,
    GovtDeptNewComponent,
    GovtDeptDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GovtDeptRoutingModule { }