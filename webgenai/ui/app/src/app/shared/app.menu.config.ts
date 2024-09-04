import { MenuRootItem } from 'ontimize-web-ngx';

import { FileCardComponent } from './File-card/File-card.component';

import { ProjectCardComponent } from './Project-card/Project-card.component';

import { UserCardComponent } from './User-card/User-card.component';


export const MENU_CONFIG: MenuRootItem[] = [
    { id: 'home', name: 'HOME', icon: 'home', route: '/main/home' },
    
    {
    id: 'data', name: ' data', icon: 'remove_red_eye', opened: true,
    items: [
    
        { id: 'File', name: 'FILE', icon: 'view_list', route: '/main/File' }
    
        ,{ id: 'Project', name: 'PROJECT', icon: 'view_list', route: '/main/Project' }
    
        ,{ id: 'User', name: 'USER', icon: 'view_list', route: '/main/User' }
    
    ] 
},
    
    { id: 'settings', name: 'Settings', icon: 'settings', route: '/main/settings'}
    ,{ id: 'about', name: 'About', icon: 'info', route: '/main/about'}
    ,{ id: 'logout', name: 'LOGOUT', route: '/login', icon: 'power_settings_new', confirm: 'yes' }
];

export const MENU_COMPONENTS = [

    FileCardComponent

    ,ProjectCardComponent

    ,UserCardComponent

];