This example illustrates that it's often a good idea to be more specific in the prompt, 
for example to specify exact table and column names.  Here, we create a time-tracking system, being specific about tables and columns in the [002_create_db_models.prompt](./).

To create this system:
```bash
# create the time_tracking system
als genai --project-name=track --using=system/genai/examples/time_tracking_billing/002_create_db_models.prompt
```