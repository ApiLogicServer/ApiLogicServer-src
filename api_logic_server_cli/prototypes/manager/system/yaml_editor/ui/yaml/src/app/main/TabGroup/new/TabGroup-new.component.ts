import { Component, Injector } from '@angular/core';
import { NavigationService } from 'ontimize-web-ngx';

@Component({
  selector: 'TabGroup-new',
  templateUrl: './TabGroup-new.component.html',
  styleUrls: ['./TabGroup-new.component.scss']
})
export class TabGroupNewComponent {

  constructor(protected injector: Injector) {
    this.injector.get(NavigationService).initialize();
  }
  
  public DirectionArray = [{
    code: "toone"   
  }, {
    code: "tomany"
  }];

  public selectedDirection = "tomany";
}