import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { VirtualRouteLegHomeComponent } from './home/VirtualRouteLeg-home.component';
import { VirtualRouteLegNewComponent } from './new/VirtualRouteLeg-new.component';
import { VirtualRouteLegDetailComponent } from './detail/VirtualRouteLeg-detail.component';

const routes: Routes = [
  {path: '', component: VirtualRouteLegHomeComponent},
  { path: 'new', component: VirtualRouteLegNewComponent },
  { path: ':id', component: VirtualRouteLegDetailComponent,
    data: {
      oPermission: {
        permissionId: 'VirtualRouteLeg-detail-permissions'
      }
    }
  }
];

export const VIRTUALROUTELEG_MODULE_DECLARATIONS = [
    VirtualRouteLegHomeComponent,
    VirtualRouteLegNewComponent,
    VirtualRouteLegDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class VirtualRouteLegRoutingModule { }