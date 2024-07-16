import { CdkDragDrop, moveItemInArray } from '@angular/cdk/drag-drop';
import {
  ChangeDetectionStrategy,
  ChangeDetectorRef,
  Component,
  Inject,
  Injector,
  Type,
  ViewEncapsulation
} from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import{DialogService, OTranslateService, Codes, Util, OColumn, OTableBase} from  'ontimize-web-ngx';
//import { DialogService } from '../../../../../services/dialog.service';
//import { OTranslateService } from '../../../../../services/translate/o-translate.service';
//import { Codes } from '../../../../../util/codes';
//import { Util } from '../../../../../util/util';
//import type { OColumn } from '../../../column/o-column.class';
//import { OTableBase } from '../../../o-table-base.class';

export type ColumnVisibilityConfiguration = {
  attr: string;
  title: string;
  visible: boolean;
  deleteValueFilter?: boolean;
  deleteSortColummn?: boolean;
  deleteGrupingColumn?: boolean;
};

@Component({
  selector: 'o-table-visible-columns-dialog',
  templateUrl: 'o-table-visible-columns-dialog.component.html',
  styleUrls: ['o-table-visible-columns-dialog.component.scss'],
  encapsulation: ViewEncapsulation.None,
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    '[class.o-table-visible-columns-dialog]': 'true'
  }
})
export class OTableVisibleColumnsDialogComponent {

  columns: ColumnVisibilityConfiguration[] = [];
  rowHeight: string = Codes.DEFAULT_ROW_HEIGHT;
  protected dialogService: DialogService;
  protected cd: ChangeDetectorRef;
  protected translateService: OTranslateService;
  protected activeColumnValueFilters: string[] = [];
  protected activeSortColumns: string[] = [];
  protected activeGroupByColumns: string[] = [];
  protected table: OTableBase;
  constructor(
    protected injector: Injector,
    public dialogRef: MatDialogRef<OTableVisibleColumnsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any
  ) {
    this.dialogService = this.injector.get<DialogService>(DialogService as Type<DialogService>);
    this.cd = this.injector.get<ChangeDetectorRef>(ChangeDetectorRef as Type<ChangeDetectorRef>);
    this.translateService = this.injector.get<OTranslateService>(OTranslateService as Type<OTranslateService>);

    if (Util.isDefined(data.table)) {
      this.table = data.table;

      const visibleColumns = Util.parseArray(this.table.visibleColumns, true);
      const nonHidableColumns = Util.parseArray(this.table.nonHidableColumns, true);

      this.table.oTableOptions.columns.filter(oCol => (visibleColumns.indexOf(oCol.attr) !== -1 || oCol.definition !== undefined) &&
        nonHidableColumns.indexOf(oCol.attr) === -1
      ).forEach((oCol: OColumn) => {
        this.columns.push({
          attr: oCol.attr,
          title: oCol.title,
          visible: oCol.visible
        });
      });

      this.rowHeight = this.table.rowHeight;
      this.activeColumnValueFilters = this.table.dataSource.getColumnValueFilters().map(colValueFilter => colValueFilter.attr);
      this.activeSortColumns = this.table.sortColArray.map(col => col.columnName);
      this.activeGroupByColumns = this.table.groupedColumnsArray;
    }
  }

  onClickColumn(col: ColumnVisibilityConfiguration): void {
    const activeColFilter = this.activeColumnValueFilters.includes(col.attr);
    const activeSorting = this.activeSortColumns.includes(col.attr);
    const activeGrouping = this.activeGroupByColumns.includes(col.attr);
    if (col.visible && (activeColFilter || activeSorting || activeGrouping)) {
      const warnArgs = [];
      if (activeColFilter) {
        warnArgs.push(this.translateService.get('TABLE.VISIBLE_COLUMNS_DIALOG.VALUE_FILTER_WARN'));
      }
      if (activeSorting) {
        warnArgs.push(this.translateService.get('TABLE.VISIBLE_COLUMNS_DIALOG.SORT_WARN'));
      }
      if (activeGrouping) {
        warnArgs.push(this.translateService.get('TABLE.VISIBLE_COLUMNS_DIALOG.GROUPING_WARN'));
      }
      const dialogText = this.translateService.get('TABLE.VISIBLE_COLUMNS_DIALOG.HIDE_COLUMN_WARNING', warnArgs);
      this.dialogService.confirm('CONFIRM', dialogText).then(res => {
        if (res) {
          col.deleteValueFilter = activeColFilter;
          col.deleteSortColummn = activeSorting;
          col.deleteGrupingColumn = activeGrouping;
          col.visible = !col.visible;
          this.cd.detectChanges();
        }
      });
    } else {
      col.visible = !col.visible;
      if (col.visible) {
        col.deleteValueFilter = false;
        col.deleteSortColummn = false;
        col.deleteGrupingColumn = false;
      }
    }
  }

  drop(event: CdkDragDrop<string[]>) {
    moveItemInArray(this.columns, event.previousIndex, event.currentIndex);
  }

  closeDialog() {
    const columnSortingToRemove = this.getColumnSortingToRemove();
    const newSortColumns = columnSortingToRemove.length > 0 ?
      this.table.sortColArray.filter(col => !columnSortingToRemove.includes(col.columnName)) :
      undefined;

    const columnGroupingToRemove = this.getColumnGroupingToRemove();
    const newGroupColumns = columnGroupingToRemove.length > 0 ?
      this.table.groupedColumnsArray.filter(col => !columnGroupingToRemove.includes(col)) :
      undefined;

    this.dialogRef.close({
      visibleColArray: this.getVisibleColumns(),
      columnsOrder: this.getColumnsOrder(),
      sortColumns: newSortColumns,
      columnValueFiltersToRemove: this.getColumnValueFiltersToRemove(),
      groupColumns: newGroupColumns
    });
  }

  private getVisibleColumns(): string[] {
    return this.columns.filter(col => col.visible).map(col => col.attr);
  }

  private getColumnsOrder(): string[] {
    return this.columns.map(col => col.attr);
  }

  private getColumnValueFiltersToRemove(): string[] {
    return this.columns.filter(col => col.deleteValueFilter).map(col => col.attr);
  }

  private getColumnSortingToRemove(): string[] {
    return this.columns.filter(col => col.deleteSortColummn).map(col => col.attr);
  }

  private getColumnGroupingToRemove(): string[] {
    return this.columns.filter(col => col.deleteGrupingColumn).map(col => col.attr);
  }
}
