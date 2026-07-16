# Reference React App

GenAI-Logic React Admin app, generated directly by an AI assistant (Claude + Context
Engineering) from `ui/admin/admin.yaml` — see [docs here](https://apilogicserver.github.io/Docs/Admin-Vibe/).
No OpenAI key, no separate CLI generation step; this replaces the older ChatGPT/prompt-engineering
`genai-add-app --vibe` pipeline as the default path.

We then *vibed it* further to add dashboards, cards, trees, and maps:

```text
Please customize the react-app as follows:

create a landing page that summarizes the architecture, and iFrame to "http://localhost:5656/dashboard"

Add an option on the Employee List page to show results as cards, and
show the employee image in the card.

Create a Department tree view component for the existing Department list page.
Make it collapsible/expandable and integrate it into the existing Department.js file.
The tree should show just the Department Name as a link;
clicking the link opens an Information panel to the right.
The panel is equivalent to Department Show: all the fields, plus tab sheets for related data.
The tab sheets should provide transitions to the related data show pages (eg, the Employee page).

Enhance supplier list page to include a toggle for a professional, interactive world map view.
The map should display supplier icons on a real map with proper geography.
Click a supplier icon should open the Supplier show page.
```

<br>

## Directory name vs. `package.json`

This app lives in `ui/reference_react_app/` — that's the name to `cd` into and the name
you'll see in file paths. `package.json`'s `"name": "react-admin-template"` is just the
generator skeleton's name (copied from `system/genai/app_templates/react-admin-template/`
as the starting point — see `ui/app_readme.md`) and was never renamed after generation.
It has no effect on how you run the app — cosmetic only, safe to ignore or rename later.

<br>

## To run the app

```bash
# security for react apps in progress, disable for now...
genai-logic add-auth --provider-type=None

cd ui/reference_react_app
npm install
npm start
```

Open your browser at [http://localhost:3000](http://localhost:3000).

### If `npm install` fails with `EACCES` on `~/.npm/_cacache`

```text
npm error code EACCES
npm error Your cache folder contains root-owned files, due to a bug in
npm error previous versions of npm which has since been addressed.
```

This means an earlier `npm install` (usually run once with `sudo` by mistake) left
root-owned files in your global npm cache — it's a one-time local machine fix, not a
problem with this project. Fix it once, permanently, for your whole machine:

```bash
sudo chown -R $(id -u):$(id -g) "$HOME/.npm"
```

Then retry `npm install`. You only need to do this once per machine, not per project.

<br>

## Packaging for users / distribution

If you're handing this project to someone else (a teammate, a customer, a fresh machine):

- **Don't commit `node_modules/`** — it's large and platform-specific; `.gitignore` already
  excludes it. The recipient runs `npm install` themselves.
- **Do commit** `package.json`, `package-lock.json`, and all of `src/`, `public/` — that's
  everything `npm install && npm start` needs to reproduce the app.
- Tell recipients about the `EACCES` cache issue above **before** they hit it — it's the
  most common first-run failure and has nothing to do with this project's code.
- `npm run build` produces a static `build/` folder for production hosting (see
  [Create React App deployment docs](https://facebook.github.io/create-react-app/docs/deployment))
  if you need to deploy rather than run `npm start` in dev mode.
