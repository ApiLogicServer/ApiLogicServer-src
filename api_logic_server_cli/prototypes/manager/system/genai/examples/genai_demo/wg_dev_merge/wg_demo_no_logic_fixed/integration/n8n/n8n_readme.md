# Workflow Integration using n8n.io
The n8n.io has over 400 integrations predefined. There are over 1,000 prebuilt templates including AI chatbot creation that can be used to integrate with ApiLogicServer. In the integration/n8n folder, the N8N_WebHook_from_ApiLogicServer,json which can be imported into your n8n.io running project and use the Northwind sample to test. [Note - the SendGrid APIKey is not provided] 

## Download and install n8n.io locally
The cloud version is available - but for development we will use the local install
```
https://docs.n8n.io/hosting/installation/npm/
```

## Create a new workflow and create webhook instance
Use the POST method and add basic authentication (user: admin, password: p) 

## Populate config.py values
Copy the path UUID (wh_path)
```
    # N8N Webhook Args (for testing)
	# see https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/?utm_source=n8n_app&utm_medium=node_settings_modal-credential_link&utm_campaign=n8n-nodes-base.webhook#path

    wh_scheme = "http"
    wh_server = "localhost" # or cloud.n8n.io...
    wh_port = 5678
    wh_endpoint = "webhook-test"
    wh_path = "002fa0e8-f7aa-4e04-b4e3-e81aa29c6e69"
    token = "...."
    # Basic Auth is (user: admin, password: p) base64 encoded

    N8N_PRODUCER = {"authorization": "Basic {token}}", "n8n_url": f'"{wh_scheme}://{wh_server}:{wh_port}/{wh_endpoint}/{wh_path}"'} 
    # OR enter the full URL
    N8N_PRODUCER = {"authorization": "Basic {token}","n8n_url":"http://localhost:5678/webhook-test/002fa0e8-f7aa-4e04-b4e3-e81aa29c6e69"}  
  	N8N_PRODUCER = None # comment out to enable N8N producer
```

## Start the n8n.io workflow webhook to listen
In the logic/logic_discovery - see workflow_integration.py
After Flush (all rules have fired and database has been updated)
call the webhook interface - once you have the body - you can extract values and pass to other nodes
in the workflow (e.g. SendGrid email)
```
    def call_n8n_workflow(row: models.Customer, old_row: models.Customer, logic_row: LogicRow):
        """
        Webhook Workflow:  When Customer is inserted/updated = post to external system
        """
        if logic_row.is_inserted():
            status = send_n8n_message(logic_row=logic_row)
            logic_row.debug(status)

    Rule.after_flush_row_event(on_class=models.Customer, calling=call_n8n_workflow)
```