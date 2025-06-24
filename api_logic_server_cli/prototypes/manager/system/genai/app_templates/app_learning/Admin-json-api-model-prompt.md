This JSONAPI is fetched using the react-admin dataProvider (useDataprovider hook).
All resources have a "type" and "id" attributes (according to the JSONAPI specification).

Besides the regular parameters, the dataProvider is extended to interpret the "include" meta parameter to retrieve included relationships.

<javascriptCode>
dataProvider.getList(resourceName, {
            pagination: { page: 1, perPage: 10 },
            meta: { include: ["relationship_name"]}
})
</javascriptCode>

attributes are inlined in the instance: 
for example, if the resource is "some_resource" and the attribute is "name", then 'some_resource.name' will be the attribute value.

included relationships are inlined in the instance:
for example, if the resource is "some_resource" and the relationship is "relationship_name", the included data will be in the instance "relationship_name" key (some_resource.relationship_name).
So:
some_resource.relationship_name.id will be the id of the included (toone) relationship.
some_resource.relationship_name will be an array of included (tomany) relationships.

instances have a "relationships" key, which contains a dictionary of the relationships, for example, 
following is the response for a resource with a tomany relationship named "tomany_relationships_name"
<json>
{
    "tomany_relationships_name": {
        "data": [
            {
                "id": "1",
                "type": "Transaction"
            }
        ],
        "meta": {
            "count": 1,
            "limit": 5,
            "total": 1
        }
    },
    "toone_relationsip_name": {
        "data": {
            "id": "1",
            "type": "Customer"
        }
    }
}
</json>

The actual relationship data is in the "data" key of the relationship.
for example, the 'instance.tomany_relationships_name' will be an array of the instances data of the related resource:
<json>
[
    {
        "id": "1",
        "ja_type": "Transaction",
        "attributes": {
            "Type": "withdrawal",
            "account_id": 1,
            "amount": 500,
            "description": "Grocery Shopping",
            "transaction_date": "2022-03-01"
        },
        "Type": "withdrawal",
        "account_id": 1,
        "amount": 500,
        "description": "Grocery Shopping",
        "transaction_date": "2022-03-01",
        "relationships": {
            "account": {
                "data": null
            }
        },
        "account": null
    }
]
</json>

similarly, the 'instance.toone_relationship_name' will be the instance data of the related resource:
<json>
{
    "id": "1",
    "credit_limit": 10000,
    "first_name": "Alice",
    "last_name": "Brown",
}
</json>
if a toone relationship is empty, it's value will be null.

if you want to fetch all related resources, you can use the 'meta: { include: ["+all"]}' parameter in the dataProvider.getList call.

