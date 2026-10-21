# system/config - your Manager settings

Files you add here are yours. A Manager refresh (`genai-logic start --clean`) re-writes this readme
(and anything else we ship) but leaves any other file in this folder alone. Don't reuse the name of
a file we ship.

## default_from_git.txt - your organization's project template

`genai-logic create` overlays a template on top of the standard project when you pass
`--from_git=<git-url-or-directory>`. Put that value in `default_from_git.txt` and every project
you create gets it, with nothing to remember:

```
# first non-comment line wins: a git URL, or a directory (relative paths are relative to the Manager)
https://github.com/your-org/genai-logic-template
```

To try it, rename `default_from_git__example.txt` (it points at a sample template) to
`default_from_git.txt`, then edit the URL or directory to your own.

- Files in the template overwrite the standard ones, so a template can carry your own
  `test/api_logic_server_behave/reports/Behave Logic Report Intro.md` (the text shown above every
  Behave Logic Report), security roles, context files, and so on.
- `--from_git=<other>` on a create overrides the default for that project; `--from_git=none` creates
  that project without any template.
- If the default can't be used (bad path, no network, private repo), `create` stops with a message
  naming this file. It never silently creates a project without your template.
- Each project's `docs/requirements/project_creation_report.md` records which template was used.
- The template is copied when the project is created. Changing it later does not change existing
  projects.
