import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { OrderItemHomeComponent } from './home/OrderItem-home.component';
import { OrderItemNewComponent } from './new/OrderItem-new.component';
import { OrderItemDetailComponent } from './detail/OrderItem-detail.component';

const routes: Routes = [
  {path: '', component: OrderItemHomeComponent},
  { path: 'new', component: OrderItemNewComponent },
  { path: ':id', component: OrderItemDetailComponent,
    data: {
      oPermission: {
        permissionId: 'OrderItem-detail-permissions'
      }
    }
  }
];

export const ORDERITEM_MODULE_DECLARATIONS = [
    OrderItemHomeComponent,
    OrderItemNewComponent,
    OrderItemDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class OrderItemRoutingModule { }