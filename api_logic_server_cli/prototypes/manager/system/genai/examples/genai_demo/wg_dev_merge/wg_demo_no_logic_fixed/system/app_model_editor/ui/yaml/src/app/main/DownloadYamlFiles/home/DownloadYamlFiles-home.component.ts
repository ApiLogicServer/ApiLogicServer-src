import { AfterViewInit, Component, ViewChild } from '@angular/core';
import { OTableButtonComponent, OTableComponent } from 'ontimize-web-ngx';
import { OChartModule } from 'ontimize-web-ngx-charts';
import {OReportModule,OReportStoreService} from 'ontimize-web-ngx-report'

@Component({
  selector: 'DownloadYamlFiles-home',
  templateUrl: './DownloadYamlFiles-home.component.html',
  styleUrls: ['./DownloadYamlFiles-home.component.scss']
})
export class DownloadYamlFilesHomeComponent implements AfterViewInit {

  @ViewChild('table', { static: true }) table: OTableComponent;

  @ViewChild('button')
  protected button: OTableButtonComponent;

  ngAfterViewInit() {
 
  }
}