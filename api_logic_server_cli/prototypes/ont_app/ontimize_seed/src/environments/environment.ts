// This file can be replaced during build by using the `fileReplacements` array.
// `ng build --prod` replaces `environment.ts` with `environment.prod.ts`.
// The list of file replacements can be found in `angular.json`.

export const environment = {
  //apiEndpoint: 'https://try.imatia.com/ontimizeweb/services/qsallcomponents-jee/services/rest',
  apiEndpoint: 'http://localhost:5656/ontimizeweb/services/qsallcomponents-jee/services/rest',
  production: false,
  versions: {
    core: '15.0.0-rc.o',
    charts: '"15.0.0-beta.1',
    filemanager: '15.0.0-beta.0',
    map: '15.0.0-beta.1',
    report: '15.0.0-beta.1'
  }
}
