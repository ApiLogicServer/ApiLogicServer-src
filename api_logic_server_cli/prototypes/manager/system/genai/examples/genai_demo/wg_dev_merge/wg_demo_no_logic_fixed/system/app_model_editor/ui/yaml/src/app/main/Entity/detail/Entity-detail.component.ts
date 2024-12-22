import { Injector, ViewChild, Component, OnInit, ViewEncapsulation } from '@angular/core';
import { OTableVisibleColumnsDialogComponent, OButtonComponent, OFormComponent, OntimizeService, OListPickerComponent, OTableComponent, OColumn, OTableOptions, DialogService} from 'ontimize-web-ngx';
import { environment } from 'src/environments/environment';
//import { OTableVisibleColumnsDialogComponent } from './visible-columns/o-table-visible-columns-dialog.component';  // This import is missing in the original file  
import { MatDialog } from '@angular/material/dialog';

@Component({
  selector: 'Entity-detail',
  templateUrl: './Entity-detail.component.html',
  styleUrls: ['./Entity-detail.component.scss']
})
export class EntityDetailComponent implements OnInit  {
  protected service: any;
  protected entity: any;
  protected dialogService: any;
  protected dialog: any
  //protected cd: ChangeDetectorRef,
  

  @ViewChild('table', { static: true }) table: OTableComponent;

  @ViewChild('button')
  protected button: OButtonComponent;

  @ViewChild('oDetailForm') form: OFormComponent;
  
  constructor(protected injector: Injector)  {
    this.service = this.injector.get(OntimizeService);
    this.dialogService = this.injector.get(DialogService);
    this.dialog = this.injector.get(MatDialog);
  }
  ngOnInit() {
    //this.configureService();
  }
  ngAfterViewInit() {
   // this.showHideColumns();
  }
  protected configureService() {
    const conf = this.service.getDefaultServiceConfiguration();
    conf['path'] = '/Entity';
    this.service.configureService(conf);
  }
  onDataLoaded(e: object) {
    console.log(JSON.stringify(e));
    this.entity = e;
  }
  
  showHideColumns() {
    // TODO - get the attributes for this table and pass them to the dialog
    // columns: ColumnVisibilityConfiguration[] = [];
    // Each column should have the following properties:
    //  attr: oCol.attr,
    //  title: oCol.label,
    //  visible: oCol.visible
    const columnVisibilityConfiguration = []
    const oCol: OColumn = new OColumn();
    oCol.attr = 'column1';
    oCol.title = 'Column 1';
    oCol.visible = true;
    columnVisibilityConfiguration.push(oCol);
    //this.table.oTableOptions.columns = columnVisibilityConfiguration;
    //this.table.oTableOptions.visibleColumns = ["column1"];
    //this.table.visibleColumns = "column1";
    //this.table.columns = "column1"
    //this.table.visibleColArray = ["column1"];
    console.log("Show/Hide VisibleColumns:", this.table.visibleColumns);
    console.log("Show/Hide Columns:", this.table.visibleColArray);
    console.log("Show/Hide TableOptions:", this.table.tableOptions);
    
    const dialogRef = this.dialog.open(OTableVisibleColumnsDialogComponent, {
      data: {
        table: this.table
      },
      maxWidth: '35vw',
      disableClose: true,
      panelClass: ['o-dialog-class', 'o-table-dialog']
    });
    // POST the new column visibility to the server and refresh the table
    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed', result);
    });
    dialogRef.componentInstance.onAccept.subscribe((data) => {
      console.log('onAccept', data);
    });  
  }
}