import {Injector, AfterViewInit, Component, ViewChild } from '@angular/core';
import { OTableButtonComponent, OTableComponent, OntimizeService, DialogService } from 'ontimize-web-ngx';
import { OChartModule } from 'ontimize-web-ngx-charts';
import {OReportModule,OReportStoreService} from 'ontimize-web-ngx-report'
import { environment } from 'src/environments/environment';
@Component({
  selector: 'Entity-home',
  templateUrl: './Entity-home.component.html',
  styleUrls: ['./Entity-home.component.scss']
})
export class EntityHomeComponent implements AfterViewInit {

  @ViewChild('table', { static: true }) table: OTableComponent;

  @ViewChild('button')
  protected button: OTableButtonComponent;
  protected service: OntimizeService;
  protected dialogService: DialogService;

  ngAfterViewInit() {
    this.configureService();
    this.button.onClick.subscribe(event => {
      this.reportStoreService.openFillReport("94fa9d2a-e9cc-458a-a680-9bc576e14a38");
    });
  }

  protected configureService() {
    const conf = this.service.getDefaultServiceConfiguration();
    conf['path'] = '/Entity';
    this.service.configureService(conf);
  }
  constructor(protected injector: Injector,
    private reportStoreService: OReportStoreService)  {
    this.service = this.injector.get(OntimizeService);
    this.dialogService = this.injector.get(DialogService);
  }

  editionStarted(arg: any) {
    console.log('editionStarted');
    console.log(arg);
  }

  editionCancelled(arg: any) {
    console.log('editionCancelled');
    console.log(arg);
  }


  showAlert(alertMessage: any) {
    if (this.dialogService) {
      this.dialogService.alert('Success', alertMessage);
    }
  }
  editionCommitted(arg: any) {
    console.log('editionCommitted');
    console.log(arg);
  }
  importyaml(arg: any){
    console.log(environment.apiEndpoint +"/importyaml" );
    this.service.query({},
      [],
      'importyaml').subscribe((resp) => {
        console.log(JSON.stringify(resp));
        if (resp.code === 0) {
          console.log(resp.data);
          setTimeout(function () {}, 15000);
          this.showAlert("Imported Successfully");
        }
      });
  }
  exportyaml(arg: any){
    console.log(environment.apiEndpoint +"/exportyaml");
    this.service.query({},
      [],
      'exportyaml').subscribe((resp) => {
        console.log(JSON.stringify(resp));
        if (resp.code === 0) {
          console.log(resp.data);
          setTimeout(function () {}, 4000);
          this.showAlert("Exported Successfully");
        }
      });
  }
}