import { stringify } from 'query-string';
import { fetchUtils, DataProvider, HttpError } from 'react-admin';
import merge from 'deepmerge';
import { defaultSettings } from './default-settings';
import ResourceLookup from './resourceLookup';
import Keycloak from 'keycloak-js';
import {getConf} from '../Config'
import urlJoin from 'url-join';

const conf : { [ key: string] : any } = getConf();
const duration = 2000;

const prepareAttributes = (attributes : any, resource_en : any) => {
    const resource = decodeURI(resource_en)
    // temp: convert all numbers to string to allow FK lookups (jsonapi ids are strings, while FKs may be numbers :////)
    const resource_attr_rels = conf.resources[resource].attributes?.map( (attr : any) => attr.relationship ? attr.name : null)    
    const m_attrs = Object.assign({}, attributes)
    for(let [k, v] of Object.entries(attributes)){
      m_attrs[k] = v
      if(typeof v === 'number' && resource_attr_rels.find((n: string) => n === k)){
        m_attrs[k] = v.toString();
      }
    }
    return m_attrs
}

const prepareQueryFilter = (query: any, ids : any, fks : any) => {
  if(ids.length === fks.length){
    for(let i = 0; i<fks.length; i++){
      let fk = fks[i]
      let id = ids[i]
      query[`filter[${fk}]`] = id
    }
  }
  else{
    // fk probably contains an underscore
    // todo: how to fix???
    console.warn("Wrong FK length.. ", ids, fks)
    query[`filter[${fks[0]}]`] = ids && ids.length ? ids[0] : ""
  }
}

export const getKeycloakHeaders = (
  keycloak: Keycloak,
  options: fetchUtils.Options | undefined
): Headers => {
  const headers = ((options && options.headers) ||
      new Headers({
          Accept: 'application/json',
      })) as Headers;
  if(keycloak?.isTokenExpired()){
      keycloak.updateToken(30)
  }
  if (keycloak.token) {
      headers.set('Authorization', `Bearer ${keycloak.token}`);
  }
  return headers;
};

export const httpAuthClient = (url: string, options : any) => {
  if (!options.headers) {
      options.headers = new Headers({ Accept: 'application/json' });
  }
  const token : string = localStorage.getItem('auth_token') || "";
  if(token){
    options.headers.set('Authorization', `Bearer ${token}`);
  }
  return fetchUtils.fetchJson(url, options)
  .catch((e:HttpError ) => {
    const msg = e.body?.msg || "Unknown Error."
    console.warn('httpAuthClient httperror', e, e.status, e.body, msg)
    if(e.body?.message?.startsWith('Booting project')){
      // Custom error handling for booting, todo!!
      console.log('WGserver_response: booting', e, e.status, e.body)
      setTimeout(() => document.location.reload(), 3000);
      throw new HttpError(e, e.status, 
        {title: "Booting", 
         detail:"Booting project, please wait", 
         message:"Booting project, please wait",
         code:e.status})
    }
    throw new HttpError(e, e.status, e.body)
  })
}

const createKCHttpAuthClient = (keycloak: Keycloak) => (
  url: any,
  options: fetchUtils.Options | undefined
) => {
  if(!keycloak){
    console.error("No keycloak")
    return
  }
  if(keycloak.token){
    localStorage.setItem('auth_token', keycloak.token)
  }
  const requestHeaders = getKeycloakHeaders(keycloak, options);
  return fetchUtils.fetchJson(url, {
      ...options,
      headers: requestHeaders,
  })
  .catch(e => {
    console.warn('KC httpAuthClient httperror', e, e.body)
    if(e.body?.message?.startsWith('Booting project')){
      // Custom error handling for booting, todo!!
      console.log('WGserver_response: booting', e, e.status, e.body)
      setTimeout(() => document.location.reload(), 3000);
      throw new HttpError(e, e.status, 
        {title: "Booting", 
         detail:"Booting project, please wait", 
         message:"Booting project, please wait",
         code:e.status})
    }
    throw new HttpError(e, e.status, e.statusText)
  })
};

/**
 * Based on
 * 
 * https://github.com/marmelab/react-admin/blob/master/packages/ra-data-simple-rest/src/index.ts
 * @see https://github.com/marmelab/FakeRest
 * 
 */
export const jsonapiClient = (
  apiUrl: string,
  userSettings = {conf : {}},
  keycloak: Keycloak| null = null,
  httpClient = httpAuthClient,//fetchUtils.fetchJson,
  countHeader: string = 'Content-Range',
): DataProvider => {
  
  if(keycloak?.isTokenExpired()){
      keycloak.login();
  }
  if(keycloak){
      httpClient = createKCHttpAuthClient(keycloak)
  }
  const settings = merge(defaultSettings, userSettings);

  return {
    /*******************************************************************************************
     * getList: fetch a collection
     *******************************************************************************************/
    getList: (resource_name_en, params = {}) => {
      const conf = getConf();
      const resource_name = decodeURI(resource_name_en);
      const { page, perPage } = params?.pagination || { page: 1, perPage: 10 };
      if(! conf.resources[resource_name]){
        console.warn(`Invalid resource ${resource_name}`)
        return Promise.reject(new Error(`Invalid resource ${resource_name}`))
      }
      const resource_conf : any = conf.resources[resource_name];
      const sort : string = resource_conf.sort
      // Create query with pagination params.
      const query : {[k: string]: any} = {
        'page[number]': page,
        'page[size]': perPage,
        'page[offset]': (page - 1) * perPage,
        'page[limit]': perPage
      };

      if(sort){
          query.sort = sort
      }
      // Add all filter params to query.
      if(params.filter?.q && "resources" in conf){
          // search is requested by react-admin
          const search_cols = resource_conf.search_cols
          const filter = search_cols?.map((col: any) => {
                              return { 
                                "name":col.name,
                                "op": col.op? col.op : "ilike",
                                "val": col.val ? col.val.format(params.filter.q) : `%${params.filter.q}%`
                              };}) || ""
          if(filter){
            query['filter'] = JSON.stringify(filter)
          }
      }
      else{
        Object.keys(params.filter || {}).forEach((key) => {
          query[`filter[${key}]`] = params.filter[key];
        });
      }

      // Add sort parameter, first check the default configured sorting, then the customized sort
      if (params.sort && params.sort.field) {
          const prefix = params.sort.order?.toLowerCase() === 'desc' ? '-' : ''; // <> ASC
          query.sort = `${prefix}${params.sort.field}`;
      }
      if(!query.sort){
          query.sort = resource_conf.sort || "id"
      }
      const rel_conf = conf.resources[resource_name].relationships || []
      // we only need "toone" rels in getList so we can show the join/user key
      const includes: string[] = rel_conf.filter((rel : any) => rel.direction !== 'tomany').map((rel : any) => rel.name);
      if(params.meta?.include?.length){
        includes.push(...params.meta.include)
      }
      query['include'] = includes.join(',');

      const url = `${apiUrl}/${resource_name_en}?${stringify(query)}`;
      return httpClient(url, {})
        .then(({ json }) => {
          // const lookup = new ResourceLookup(json.data);
          // When meta data and the 'total' setting is provided try
          // to get the total count.
          let total = 0;
          if (json.meta && settings.total) {
            total = json.meta[settings.total];
          }
          // Use the length of the data array as a fallback.
          total = total || json.data.length;
          const lookup = new ResourceLookup(json);
          const jsonData = json.data.map((resource: any) =>{
              return lookup.unwrapData(resource)
            }
          );
          const validUntil = new Date();
          validUntil.setTime(validUntil.getTime() + duration);
          return {
            data: jsonData,
            included: json.included,
            validUntil : validUntil,
            total: total
          };
        })
        .catch((err: HttpError) => {
          console.warn('getList Error', err, err.body, err.status);
          const errorHandler = settings.errorHandler;
          return Promise.reject(errorHandler(err));
        });
    },

    /*******************************************************************************************
      getOne
    ********************************************************************************************/
    getOne: (resource_en: any, params: { id: any }) => {
      const conf = getConf();
      const resource = decodeURI(resource_en)
      if(params.id === null || params.id === undefined){
          return new Promise(()=>{return {data: {}}})
      }
      const resource_conf = conf["resources"][resource];
      if(!resource_conf){
        console.warn(`Invalid resource ${resource}`)
        return new Promise(()=>{});
      }
      const rel_conf = resource_conf?.relationships || [];
      const includes: string[] = rel_conf.map((rel : any) => rel.name).join(",")
      const url = `${apiUrl}/${resource}/${params.id}?include=${includes}&page[limit]=1`; // we only need 1 include at most
      
      return httpClient(url, {}).then(({ json }) => {

        let { id, attributes, relationships, type } = json.data;
        if(id === undefined){
          return {data:{}}
        }
        Object.assign(attributes, relationships, {type: type}, {relationships: relationships}, {attributes: {...attributes} });
        attributes = prepareAttributes(attributes, resource)
        const validUntil = new Date();
        validUntil.setTime(validUntil.getTime() + duration);
        return {
          data: {
            id,
            validUntil : validUntil,
            ...attributes
          }
        };
      });
    },

    /*******************************************************************************************
      getMany
    ********************************************************************************************/
    getMany: (resource_en, params: any) => {
      const conf = getConf();
      if(resource_en === null || resource_en === undefined  || resource_en === "" ||  resource_en === "Location"){
          return new Promise(()=>{return {data: {}}})
      }
      const  resource_de = decodeURI(resource_en)
      const  resource = capitalize(resource_de);
      let query = `filter[id]=${params.ids instanceof Array ? params.ids.join(',') : JSON.stringify(params.ids)}`
      if(params.meta?.include?.length){
        query += `&include=${(params.meta.include).join(',')}`
      }
      
      const url = `${apiUrl}/${resource}?${query}`;
      return httpClient(url, {}).then(({ json }) => {
        
        // When meta data and the 'total' setting is provided try
        // to get the total count.
        let total = 0;
        if (json.meta && settings.total) {
          total = json.meta[settings.total];
        }
        // Use the length of the data array as a fallback.
        total = total || json.data.length; // { id: any; attributes: any; }
        
        const jsonData = json.data.map((value: any) => {
            const result = Object.assign({ id: value.id, type: value.type, relationships: value.relationships }, prepareAttributes(value.attributes, resource))
            //const related = json.included || [];
            // TODO!!: this is not working, we need to find the included resources
            // for(const [k,v] of Object.entries(value.relationships || {})){
            //   console.log('getMany', k, v)
            //   if(v instanceof Array){
            //     v.forEach((inc: any) => {
            //       const type = inc.data?.type
            //       if(!type){
            //         return
            //       }
            //       const related = json.included?.find((rel: any) => rel.type === type && rel.id === inc.id)
            //       Object.assign(result, { [k]: related})
            //     });
            //   }
            // }
            return result;
          }
        );
        const validUntil = new Date();
        validUntil.setTime(validUntil.getTime() + duration);
        return {
          data: jsonData,
          validUntil : validUntil,
          total: total
        };
      });
    },

    /*******************************************************************************************
      getManyReference
    ********************************************************************************************/
    getManyReference: (resource_name_en, params : any) => {
      const conf = getConf();
      const resource_name = decodeURI(resource_name_en)
      const { page, perPage } = params.pagination;
      const { field, order } = params.sort;

      const query: {[k: string]: any} = { };

      if (field) {
        const prefix = order === 'DESC' ? '-' : ''; // <> ASC
        query.sort = `${prefix}${field}`;
      }
      

      let fks = params.target.split('_')
      //const ids = fks.length > 1 ? params.id.split('_') : params.id
      let ids = params.id.split('_')

      if(ids.length !== fks.length){
          console.warn("Wrong FK length ", ids, fks)
          fks = [params.target]
          ids = [params.id]
      }
      
      prepareQueryFilter(query, ids, fks);
      
      query[`page[limit]`] = perPage
      query[`page[offset]`] = (page - 1) * perPage
     
      const options = {};
      const resource_conf = conf["resources"][resource_name];
      const rel_conf = resource_conf?.relationships || [];
      const includes: string[] = rel_conf.map((rel : any) => rel.name).join(",")
      const url = `${apiUrl}/${resource_name}?${stringify(query)}&include=${includes}`
      return httpClient(url, options).then(({ headers, json }) => {
        if (!headers.has(countHeader)) {
          console.debug(
            `The ${countHeader} header is missing in the HTTP Response. The simple REST data provider expects responses for lists of resources to contain this header with the total number of results to build the pagination. If you are using CORS, did you declare ${countHeader} in the Access-Control-Expose-Headers header?`
          );
        }
        let total = json.meta?.total;
        if (json.meta && settings.total) {
          total = json.meta[settings.total];
        }
        // Use the length of the data array as a fallback.
        total = total || json.data.length;
        const lookup = new ResourceLookup(json);
        const jsonData = json.data.map((resource: any) =>{
          return lookup.unwrapData(resource)
          }
        );

        return {
          data: jsonData,
          total: total
        };
      });
    },

    update: async(resource_name_en : string, params: any) => {
      const conf = getConf();
      const resource_name = decodeURI(resource_name_en)
      let type = conf.resources[resource_name].type || resource_name;
      
      const previousDataFiltered = Object.keys(params.previousData)
      .filter(key => !(key in params.data))
      .reduce((obj, key) => {
        obj[key] = params.previousData[key];
        return obj;
      }, {});

        let Sendingdata = { ...previousDataFiltered, ...params.data };
        const data = {
          data: {
            id:  params.id,
            type: type,
            attributes:  Sendingdata
          }
        };

        console.log('Update ', data)
  
        return httpClient(`${apiUrl}/${resource_name}/${params.id}`, {
          method: settings.updateMethod,
          body: JSON.stringify(data)
        })
          .then(({ json }) => {
            const { id, attributes } = json.data;
            return {
              data: {
                id,
                ...attributes
              }
            };
          })
          .catch((err: HttpError) => {
            console.log('catch Error', err.body);
            const errorHandler = settings.errorHandler;
            return Promise.reject(errorHandler(err));
          });
      },
      
    // },

    // simple-rest doesn't handle provide an updateMany route, so we fallback to calling update n times instead
    updateMany: (resource_name, params) => {
      // todo : bulk update
      const conf = getConf();
      return Promise.all(
        params.ids.map((id) => {
          const data = {
            data: {
              attributes: params.data
            }
          };
          return httpClient(`${apiUrl}/${decodeURI(resource_name)}/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(params.data)
          })
        })
      )
      .then((responses) => ({ data: responses.map(({ json }) => json.id) }))
    },

    create: (resource_name_en : string, params: any) => {
      const conf = getConf();
      const resource_name = decodeURI(resource_name_en)
      let type = conf.resources[resource_name].type || resource_name;
      // use both current (in case of a form reference) and data in case of raw dataProvider.create() call
      let item_data = params.data?.current?.data ?? params.data;
      console.log('creating resource with params', params)
      const data = {
        data: {
          type: type,
          attributes: item_data
        }
      };
      return httpClient(`${apiUrl}/${resource_name}`, {
        method: 'POST',
        body: JSON.stringify(data)
      })
        .then(({ json }) => {
          const { id, attributes } = json.data;
          return {
            data: {
              id,
              ...attributes
            }
          };
        })
        .catch((err: HttpError) => {
          console.log('catch Error', err.body);
          const errorHandler = settings.errorHandler;
          return Promise.reject(errorHandler(err));
        })
    },

    delete: (resource, params) => {
      const conf = getConf();
      return httpClient(`${apiUrl}/${decodeURI(resource)}/${params.id}`, {
        method: 'DELETE',
        headers: new Headers({
          'Content-Type': 'text/plain'
        })
      }).then(({ json }) => ({ data: json }))},

    // simple-rest doesn't handle filters on DELETE route, so we fallback to calling DELETE n times instead
    deleteMany: (resource, params) => {
      const conf = getConf();
      return Promise.all(
        params.ids.map((id) =>
          httpClient(`${apiUrl}/${decodeURI(resource)}/${id}`, {
            method: 'DELETE',
            headers: new Headers({
              'Content-Type': 'text/plain'
            })
          })
        )
      ).then((responses) => ({
        data: responses.map(({ json }) => json)
      }))
    },

    getResources: () => {
        const conf = getConf();
        if(conf){
            return Promise.resolve({data: conf});
        };
        return httpClient(`${apiUrl}/schema`, {
            method: 'GET'
        }).then(({json}) => {
            localStorage.setItem('raconf', JSON.stringify(json));
            return { data: json };
        })
        .catch(()=> {return {data : {}} })
      },

    execute: (resource_name_en: string, command: string, data: {  id: string|undefined, data: any, args: any }) => {
        const conf = getConf();
        const resource_name = decodeURI(resource_name_en)
        console.log(`execute rpc on resource ${resource_name} with params`, data)
        const id = data?.id || ""
        if(!command){
          console.warn('No command provided')
          return new Promise(()=>{})
        }
        const endpoint = id ? `${apiUrl}/${resource_name}/${id}/${command}` : `${apiUrl}/${resource_name}/${command}`
        return httpClient(endpoint, {
          method: 'POST',
          body: JSON.stringify(data?.args || {})
        })
      },
  };
};

function capitalize(s: string): string {
  // todo
  return s;
  return s[0].toUpperCase() + s.slice(1);
}
export interface includeRelations {
  resource: string;
  includes: string[];
}

/*
Call safrs jsonapi rpc endpoints
*/
export const jaRpc = async (endpoint: string, data?: any, options?: RequestInit) => {
  const url = urlJoin(conf.api_root, endpoint);
  console.log('jaRpc', url, data, options);
  console.log('jaRpc', conf);
  
  const defaultOptions: RequestInit = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${localStorage.getItem("auth_token")}`,
    },
    body: JSON.stringify(data || {}),
  };
  const requestOptions = { ...defaultOptions, ...options };
  const response = await fetch(url, requestOptions);
  return response.json();
};
