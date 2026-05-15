import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SpecialHandlingHomeComponent } from './home/SpecialHandling-home.component';
import { SpecialHandlingNewComponent } from './new/SpecialHandling-new.component';
import { SpecialHandlingDetailComponent } from './detail/SpecialHandling-detail.component';

const routes: Routes = [
  {path: '', component: SpecialHandlingHomeComponent},
  { path: 'new', component: SpecialHandlingNewComponent },
  { path: ':id', component: SpecialHandlingDetailComponent,
    data: {
      oPermission: {
        permissionId: 'SpecialHandling-detail-permissions'
      }
    }
  }
];

export const SPECIALHANDLING_MODULE_DECLARATIONS = [
    SpecialHandlingHomeComponent,
    SpecialHandlingNewComponent,
    SpecialHandlingDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class SpecialHandlingRoutingModule { }