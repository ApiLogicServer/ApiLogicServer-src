import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { YamlFilesHomeComponent } from './home/YamlFiles-home.component';
import { YamlFilesNewComponent } from './new/YamlFiles-new.component';
import { YamlFilesDetailComponent } from './detail/YamlFiles-detail.component';

const routes: Routes = [
  {path: '', component: YamlFilesHomeComponent},
  { path: 'new', component: YamlFilesNewComponent },
  { path: ':name', component: YamlFilesDetailComponent,
    data: {
      oPermission: {
        permissionId: 'YamlFiles-detail-permissions'
      }
    }
  }
];

export const YAMLFILES_MODULE_DECLARATIONS = [
    YamlFilesHomeComponent,
    YamlFilesNewComponent,
    YamlFilesDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class YamlFilesRoutingModule { }