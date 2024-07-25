import { Injector, ViewChild, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { OFormComponent, OntimizeService, OListPickerComponent, OTableComponent, ORealPipe, ONIFInputComponent } from 'ontimize-web-ngx';


@Component({
  selector: 'YamlFiles-detail',
  templateUrl: './YamlFiles-detail.component.html',
  styleUrls: ['./YamlFiles-detail.component.scss']
})
export class YamlFilesDetailComponent implements OnInit  {
  protected service: OntimizeService;
  public data: any;
  public content: string;
  public downloaded: string;

  @ViewChild('oDetailForm') form: OFormComponent;
  
  constructor(protected injector: Injector) {
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
  process_yaml() {
    console.log("process_yaml");
    this.service.query({ 'id': this.data.id }, ['content'],"importyaml").subscribe((resp) => {
        if (resp.code === 0) {
          console.log("res: " + JSON.stringify(resp));
        }
      });
    }

}