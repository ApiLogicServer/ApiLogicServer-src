import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SysConfigHomeComponent } from './home/SysConfig-home.component';
import { SysConfigNewComponent } from './new/SysConfig-new.component';
import { SysConfigDetailComponent } from './detail/SysConfig-detail.component';

const routes: Routes = [
  {path: '', component: SysConfigHomeComponent},
  { path: 'new', component: SysConfigNewComponent },
  { path: ':id', component: SysConfigDetailComponent,
    data: {
      oPermission: {
        permissionId: 'SysConfig-detail-permissions'
      }
    }
  }
];

export const SYSCONFIG_MODULE_DECLARATIONS = [
    SysConfigHomeComponent,
    SysConfigNewComponent,
    SysConfigDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SysConfigRoutingModule { }