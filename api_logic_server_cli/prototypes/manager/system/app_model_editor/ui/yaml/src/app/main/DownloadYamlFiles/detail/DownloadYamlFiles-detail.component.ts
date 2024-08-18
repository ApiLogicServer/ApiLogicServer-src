import { Injector, ViewChild, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { OFormComponent, OntimizeService, OTableComponent, OTextareaInputComponent } from 'ontimize-web-ngx';
import { DialogService } from 'ontimize-web-ngx';

@Component({
  selector: 'DownloadYamlFiles-detail',
  templateUrl: './DownloadYamlFiles-detail.component.html',
  styleUrls: ['./DownloadYamlFiles-detail.component.scss']
})
export class DownloadYamlFilesDetailComponent implements OnInit {
  protected service: OntimizeService;
  public data: any;
  public content: string;
  public downloaded: string;

  @ViewChild('yamlFile') yamlFile: OFormComponent;
  @ViewChild('downloadedFile') downloadedFile: OTextareaInputComponent;
  constructor(protected injector: Injector,
    protected dialogService: DialogService) {
    this.service = this.injector.get(OntimizeService);

  }

  ngOnInit() {
    this.configureService();
  }

  protected configureService() {
    const conf = this.service.getDefaultServiceConfiguration();
    conf['path'] = '/YamlFiles';
    this.service.configureService(conf);
  }
  onDataLoaded(e: object) {

    this.data = e;
    //console.log("OnDataLoad: " + JSON.stringify(this.data));
    this.content = this.data.content;
    this.downloaded = this.data.downloaded;
  }
  getContent(): string {
    //console.log("getValue " + this.content);
    if (!this.content) {
      return "foo bar";
    }
    return this.content;
  }
  getConverted(): string {
    //console.log("getValue " + this.content);
    if (!this.downloaded) {
      return "";
    }
    return this.downloaded;
  }
  download_yaml() {
    console.log("download_yaml");
    //this.service.update({ 'name': this.data.name }, { 'download_flag': true }, "YamlFiles").subscribe((resp) => {
      this.service.query({'name': this.data.name },
        [],
        'downloadyaml').subscribe((resp) => {
      console.log("downloaded: " + JSON.stringify(resp.data));
      if (resp.code === 0) {
        this.data.downloaded = JSON.stringify(resp.data);
        this.showDownloadInfo();
        //this.yamlFile.reload();
      } else {
        console.error(resp);
      }
    });
  }
  showDownloadInfo() {
    if (this.dialogService) {
      this.dialogService.info('Yaml File Downloaded',
        'The Yaml "converted content" has been downloaded (press Refresh if not visible)',);
    }
  }
  reload_yaml() {
      console.log("reload_yaml");
      this.service.query({'name': this.data.name },
        [],
        'reloadyaml').subscribe((resp) => {
          console.log("reload_yaml: " + JSON.stringify(resp.data));
          if (resp.code === 0) {
            this.showReloadInfo();
          } else {
            console.error(resp);
          }
        });
    }
    showReloadInfo(){
      if(this.dialogService) {
      this.dialogService.info('Yaml File Reloaded',
        'The Yaml "downloaded content" has been reprocessed (Reloaded Entities, Attributes, Relationships)',);
    }
  }
}