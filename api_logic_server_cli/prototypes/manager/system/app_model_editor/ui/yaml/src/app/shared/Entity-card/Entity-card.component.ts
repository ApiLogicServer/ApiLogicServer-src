import { Component, ViewEncapsulation, CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';
import {  MultiBarHorizontalChartConfiguration } from 'ontimize-web-ngx-charts';
import { Constants } from '../constant';


@Component({
  selector: 'transactions-card',
  templateUrl: './Entity-card.component.html',
  styleUrls: ['./Entity-card.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.Entity-card]': 'true'
  }
})


export class EntityCardComponent {

  public chartParameters: MultiBarHorizontalChartConfiguration;
  public scheme;
  constructor(  ) {
    this.chartParameters = new MultiBarHorizontalChartConfiguration();
    this.chartParameters.showLegend = false;
    this.chartParameters.height = 150;
    this.chartParameters.width = 250;
    this.chartParameters.showControls = false;
    this.chartParameters.y1Axis.showMaxMin = false;
    this.chartParameters.x1Axis.showMaxMin = false;
    this.chartParameters.showYAxis = true;
    this.chartParameters.showXAxis = false;
    this.chartParameters.margin.top = 0;
    this.chartParameters.margin.right = 0;
    this.chartParameters.margin.bottom = 0;
    this.chartParameters.margin.left = 60;
    this.chartParameters.yDataType = 'intGrouped';
    this.chartParameters.valueType = 'intGrouped';
    this.chartParameters.showTooltip = false;
    this.scheme = { domain: ['#eeeeee', Constants.THEME.accent, '#c5c5c5'] };
  }
}