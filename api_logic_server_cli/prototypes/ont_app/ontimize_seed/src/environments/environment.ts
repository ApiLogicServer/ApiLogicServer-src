// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  //apiEndpoint: 'https://try.imatia.com/ontimizeweb/services/qsallcomponents-jee/services/rest',
  apiEndpoint: 'http://localhost:5656/api',
  production: false,
  versions: {
    core: '15.6.0-next.2',
    charts: '15.2.0-next.2',
    filemanager: '15.1.0-next.0',
    map: '15.0.0',
    report: '15.1.0-next.2'
  }
}
