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
      
    
        { path: 'CcpCustomer', loadChildren: () => import('./CcpCustomer/CcpCustomer.module').then(m => m.CcpCustomerModule) },
    
        { path: 'Piece', loadChildren: () => import('./Piece/Piece.module').then(m => m.PieceModule) },
    
        { path: 'Shipment', loadChildren: () => import('./Shipment/Shipment.module').then(m => m.ShipmentModule) },
    
        { path: 'ShipmentCommodity', loadChildren: () => import('./ShipmentCommodity/ShipmentCommodity.module').then(m => m.ShipmentCommodityModule) },
    
        { path: 'ShipmentParty', loadChildren: () => import('./ShipmentParty/ShipmentParty.module').then(m => m.ShipmentPartyModule) },
    
        { path: 'SpecialHandling', loadChildren: () => import('./SpecialHandling/SpecialHandling.module').then(m => m.SpecialHandlingModule) },
    
        { path: 'SysConfig', loadChildren: () => import('./SysConfig/SysConfig.module').then(m => m.SysConfigModule) },
    
        { path: 'VirtualRouteLeg', loadChildren: () => import('./VirtualRouteLeg/VirtualRouteLeg.module').then(m => m.VirtualRouteLegModule) },
    
    ]
  }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MainRoutingModule { }