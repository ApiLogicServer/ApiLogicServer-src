import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DownloadYamlFilesHomeComponent } from './home/DownloadYamlFiles-home.component';
import { DownloadYamlFilesDetailComponent } from './detail/DownloadYamlFiles-detail.component';

const routes: Routes = [
  {path: '', component: DownloadYamlFilesHomeComponent},
  { path: ':name', component: DownloadYamlFilesDetailComponent,
    data: {
      oPermission: {
        permissionId: 'DownloadYamlFiles-detail-permissions'
      }
    }
  }
];

export const DOWNLOAD_YAMLFILES_MODULE_DECLARATIONS = [
    DownloadYamlFilesHomeComponent,
    DownloadYamlFilesDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class DownloadYamlFilesRoutingModule { }