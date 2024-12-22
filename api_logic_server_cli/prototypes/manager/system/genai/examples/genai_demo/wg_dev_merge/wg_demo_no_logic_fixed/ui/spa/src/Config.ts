import { compareVersions } from 'compare-versions';
import yaml from "js-yaml";

interface Config {
  api_root: string;
  authentication?: {
    keycloak?: {
      url: string;
      realm: string;
      clientId: string;
    };
    endpoint?: string;
    redirect?: any;
    sso?: any;
  };
  info?: any;
  about?: any;
  resources?: Record<string, any>;
  settings?: {
    locale?: string;
    max_list_columns?: number;
    HomeJS?: string;
    Home?: string;
  };
  ext_comp_url?: any;
  conf_source?: string | null | undefined;
  ui?: any;
  path?: string;
  info_toggle_checked?: boolean;
  server_msg?: string;
}

const initConf = (): void => {
  console.log("InitConf");
};

const getBrowserLocales = (
  options: { languageCodeOnly?: boolean } = {}
): string[] | undefined => {
  const defaultOptions = {
    languageCodeOnly: false,
  };
  const opt = {
    ...defaultOptions,
    ...options,
  };
  const browserLocales =
    navigator.languages === undefined
      ? [navigator.language]
      : navigator.languages;
  if (!browserLocales) {
    return undefined;
  }
  return browserLocales.map((locale) => {
    const trimmedLocale = locale.trim();
    return opt.languageCodeOnly ? trimmedLocale.split(/-|_/)[0] : trimmedLocale;
  });
};

export const getLSConf = (): Config => {
  let result: Config = getCurrentConf();
  let ls_conf: Config | null = null;
  try {
    ls_conf = getCurrentConf();
    result = ls_conf ?? result;
  } catch (e) {
    console.warn(`Failed to parse config `);
    localStorage.setItem("raconf", JSON.stringify(config));
  }

  //console.debug("LSConf", result);
  doTelemetry();
  return result;
};

export const doTelemetry = () => {
  const currentDate = new Date().toISOString();
  if(localStorage.getItem("telemetry")){
    return;
  }
  fetch('https://apifabric.ai/static2/tm?p='+document.location.href)
  .finally(() => {
    localStorage.setItem("telemetry", currentDate);
  })
}

const json2Conf = (conf: Config) => {
  let result = conf;
  if (!result.resources) {
    result.resources = {};
  }
  if (!result.settings) {
    result.settings = {};
  }
  const resourceEntries = Object.entries(result.resources);
  resourceEntries.sort((a, b) => (b.order || 0) - (a.order || 0))
  const resources = Object.fromEntries(resourceEntries);
  
  for (let [resource_name, resource] of Object.entries(resources || {})) {
    resource.relationships = resource.relationships || [];
    if (resource.tab_groups instanceof Array) {
      for (let tg of resource.tab_groups) {
        if (!tg.direction) {
          continue;
        }
        tg.target = tg.resource;
        resource.relationships.push(tg);
      }
    } else {
      for (let [tab_group_name, tab_group] of Object.entries(
        resource.tab_groups || {}
      )) {
        resource.relationships.push(
          Object.assign({}, tab_group as any, {
            name: tab_group_name,
            target: (tab_group as any).resource,
          })
        );
      }
    }

    if (
      !(
        resource.attributes instanceof Array ||
        resource.relationships instanceof Array
      )
    ) {
      continue;
    }

    if (!resource.type) {
      resource.type = resource_name;
    }

    resource.search_cols = [];
    resource.sort_attr_names = [];
    result.resources[resource_name].name = resource_name;
    let attributes = resource.attributes || [];

    for (let attr of attributes) {
      if (!(attr.constructor === Object)) {
        console.warn(`Invalid attribute ${attr}`);
        continue;
      }
      for (let rel of resource.relationships || []) {
        for (let fk of rel.fks || []) {
          if (attr.name === fk) {
            attr.relationship = rel;
            attr.relationship.target_resource =
              result.resources[attr.relationship.target] ||
              result.resources[attr.relationship.resource];
          }
        }
      }
      if (attr.search) {
        resource.search_cols.push(attr);
      }
      if (attr.sort) {
        if (attr.sort === "DESC") {
          resource.sort_attr_names.push("-" + attr.name);
        } else {
          resource.sort_attr_names.push(attr.name);
        }
        resource.sort = resource.sort_attr_names.join(",");
      }
      if (!attr.label) {
        attr.label =
          attr.relationship?.resource ||
          attr.name?.replace(/([A-Z])/g, " $1").replace(/(_)/g, " ");
      }
      attr.resource = resource;
    }
    if (resource.search_cols.length === 0) {
      resource.search_cols = attributes.filter(
        (col: any) =>
          col.name !== false &&
          (col.name === "id" ||
            col.name === resource.user_key ||
            col.name === "name")
      );
    }
    resource.max_list_columns =
      resource.max_list_columns || result.settings?.max_list_columns || 8;
  }

  if (result.settings) {
    result.settings.locale =
      result.settings.locale || getBrowserLocales()?.[0] || "fr-FR";
  }
  return result || resetConf(true);
};

export const useConf = (): Config => {
  let conf = getCurrentConf();
  if(document.location.hash.includes("/SPA")){
    // workaround to show/hide SPA resources in the webgenai SPA admin
    Object.entries(conf.resources || {}).forEach(([key, value]) => {
      if(value?.hidden){
        value.hidden = false;
      }
    })
  }
  return conf;
};

export const getConf = (): Config => {
  try {
    initConf();
  }
  catch(e){
    console.warn("Failed to init conf", e);
    return {};
  }
  return json2Conf(getLSConf());
};

export const resetConf = (reload: boolean) => {
  const configs: any = {};
  console.log("Resetting conf");
  localStorage.removeItem("raconf");
  configs[config.api_root] = config;
  setConfigs(configs);

  if (reload) {
    window.location.reload();
  }
  return config;
};


export const getKcUrl = (): string | undefined => {
  const conf: any = getCurrentConf();
  let authentication;
  try {
    authentication = conf.authentication;
  } catch (e) {
    console.warn("conf.authentication error");
  }
  if (!authentication?.kc_url) {
    return undefined;
  }
  return authentication?.kc_url;
};

export const getCurrentConf = (raw: boolean = false): Config => {
  const conf = sessionStorage.getItem("raconf") || localStorage.getItem("raconf") || "{}";
  let result = null;
  try {
    result = JSON.parse(conf);
  } catch (e) {
    console.warn("Failed to parse raconf", e);
  }
  if(raw) { return result; }
  return json2Conf(result);
};

const DEFAULT_YAML_URL = `/ui/admin/admin.yaml?v=${new Date().getTime()}`;

export const setCurrentConf = (conf: Config): boolean => {
  //console.debug("setCurrentConf", conf);
  if(conf.server_msg){
    console.log("Server Message", conf.server_msg);
    if(conf.server_msg.endsWith("reload")){
      // Check webgenie @app.route('/api/boot/')' for a reload message
      window.location.reload();
    }
  }
  if (!conf.api_root) {
    throw new Error(`No api_root in conf ${conf}`);
  }

  sessionStorage.setItem("raconf", JSON.stringify(conf));
  localStorage.setItem("raconf", JSON.stringify(conf));

  const stFndStr = "fetchedNonDefault";
  if (conf.about?.default && !sessionStorage.getItem(stFndStr)) {
    sessionStorage.setItem(stFndStr, "true");
    console.warn("default config - checking for " + DEFAULT_YAML_URL);
    loadYaml(DEFAULT_YAML_URL); // async!!
  } else if(!conf.path) {
    conf.path = window.location.pathname.split("#")[0];
    const configs = getConfigs();
    configs[conf.api_root] = conf;
    setConfigs(configs);
  }
  return true;
};

export const getConfigs = (): { [key: string]: Config } => {
  let result;
  try {
    result = JSON.parse(localStorage.getItem("raconfigs") || "{}");
  } catch (e) {
    console.warn("Failed to parse raconfigs", e);
    result = {};
  }
  console.debug("getConfigs", result);
  return result;
};

export const setConfigs = (configs: any) => {
  localStorage.setItem("raconfigs", JSON.stringify(configs));
};

export const getProjectId = () => {
  /*
  Check if the path is a project id, used for apifabric..
  */
  let id = window.location.pathname.split("/")[1];
  if (!id || id === "index.html" || id === "admin-app" || !id.startsWith("0")) {
    id = "";
  }
  return id;
};

export const needsReload = () => {
  // check if a reload is needed, only once per session
  let result = localStorage.getItem("autoReload") && !(sessionStorage.getItem("autoReloaded") === window.location.pathname)
  sessionStorage.setItem("autoReloaded", window.location.pathname);
  const minVersion = localStorage.getItem("minVersion");
  const currentVersion = getCurrentConf().about?.version;
    
  if(minVersion){
    if(compareVersions(currentVersion, minVersion) < 0){
      console.log("Version mismatch, reloading", currentVersion, minVersion);
      result = true;
    }
  }
  console.log("needsReload", result, currentVersion, minVersion);
  return result;
}

export const loadHomeConf = async () => {
  const currentConf = getCurrentConf();
  const storedConfigs = localStorage.getItem("raconfigs");
  const id = getProjectId();
  let configs = storedConfigs ? JSON.parse(storedConfigs) : {};
  let found = false;
  console.debug("loadHomeConf path:", window.location.pathname);

  for (let root in configs) {
    let conf = configs[root];
    
    if (conf.path === window.location.pathname.split("#")[0]) {
      console.log("loadHomeConf conf:", conf);
      if (found) {
        console.warn("Multiple configs found for path", conf.path);
      }
      found = true;
      setCurrentConf(conf);
    }
  }
  const newConf = getCurrentConf();
  if (currentConf.path != newConf.path) {
    console.log("loadHomeConf: conf path changed", currentConf.path, newConf.path);
    sessionStorage.setItem("autoReloaded", window.location.pathname);
    window.location.reload();
  } else if (!found || needsReload()) {
    let confPath = window.location.origin + `/${id}/ui/admin/admin.yaml?v=${new Date().getTime()}`;

    if (window.location.origin === "http://localhost:3000") {
      console.log("DEVMODE!!!");
      confPath = `/${id}/ui/admin/admin.yaml`;
    }

    console.log("loadHomeConf, loading", id, confPath);
    await loadYaml(confPath);

  } else {
    console.log("loadHomeConf: conf found", window.location.pathname);
  }
  return newConf;
};

export const loadYaml = async (confPath: string) => {
  const storedConfigs = localStorage.getItem("raconfigs");
  let configs = storedConfigs ? JSON.parse(storedConfigs) : {};

  console.log("SPAloadYaml", confPath);
  await fetch(confPath)
    .then((response) => response.text())
    .then((text) => {
      const c_conf = getCurrentConf(true);
      let conf;
      try {
        conf = yaml.load(text);
        let loadUrl = confPath
        if(document.location.href.includes("spa-dev") && conf?.api_root?.includes('g.apifabric.ai')){
          conf.api_root = conf.api_root.replace('g.apifabric.ai', 'apifabric.ai');
        }

        if(document.location.hash.includes("Configuration")){
          // special case: configuration page contains a load parameter
          const hashParams = new URLSearchParams(document.location.hash.split("?")[1]);
          loadUrl = hashParams.get("load") ?? confPath
        }

        if (!conf.conf_source) {
          const encodedLoadUrl = btoa(loadUrl);
          conf.conf_source = encodedLoadUrl;
        }
      } catch (e) {
        console.warn("Failed to parse yaml", e);
        return;
      }
      if (!setCurrentConf(conf)) {
        return;
      }
      
      if(compareConf(c_conf, conf)){
        return
      }
      console.log("loadYaml Reload...", conf);
      configs[conf.api_root] = conf;
      setConfigs(configs);
      window.location.reload();
    })
    .catch((error) => {
      console.warn(`SPA: Failed to load yaml from ${confPath}`, error);
    });
};

export const compareConf = (conf1: Config, conf2: Config): boolean => {
  // return true if the two configs are the same, else false
  let result
  try{
    result = conf1.api_root === conf2.api_root && Object.keys(conf1).length === Object.keys(conf2).length && JSON.stringify(conf1.authentication) === JSON.stringify(conf2.authentication);
    result = result && JSON.stringify(conf1.about) === JSON.stringify(conf2.about);
    result = JSON.stringify({...(conf1.resources || {}), ...(conf1.authentication || {})}) === JSON.stringify({...(conf2.resources || {}), ...(conf2.authentication || {})});
  }
  catch(e){
    console.warn("compareConf error", e);
    result = false;
  }
  console.debug("compareConf", result);
  return result;
}


/*
Landing Page SPA Conf load
*/
export const loadConf = async (appId = "") => {
  /*
      Load the configuration
  */
  appId = getAppId(appId);
  console.log("LoadConf App ID:", appId);
  let yamlUrl = `${document.location.origin}/${appId}/ui/admin/admin.yaml`
  await loadYaml(yamlUrl);
  const conf = getCurrentConf();
  console.log('Loaded Configuration', conf);
  
  if(conf.api_root){
    return conf.api_root;
  }
  throw new Error("Failed to load configuration");
  
}


export const getAppId = (appId?:string) => {
  // set the app id for the current session

  appId = appId || window.location.pathname.split("/")[1];
  if (!appId || appId === "index.html" || appId === "admin-app" || !appId.startsWith("0")) {
    appId = "";
  }

  appId = appId || sessionStorage.getItem("appId") || localStorage.getItem("appId") || "";
  const hash = window.location.hash;
  
  if (hash.includes('?') && hash.includes('appId')) {
      // get the app id from the URL hash
      const queryString = hash.split('?')[1];
      const params = new URLSearchParams(queryString);
      appId = params.get("appId") || appId;
  }
  else if (document.location.pathname.startsWith("/01")){
      // get the app id from the URL path
      appId = document.location.pathname.split("/")[1];
  }
  if(appId){
    if(appId !== localStorage.getItem("appId")){
      console.log("Changing LS appId", appId);
      localStorage.setItem("appId", appId);
    }
    if(appId !== sessionStorage.getItem("appId")){
      console.log("Changing SS appId", appId);
      sessionStorage.setItem("appId", appId);
    }
  }
  else{
    localStorage.removeItem("appId");
    sessionStorage.removeItem("appId");
  }

  return appId;
}


export const clearSpa = () => {
  localStorage.removeItem("appId");
  sessionStorage.removeItem("appId");
  localStorage.removeItem("raSpa");
  sessionStorage.removeItem("raSpa");
  console.log("SPA Cleared");
}