Courtesy Ray Myers


1. Column (as a table name) is a reserved word [issue 85]
2. Missing attributes:
3. Rule xlate: 
    * Tasks cannot move to 'In Progress' if dependencies are incomplete
    * `Rule.constraint(validate=Task, as_condition=lambda row: not row.dependencies or row.dependencies_completed, error_msg="Task dependencies are not completed")`

Here is the prompt

```
A board has a WIP limit that restricts the number of tasks in a specific board_column (e.g., "In Progress").
A task belongs to a board_column on a board (e.g., "To Do," "In Progress," "Done").
A task's status moves from "To Do" → "In Progress" → "Done" in sequence.
A task cannot move to "In Progress" if it exceeds the board's WIP limit.
A board's total WIP limit is the sum of all board_column WIP limits.
A task's priority is automatically set based on predefined criteria (e.g., deadline, dependencies).
A task can have dependencies that prevent it from being moved to "In Progress" until prerequisite tasks are completed.
```

And here is our first cut of logic

```
# Automatically derive task priority based on predefined criteria.
Rule.formula(derive=Task.priority, as_expression=lambda row: 'High' if row.deadline and row.deadline < datetime.now() + timedelta(days=1) else 'Normal')

# A task cannot move to 'In Progress' if it exceeds the board's WIP limit.
Rule.constraint(validate=Task, as_condition=lambda row: row.status != 'In Progress' or Task.query.join(BoardColumn).filter(BoardColumn.id==row.board_column_id).filter(BoardColumn.name=='In Progress').count() < BoardColumn.wip_limit, error_msg='exceeds the board column WIP limit')

# A board's total WIP limit is the sum of all board column WIP limits.
Rule.sum(derive=Board.total_wip_limit, as_sum_of=BoardColumn.wip_limit)

# A task with dependencies cannot move to 'In Progress' unless all prerequisite tasks are completed.
Rule.constraint(validate=Task, as_condition=lambda row: row.status != 'In Progress' or all(depends_on.status == 'Done' for depends_on in row.dependencies), error_msg='Task has incomplete dependencies')
```