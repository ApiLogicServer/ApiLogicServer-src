# Send Email

Verbatim excerpt from `docs/requirements/project_creation_prompt.md` that drove
`logic/logic_discovery/send_email.py`:

```
Send Email
    Add a SysEmail table (child of customer) with message, subject and CreatedOn.
    When a SysEmail is created, log "email sent", unless the customer has opted out.
```
