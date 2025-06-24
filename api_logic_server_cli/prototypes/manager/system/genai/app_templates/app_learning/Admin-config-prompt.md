Backend JSONAPI endpoint metadata is described in the following <resources> section , each key is a resource collection endpoint name.
The tab_groups attribute describes the resource relationships, with fks being the foreign keys of the related resource.
user_key tells which attribute should be shown when referencing the resource. for example, if the user_key is "name", the resource should be be shown by its "name" in the UI, while its reference should be by its "id".

<resources></resources> 

Most of the time, the resource name key will be the same as the type, 
so you can use an instance type to get the resource configuration.

ignore SPAPage and SPASection resources.

This resource configuration can be used when importing the Config getConf() function in the react code, for example:

<javascriptCode>
import { getConf } from '../../Config';
const conf = getConf();
const resources = conf.resources;
</javascriptCode>
