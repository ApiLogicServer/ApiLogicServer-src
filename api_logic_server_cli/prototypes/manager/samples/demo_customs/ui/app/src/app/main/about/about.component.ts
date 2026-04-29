import { Component } from '@angular/core';

import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-about',
  templateUrl: './about.component.html',
  styleUrls: ['./about.component.scss']
})
export class AboutComponent {

  public vCore: string = environment.versions.core;
  public vCharts: string = environment.versions.charts;
  public vFilemanager: string = environment.versions.filemanager;
  public vMap: string = environment.versions.map;
  public vReport: string = environment.versions.report;
}
