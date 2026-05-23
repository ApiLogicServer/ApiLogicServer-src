import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CustomsRegionHomeComponent } from './home/CustomsRegion-home.component';
import { CustomsRegionNewComponent } from './new/CustomsRegion-new.component';
import { CustomsRegionDetailComponent } from './detail/CustomsRegion-detail.component';

const routes: Routes = [
  {path: '', component: CustomsRegionHomeComponent},
  { path: 'new', component: CustomsRegionNewComponent },
  { path: ':id', component: CustomsRegionDetailComponent,
    data: {
      oPermission: {
        permissionId: 'CustomsRegion-detail-permissions'
      }
    }
  },{
    path: ':customs_region_id/CustomsOffice', loadChildren: () => import('../CustomsOffice/CustomsOffice.module').then(m => m.CustomsOfficeModule),
    data: {
        oPermission: {
            permissionId: 'CustomsOffice-detail-permissions'
        }
    }
}
];

export const CUSTOMSREGION_MODULE_DECLARATIONS = [
    CustomsRegionHomeComponent,
    CustomsRegionNewComponent,
    CustomsRegionDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CustomsRegionRoutingModule { }