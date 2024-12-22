import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GlobalSettingHomeComponent } from './home/GlobalSetting-home.component';
import { GlobalSettingNewComponent } from './new/GlobalSetting-new.component';
import { GlobalSettingDetailComponent } from './detail/GlobalSetting-detail.component';

const routes: Routes = [
  {path: '', component: GlobalSettingHomeComponent},
  { path: 'new', component: GlobalSettingNewComponent },
  { path: ':name', component: GlobalSettingDetailComponent,
    data: {
      oPermission: {
        permissionId: 'GlobalSetting-detail-permissions'
      }
    }
  }
];

export const GLOBALSETTING_MODULE_DECLARATIONS = [
    GlobalSettingHomeComponent,
    GlobalSettingNewComponent,
    GlobalSettingDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GlobalSettingRoutingModule { }