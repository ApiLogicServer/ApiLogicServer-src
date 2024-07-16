import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EntityAttrHomeComponent } from './home/EntityAttr-home.component';
import { EntityAttrNewComponent } from './new/EntityAttr-new.component';
import { EntityAttrDetailComponent } from './detail/EntityAttr-detail.component';

const routes: Routes = [
  {path: '', component: EntityAttrHomeComponent},
  { path: 'new', component: EntityAttrNewComponent },
  { path: ':entity_name/:attr', component: EntityAttrDetailComponent,
    data: {
      oPermission: {
        permissionId: 'EntityAttr-detail-permissions'
      }
    }
  }
];

export const ENTITYATTR_MODULE_DECLARATIONS = [
    EntityAttrHomeComponent,
    EntityAttrNewComponent,
    EntityAttrDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class EntityAttrRoutingModule { }