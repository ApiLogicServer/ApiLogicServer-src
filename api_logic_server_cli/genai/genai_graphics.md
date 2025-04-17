### Tests

| Case           | From Demo      | Normal | Notes |
| :------------- | :------------- | :----- | :----- |
| Change Model   | Worked 1 of 2
| Rules          | wg failed spa page after upd model (class no Base)<br>Dup Rules (so fail-safe ignored logic)<br>* rules not in docs response, dup'd in active_rules.json
| Both
| + Graphics
| New Graphics   | n/a            | Worked


### Notes:

1. fixed: demo prompt was wrong, so its graphics lost
2. Many graphics failures (Sales vs Sale, sql 'extract', ...) ==> badly need a delete/repair
3. Iterations definitely driven by docs/response, but
    * Bad-g-1 then add g-2, lost g-1
    * Bug: add g must add to docs/response
4. genai/iteration does not have access to src app, nor target, so 
    * how could a 'delete_graphics` work?  Seems unfortunate to create a new project from that...
    * maybe the 'genai#insert_logic...' -- remove the prompt lines *and* reponse objects
5. Often failing to create much test data (eg, orders)