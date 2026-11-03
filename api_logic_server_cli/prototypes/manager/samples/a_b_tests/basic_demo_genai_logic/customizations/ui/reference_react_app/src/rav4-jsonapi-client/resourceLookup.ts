interface Relationship {
    data: null | { id: string; type: string } | Array<{ id: string; type: string }>;
    relationships?: { [key: string]: Relationship };
}

/**
 * A map-like class that maps resource linkage objects {id: 1, type: "user"} to concrete resources with attributes and
 * relationships
 */
export default class ResourceLookup {
    lookup: Map<any, any>;
    includes: string[];

    /**
     * Constructs a new lookup map
     * @param {Object} response A JSON API response, in JSON format
     */
    constructor(response: any) {
        this.lookup = new Map();
        this.includes = [];

        // If the response wasn't a JSON dictionary, we can't and don't need to build a lookup
        if (typeof response !== 'object') return;

        let resources;
        // if (response.hasOwnProperty('included')) {
        if (Object.prototype.hasOwnProperty.call(response, 'included')) {
            resources = [...response.data, ...response.included];
        } else {
            resources = response.data;
        }

        // Iterate over each resource returned and put each in the lookup
        for (const entry of resources) {
            const key = this.getKey(entry);
            this.lookup.set(key, entry);
        }
    }

    /**
     * Calculates a hashable key for JSON API resources
     * @param resource A resource linkage object
     * @returns {string}
     */
    getKey(resource: any) {
        return `${resource.type}:${resource.id}`;
    }

    /**
     * Looks up a resource
     * @param resource A resource linkage object
     * @returns {Object}
     */
    get(resource: any) {
        // If we don't have included data for this resource, just return the Resource Linkage object, since that's still
        // useful
        if (this.has(resource)) {
            return this.lookup.get(this.getKey(resource));
        } else {
            return structuredClone(resource);
        }
    }

    /**
     * Returns true if the resource is in the lookup
     * @param resource
     * @returns {boolean}
     */
    has(resource: any) {
        return this.lookup.has(this.getKey(resource));
    }

    /**
     * Converts a JSON API data object (with id, type, and attributes fields) into a flattened object
     * @param {Object} response A JSON API data object
     */
    unwrapData(response: any) {
        // The base resource object, merge the attributes and the id/type fields
        const result = Object.assign(
            {
                id: response?.id,
                ja_type: response?.type,
                type: response?.Type || response?.type,
                attributes: response.attributes || {},
            },
            response.attributes
        );

        // Deal with relationships
        if (Object.prototype.hasOwnProperty.call(response, 'relationships')) {
            result.relationships = response.relationships;
            for (const [relationshipName, relationship] of Object.entries(response.relationships)) {
                if ((relationship as Relationship).data === null) {
                    result[relationshipName] = null;
                }

                if (!(relationship as Relationship).data) {
                    continue;
                } else if (Array.isArray((relationship as Relationship).data && (relationship as Relationship).data)) {
                    result[relationshipName] = (relationship as Relationship).data?.map((linkage: any) => {
                        const resource = this.get(linkage);
                        const lresult = structuredClone(this.unwrapData(resource));
                        Object.entries(lresult.attributes || {}).map(([key, value]) => {
                            lresult[key] = value;
                        });
                        result.relationships[relationshipName].data = result[relationshipName];
                        return lresult;
                    });
                } else if ((relationship as Relationship).data?.id) {
                    const resource = this.get((relationship as Relationship).data);
                    result[relationshipName] = this.unwrapData(resource);
                    result.relationships[relationshipName].data = result[relationshipName];
                }
            }
        }

        try {
            JSON.stringify(structuredClone(result));
        } catch (e) {
            return null;
        }
        return structuredClone(result);
    }
}