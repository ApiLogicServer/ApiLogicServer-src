import { MenuRootItem } from 'ontimize-web-ngx';

import { EntityCardComponent } from './Entity-card/Entity-card.component';

import { EntityAttrCardComponent } from './EntityAttr-card/EntityAttr-card.component';

import { GlobalSettingCardComponent } from './GlobalSetting-card/GlobalSetting-card.component';

import { TabGroupCardComponent } from './TabGroup-card/TabGroup-card.component';

import { TemplateCardComponent } from './Template-card/Template-card.component';

import { YamlFilesCardComponent } from './YamlFiles-card/YamlFiles-card.component';


export const MENU_CONFIG: MenuRootItem[] = [
    { id: 'home', name: 'HOME', icon: 'home', route: '/main/home' },
    { id: 'New YamlFiles', name: '1. Import Yaml File', icon: 'upload', route: '/main//YamlFiles/new' },
    { id: 'YamlFiles', name: '2. Process Yaml File', icon: 'upload_file', route: '/main/YamlFiles' },
    { id: 'data', name: '3. Edit Yaml Data', icon: 'edit_square', opened: true,
    items: [
        { id: 'Entity', name: 'Entities', icon: 'view_list', route: '/main/Entity' }
        ,{ id: 'EntityAttr', name: 'Attributes', icon: 'view_list', route: '/main/EntityAttr' }
        ,{ id: 'TabGroup', name: 'Relationships', icon: 'view_list', route: '/main/TabGroup' }
    
        ] 
    }
    ,{ id: 'YamlFiles', name: '4. Download Yaml File', icon: 'download_file', route: '/main/DownloadYamlFiles' }
    ,{ id: 'other', name: 'Global Settings', icon: 'remove_red_eye', opened: false,
    items: [        
        { id: 'GlobalSetting', name: 'Global Settings', icon: 'view_list', route: '/main/GlobalSetting' }
        ,{ id: 'Template', name: 'TEMPLATE', icon: 'view_list', route: '/main/Template' }
        ] 
    }

    ,{ id: 'settings', name: 'Settings', icon: 'settings', route: '/main/settings'}
    ,{ id: 'about', name: 'About', icon: 'info', route: '/main/about'}
    ,{ id: 'logout', name: 'LOGOUT', route: '/login', icon: 'power_settings_new', confirm: 'yes' }
];

export const MENU_COMPONENTS = [

    EntityCardComponent

    ,EntityAttrCardComponent

    ,GlobalSettingCardComponent

    ,TabGroupCardComponent

    ,TemplateCardComponent

    ,YamlFilesCardComponent

];