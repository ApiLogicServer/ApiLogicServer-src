Provide an option to see departments either as a list (as now), or as a tree.  The tree expands to show related sub departments, as links.  If I click on the dept name link, then open the department "show" to the right.

TECHNICAL CONSTRAINTS:

- Avoid recursion stack overflow: include proper termination conditions
- Handle mixed data types: use parseInt() for ID comparisons  
- Prevent import conflicts: use aliases for Material-UI components
- Verify data relationships: check actual field names in backend
- Use incremental development: start simple, add complexity gradually
- Test each layer: tree logic → expansion → detail panel → tabs
