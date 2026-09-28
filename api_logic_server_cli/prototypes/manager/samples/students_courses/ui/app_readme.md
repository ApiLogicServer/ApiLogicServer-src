# Vibe-Coding a Custom React Admin App

Full docs: [apilogicserver.github.io/Docs/Admin-Vibe](https://apilogicserver.github.io/Docs/Admin-Vibe/)

## The Idea: Get the Data Model Right Fast, *Then* Build the UI

Don't start React generation from a blank prompt — start from the Admin App you
already have running. It's the fast iteration loop for getting the data-model
surface correct before any UI code exists:

1. **Iterate on `ui/admin/admin.yaml`** — columns, types, ordering, labels,
   relationships, `show_when` visibility. Refresh the Admin App, check it, adjust,
   repeat. This loop is seconds per cycle, no build step, no React involved.
2. **Once `admin.yaml` is right**, generate the React Admin app from it. The
   generator isn't guessing table structure — it's translating a schema you've
   already verified. That's why this step is reliable: the hard part (getting
   columns/types/relationships correct) happened first, in the cheap loop.
3. **Only then layer on presentation** the Admin App's generic grid/form UI
   doesn't do — card layouts, maps, custom dashboards, branded styling. This is
   where a custom React app earns its keep over the built-in Admin App.

Skipping straight to React generation means debugging schema mistakes (wrong
column, wrong type, missing relationship) inside generated JSX — slower and
harder to isolate than catching them in `admin.yaml` first.

## Command — ask your AI assistant directly

**Default method.** No OpenAI key, no separate API call — your AI assistant
(Copilot/Claude, already in this session) generates the app directly, using
`docs/training/admin_app_2_functionality.prompt.md` for the per-resource
pattern and reporting requirements:

```text
Create a new react app named my-app-name from ui/admin/admin.yaml.
```

Copy the skeleton from `<manager-root>/venv/lib/python<ver>/site-packages/
api_logic_server_cli/prototypes/manager/system/genai/app_templates/react-admin-template/`
into `ui/my-app-name/` (a sibling of `ui/admin/`, not inside it — `ui/admin/`
is reserved for the built-in Admin App's own `admin.yaml`/config). This path is
**Manager-level, not project-level** — it lives in the shared venv one or more
directories above this project (e.g. `../venv/...` if the project is a direct
child of the Manager), not under this project's own `system/` folder. If unsure
of the depth, locate it dynamically:
```bash
python3 -c "import api_logic_server_cli, os; print(os.path.join(os.path.dirname(api_logic_server_cli.__file__), 'prototypes/manager/system/genai/app_templates/react-admin-template'))"
```
Then generate one resource file per table in `admin.yaml`, then wire `App.js`.
See `docs/training/admin_app_2_functionality.prompt.md` for the full pattern
— this is not free-form: it documents the required structure per resource
file (List/Show/Create/Edit) and the reporting format (per-file progress and
timing, then a total summary).

The generated app is pre-wired to this project's JSON:API (data provider,
auth, record context) and shaped by the current `ui/admin/admin.yaml`.

<details markdown>
<summary>Fallback: CLI generator (requires an OpenAI key)</summary>

Only use this if no AI assistant is available in your environment. It calls
OpenAI's API directly (one call per resource file, to avoid token overflow)
instead of using your assistant's own session:

```bash
source ../venv/bin/activate
genai-logic genai-add-app --app-name=my-app-name --vibe
```

Requires an OpenAI key set in `.env`. Produces the same output shape as the
default method above.

</details>

## Requirements

- Node/npm installed
- Security must be disabled for now (temporary restriction)

## After generation

```bash
cd ui/my-app-name
npm install
npm start
```

If `npm install` fails with `EACCES` on `~/.npm/_cacache`, an earlier `npm install`
(usually run once with `sudo` by mistake) left root-owned files in your global npm
cache — a one-time local machine fix, not a project problem: `sudo chown -R
$(id -u):$(id -g) "$HOME/.npm"`, then retry.

## Customizing — Cards, Maps, and Beyond

This is step 3 above: presentation the Admin App can't do. Customize using AI
chat (Copilot/Claude). **Read `docs/training/` first** — it documents the
data-access provider configuration built at generation time, governing how the
app talks to JSON:API and maintains record context. Skipping this is the most
common cause of custom React work going wrong.
