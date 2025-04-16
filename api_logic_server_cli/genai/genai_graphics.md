### Tests

| Case           | From Demo      | Normal | Notes |
| :------------- | :------------- | :----- | :----- |
| Change Model   | Worked 1 of 2
| Rules          | wg failed spa page after upd model (class no Base)<br>Dup Rules (so fail-safe ignored logic)<br>* rules not in docs response, dup'd in active_rules.json
| Both
| + Graphics


### Notes:

1. fixed: demo prompt was wrong, so its graphics lost
2. Many graphics failures (Sales vs Sale, sql 'extract', ...) ==> badly need a delete/repair
3. Iterations definitely driven by docs/response, but
    * Bad-g-1 then add g-2, lost g-1
    * Bug: add g must add to docs/response