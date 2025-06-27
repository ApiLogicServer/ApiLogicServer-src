import { fetchUtils } from 'react-admin';

const apiUrl = 'http://localhost:5656/api';
const httpClient = fetchUtils.fetchJson;

const convertId = (record) => ({
    ...record.attributes,
    id: record.id,
});

export const dataProvider = {
    getList: async (resource, params) => {
        const { page, perPage } = params.pagination;
        const { field, order } = params.sort;
        const query = {
            [`page[number]`]: page,
            [`page[size]`]: perPage,
            [`sort`]: order === 'ASC' ? field : `-${field}`,
        };

        // Filters (e.g. filter[name]=Alice)
        Object.entries(params.filter || {}).forEach(([key, value]) => {
            query[`filter[${key}]`] = value;
        });

        const url = `${apiUrl}/${resource}?${new URLSearchParams(query).toString()}`;
        const { json } = await httpClient(url);
        return {
            data: json.data.map(convertId),
            total: json.meta?.total || json.data.length,
        };
    },

    getOne: async (resource, params) => {
        const url = `${apiUrl}/${resource}/${params.id}`;
        const { json } = await httpClient(url);
        return {
            data: convertId(json.data),
        };
    },

    getMany: async (resource, params) => {
        const promises = params.ids.map((id) =>
            httpClient(`${apiUrl}/${resource}/${id}`).then(({ json }) => convertId(json.data))
        );
        const data = await Promise.all(promises);
        return { data };
    },

    getManyReference: async (resource, params) => {
        const { page, perPage } = params.pagination;
        const { field, order } = params.sort;
        const query = {
            [`page[number]`]: page,
            [`page[size]`]: perPage,
            [`sort`]: order === 'ASC' ? field : `-${field}`,
            [`filter[${params.target}]`]: params.id,
        };

        const url = `${apiUrl}/${resource}?${new URLSearchParams(query).toString()}`;
        const { json } = await httpClient(url);
        return {
            data: json.data.map(convertId),
            total: json.meta?.total || json.data.length,
        };
    },

    create: async (resource, params) => {
        const url = `${apiUrl}/${resource}`;
        const body = {
            data: {
                type: resource,
                attributes: params.data,
            },
        };
        const { json } = await httpClient(url, {
            method: 'POST',
            body: JSON.stringify(body),
        });
        return {
            data: convertId(json.data),
        };
    },

    update: async (resource, params) => {
        const url = `${apiUrl}/${resource}/${params.id}`;
        const body = {
            data: {
                type: resource,
                id: params.id,
                attributes: params.data,
            },
        };
        const { json } = await httpClient(url, {
            method: 'PATCH',
            body: JSON.stringify(body),
        });
        return {
            data: convertId(json.data),
        };
    },

    delete: async (resource, params) => {
        const url = `${apiUrl}/${resource}/${params.id}`;
        await httpClient(url, {
            method: 'DELETE',
        });
        return { data: { id: params.id } };
    },
};