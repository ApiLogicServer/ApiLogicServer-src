# Getting Started with GenAI-Logic React Apps

Generated directly by an AI assistant (Claude + Context Engineering) from
`ui/admin/admin.yaml` — see [docs here](https://apilogicserver.github.io/Docs/Admin-Vibe/).

## To run the app

```bash
# security for react apps in progress, disable for now...
genai-logic add-auth --provider-type=None

cd ui/<app-name>   # the name you gave it, e.g. ui/reference_react_app
npm install
npm start
```

Open your browser at [http://localhost:3000](http://localhost:3000).

### If `npm install` fails with `EACCES` on `~/.npm/_cacache`

An earlier `npm install` (usually run once with `sudo` by mistake) left root-owned
files in your global npm cache — a one-time local machine fix, not a project problem:

```bash
sudo chown -R $(id -u):$(id -g) "$HOME/.npm"
```

Then retry `npm install`.
