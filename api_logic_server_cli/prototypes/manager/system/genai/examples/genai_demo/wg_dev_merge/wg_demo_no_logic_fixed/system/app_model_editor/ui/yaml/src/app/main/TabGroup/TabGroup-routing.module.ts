import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { TabGroupHomeComponent } from './home/TabGroup-home.component';
import { TabGroupNewComponent } from './new/TabGroup-new.component';
import { TabGroupDetailComponent } from './detail/TabGroup-detail.component';

const routes: Routes = [
  {path: '', component: TabGroupHomeComponent},
  { path: 'new', component: TabGroupNewComponent },
  { path: ':entity_name/:tab_entity/:direction/:name', component: TabGroupDetailComponent,
    data: {
      oPermission: {
        permissionId: 'TabGroup-detail-permissions'
      }
    }
  }
];

export const TABGROUP_MODULE_DECLARATIONS = [
    TabGroupHomeComponent,
    TabGroupNewComponent,
    TabGroupDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class TabGroupRoutingModule { }