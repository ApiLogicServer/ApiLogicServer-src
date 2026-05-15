import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { CcpCustomerHomeComponent } from './home/CcpCustomer-home.component';
import { CcpCustomerNewComponent } from './new/CcpCustomer-new.component';
import { CcpCustomerDetailComponent } from './detail/CcpCustomer-detail.component';

const routes: Routes = [
  {path: '', component: CcpCustomerHomeComponent},
  { path: 'new', component: CcpCustomerNewComponent },
  { path: ':id', component: CcpCustomerDetailComponent,
    data: {
      oPermission: {
        permissionId: 'CcpCustomer-detail-permissions'
      }
    }
  }
];

export const CCPCUSTOMER_MODULE_DECLARATIONS = [
    CcpCustomerHomeComponent,
    CcpCustomerNewComponent,
    CcpCustomerDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class CcpCustomerRoutingModule { }