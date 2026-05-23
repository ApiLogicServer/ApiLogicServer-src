import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CustomsOfficeHomeComponent } from './home/CustomsOffice-home.component';
import { CustomsOfficeNewComponent } from './new/CustomsOffice-new.component';
import { CustomsOfficeDetailComponent } from './detail/CustomsOffice-detail.component';

const routes: Routes = [
  {path: '', component: CustomsOfficeHomeComponent},
  { path: 'new', component: CustomsOfficeNewComponent },
  { path: ':id', component: CustomsOfficeDetailComponent,
    data: {
      oPermission: {
        permissionId: 'CustomsOffice-detail-permissions'
      }
    }
  }
];

export const CUSTOMSOFFICE_MODULE_DECLARATIONS = [
    CustomsOfficeHomeComponent,
    CustomsOfficeNewComponent,
    CustomsOfficeDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CustomsOfficeRoutingModule { }