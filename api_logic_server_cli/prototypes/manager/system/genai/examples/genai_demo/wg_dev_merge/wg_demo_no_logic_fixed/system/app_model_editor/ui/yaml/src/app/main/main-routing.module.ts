import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { MainComponent } from './main.component';

export const routes: Routes = [
  {
    path: '', component: MainComponent,
    children: [
        { path: '', redirectTo: 'home', pathMatch: 'full' },
        { path: 'about', loadChildren: () => import('./about/about.module').then(m => m.AboutModule) },
        { path: 'home', loadChildren: () => import('./home/home.module').then(m => m.HomeModule) },
        { path: 'settings', loadChildren: () => import('./settings/settings.module').then(m => m.SettingsModule) },
        { path: 'Entity', loadChildren: () => import('./Entity/Entity.module').then(m => m.EntityModule) },
        { path: 'EntityAttr', loadChildren: () => import('./EntityAttr/EntityAttr.module').then(m => m.EntityAttrModule) },
        { path: 'TabGroup', loadChildren: () => import('./TabGroup/TabGroup.module').then(m => m.TabGroupModule) },

        { path: 'GlobalSetting', loadChildren: () => import('./GlobalSetting/GlobalSetting.module').then(m => m.GlobalSettingModule) },
        { path: 'Template', loadChildren: () => import('./Template/Template.module').then(m => m.TemplateModule) },
    
        { path: 'YamlFiles', loadChildren: () => import('./YamlFiles/YamlFiles.module').then(m => m.YamlFilesModule) },
        { path: 'DownloadYamlFiles', loadChildren: () => import('./DownloadYamlFiles/DownloadYamlFiles.module').then(m => m.DownloadYamlFilesModule) },
    
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MainRoutingModule { }