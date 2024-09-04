import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FileHomeComponent } from './home/File-home.component';
import { FileNewComponent } from './new/File-new.component';
import { FileDetailComponent } from './detail/File-detail.component';

const routes: Routes = [
  {path: '', component: FileHomeComponent},
  { path: 'new', component: FileNewComponent },
  { path: ':id', component: FileDetailComponent,
    data: {
      oPermission: {
        permissionId: 'File-detail-permissions'
      }
    }
  }
];

export const FILE_MODULE_DECLARATIONS = [
    FileHomeComponent,
    FileNewComponent,
    FileDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class FileRoutingModule { }