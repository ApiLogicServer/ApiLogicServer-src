# Important Pre-created Sample Apps

The `samples` folder has pre-created important projects you will want to review at some point:

* [nw_sample_nocust](https://apilogicserver.github.io/Docs/Tutorial/) - northwind (customers, orders...) database

* [nw_sample](https://apilogicserver.github.io/Docs/Sample-Database/) - same database, but with logic/Python ***customizations added***.  It's a great resource for exploring:

    * Hint: use your IDE to search for `#als`

    * The sample is also created without customization (`sample_nocust`).

* [tutorial](https://apilogicserver.github.io/Docs/Tutorial/) - short (~30 min) walk-through of using API Logic Server using the northwind (customers, orders...) database

<details markdown>

<summary>You can always re-create the samples</summary>

<br>Re-create them as follows:

1. Open a terminal window (**Terminal > New Terminal**), and paste the following CLI command:

```bash
ApiLogicServer create --project-name=samples/tutorial --db-url=
ApiLogicServer create --project-name=samples/nw_sample --db-url=nw+
ApiLogicServer create --project-name=samples/nw_sample_nocust --db-url=nw
```
</details>
</details>

&nbsp;

<details markdown>

<summary>How to Run Projects from the Manager </summary>

<br>There are 2 ways of running projects from the Manager:

1. Use ***another instance of VSCode.***  You can *examine* them in this current instance, but *run* them in their own instance.

    * To do so, you probably want to acquire this extension: `Open Folder Context Menus for VS Code`. It will enable you to open the sample, tutorial or your own projects in another instance of VSCode.

    * This option provides more Run/Debug options (e.g., run without security, etc),

2. Or, use the Run/Debug Entry: `API Logic Server Run (run project from manager)`

</details>

