interface JsonApiItem {
    id: string;
    type: string;
    attributes: { [key: string]: any };
    relationships: { [key: string]: { data: {
        attributes: any; id: string; type: string 
} | { id: string; type: string }[] } };
    [key: string]: any; // Add index signature
}

export interface JsonApiResponse {
    data: JsonApiItem[];
    included?: JsonApiItem[];
}

export function mapIncludedData(jsonApiResponse: JsonApiResponse): JsonApiResponse {
    // Create a map of included data by their IDs
    const includedMap = jsonApiResponse?.included?.reduce((map, item) => {
        map[`${item.type}:${item.id}`] = item;
        return map;
    }, {} as { [key: string]: JsonApiItem }) || {};

    // Iterate over the data array
    jsonApiResponse.data.forEach(item => {
        // Iterate over the relationships
        for (const [_, relationship] of Object.entries(item.relationships)) {
            if (!relationship) continue;
            if (relationship.data) {
                if (Array.isArray(relationship.data)) {
                    // If the relationship data is an array, map each item
                    relationship.data = relationship.data.map(relItem => includedMap[`${relItem.type}:${relItem.id}`]);
                } else {
                    // If the relationship data is a single object, map it directly
                    relationship.data = includedMap[`${relationship.data.type}:${relationship.data.id}`];
                }
            }
        }
    });

    for (const item of jsonApiResponse.data) {
        for (const [key, value] of Object.entries(item.attributes)) {
            item[key] = value;
        }
        for (const [key, value] of Object.entries(item.relationships)) {
            if (Array.isArray(value.data)) {
                item[key] = value.data.map((relItem: any) => {
                    return { ...relItem, ...relItem.attributes };
                });
            } else {
                item[key] = { ...value.data, ...value.data.attributes };
            }
        }
    }

    return jsonApiResponse;
}
