import { Component } from '@angular/core';
import { AppearanceService } from 'ontimize-web-ngx';

@Component({
  selector: 'o-app',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  constructor(private appearanceService: AppearanceService) {

  }
}
