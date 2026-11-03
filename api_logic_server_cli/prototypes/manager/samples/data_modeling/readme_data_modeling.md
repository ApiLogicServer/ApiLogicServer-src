# Data modeling samples

How to shape the data so that rules can govern it.

| Project | Pattern |
|---|---|
| `demo_emp_types` | Entity subtypes: single-table inheritance with a type column, and two independent classifications (employment type and military status) on one entity |
| `basic_demo_sales_by_month` | `insert_parent`: rollup (bucket) rows keyed by a composite natural key, created automatically on first use |
