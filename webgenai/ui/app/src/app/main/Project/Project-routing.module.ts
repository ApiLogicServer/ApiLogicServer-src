import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProjectHomeComponent } from './home/Project-home.component';
import { ProjectNewComponent } from './new/Project-new.component';
import { ProjectDetailComponent } from './detail/Project-detail.component';

const routes: Routes = [
  {path: '', component: ProjectHomeComponent},
  { path: 'new', component: ProjectNewComponent },
  { path: ':id', component: ProjectDetailComponent,
    data: {
      oPermission: {
        permissionId: 'Project-detail-permissions'
      }
    }
  },{
    path: ':project_id/File', loadChildren: () => import('../File/File.module').then(m => m.FileModule),
    data: {
        oPermission: {
            permissionId: 'File-detail-permissions'
        }
    }
}
];

export const PROJECT_MODULE_DECLARATIONS = [
    ProjectHomeComponent,
    ProjectNewComponent,
    ProjectDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ProjectRoutingModule { }