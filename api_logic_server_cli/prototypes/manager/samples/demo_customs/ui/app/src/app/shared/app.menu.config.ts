import { MenuRootItem } from 'ontimize-web-ngx';

import { CcpCustomerCardComponent } from './CcpCustomer-card/CcpCustomer-card.component';

import { PieceCardComponent } from './Piece-card/Piece-card.component';

import { ShipmentCardComponent } from './Shipment-card/Shipment-card.component';

import { ShipmentCommodityCardComponent } from './ShipmentCommodity-card/ShipmentCommodity-card.component';

import { ShipmentPartyCardComponent } from './ShipmentParty-card/ShipmentParty-card.component';

import { SpecialHandlingCardComponent } from './SpecialHandling-card/SpecialHandling-card.component';

import { SysConfigCardComponent } from './SysConfig-card/SysConfig-card.component';

import { VirtualRouteLegCardComponent } from './VirtualRouteLeg-card/VirtualRouteLeg-card.component';


export const MENU_CONFIG: MenuRootItem[] = [
    { id: 'home', name: 'HOME', icon: 'home', route: '/main/home' },
    
    {
    id: 'data', name: ' data', icon: 'remove_red_eye', opened: true,
    items: [
    
        { id: 'CcpCustomer', name: 'CCPCUSTOMER', icon: 'view_list', route: '/main/CcpCustomer' }
    
        ,{ id: 'Piece', name: 'PIECE', icon: 'view_list', route: '/main/Piece' }
    
        ,{ id: 'Shipment', name: 'SHIPMENT', icon: 'view_list', route: '/main/Shipment' }
    
        ,{ id: 'ShipmentCommodity', name: 'SHIPMENTCOMMODITY', icon: 'view_list', route: '/main/ShipmentCommodity' }
    
        ,{ id: 'ShipmentParty', name: 'SHIPMENTPARTY', icon: 'view_list', route: '/main/ShipmentParty' }
    
        ,{ id: 'SpecialHandling', name: 'SPECIALHANDLING', icon: 'view_list', route: '/main/SpecialHandling' }
    
        ,{ id: 'SysConfig', name: 'SYSCONFIG', icon: 'view_list', route: '/main/SysConfig' }
    
        ,{ id: 'VirtualRouteLeg', name: 'VIRTUALROUTELEG', icon: 'view_list', route: '/main/VirtualRouteLeg' }
    
    ] 
},
    
    { id: 'settings', name: 'Settings', icon: 'settings', route: '/main/settings'}
    ,{ id: 'about', name: 'About', icon: 'info', route: '/main/about'}
    ,{ id: 'logout', name: 'LOGOUT', route: '/login', icon: 'power_settings_new', confirm: 'yes' }
];

export const MENU_COMPONENTS = [

    CcpCustomerCardComponent

    ,PieceCardComponent

    ,ShipmentCardComponent

    ,ShipmentCommodityCardComponent

    ,ShipmentPartyCardComponent

    ,SpecialHandlingCardComponent

    ,SysConfigCardComponent

    ,VirtualRouteLegCardComponent

];