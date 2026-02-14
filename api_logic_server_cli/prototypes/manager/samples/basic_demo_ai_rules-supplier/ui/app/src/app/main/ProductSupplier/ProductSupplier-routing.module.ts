import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductSupplierHomeComponent } from './home/ProductSupplier-home.component';
import { ProductSupplierNewComponent } from './new/ProductSupplier-new.component';
import { ProductSupplierDetailComponent } from './detail/ProductSupplier-detail.component';

const routes: Routes = [
  {path: '', component: ProductSupplierHomeComponent},
  { path: 'new', component: ProductSupplierNewComponent },
  { path: ':id', component: ProductSupplierDetailComponent,
    data: {
      oPermission: {
        permissionId: 'ProductSupplier-detail-permissions'
      }
    }
  }
];

export const PRODUCTSUPPLIER_MODULE_DECLARATIONS = [
    ProductSupplierHomeComponent,
    ProductSupplierNewComponent,
    ProductSupplierDetailComponent 
];


@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ProductSupplierRoutingModule { }