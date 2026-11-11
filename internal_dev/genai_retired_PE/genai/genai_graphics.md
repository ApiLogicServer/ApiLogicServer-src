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
    * Bug: add g-1 must add to docs/response
4. genai/iteration cli does not have access to src app, nor target on original call, so 
    * maybe the 'genai#insert_logic...' which does have access to target project...
        * replace the output docs folder entirely
        * remove graphics from the prompt lines *and* response objects - 
        * Seems unfortunate to create a new project from that...
    * or, a direct call from WebGenai UI (which can pass the project dir)
5. Often failing to create much test data (eg, orders)
