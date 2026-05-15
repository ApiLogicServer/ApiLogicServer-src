import { Component, ViewChild, ViewEncapsulation } from '@angular/core';
import { MatRadioChange } from '@angular/material/radio';
import { MatSlideToggle, MatSlideToggleChange } from '@angular/material/slide-toggle';
import { AppConfig, AppearanceService, OTranslateService, Util } from 'ontimize-web-ngx';


@Component({
  selector: 'app-settings',
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss'],
  encapsulation: ViewEncapsulation.None,
  host: {
    '[class.app-settings]': 'true'
  }
})
export class SettingsComponent {

  public availableLangs: string[] = [];
  public currentLang: string;
  public darkDefaultMode = false;

  @ViewChild('toggleDark')
  private toggleDark: MatSlideToggle;

  constructor(
    private _appConfig: AppConfig,
    private _translateService: OTranslateService,
    private appearanceService: AppearanceService
  ) {
    this.darkDefaultMode = this.appearanceService.isDarkMode();
    this.availableLangs = this._appConfig.getConfiguration().applicationLocales;
    this.currentLang = this._translateService.getCurrentLang();
  }

  changeLang(e: MatRadioChange): void {
    if (this._translateService && this._translateService.getCurrentLang() !== e.value) {
      this._translateService.use(e.value);
    }
  }


  changeDarkMode(e: MatSlideToggleChange): void {
    this.appearanceService.setDarkMode(e.checked);
  }

}
