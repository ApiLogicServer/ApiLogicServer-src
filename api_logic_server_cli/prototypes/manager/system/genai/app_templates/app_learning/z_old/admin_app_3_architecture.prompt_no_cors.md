
## Architecture

- **Framework**: React 18 + react-admin 4.x
- **Data Provider**: Custom `dataProvider.js` using `fetchUtils` (no external `ra-jsonapi-client`)
  - Must support: `getList`, `getOne`, `getMany`, `getManyReference`, `create`, `update`, `delete`
  - Must support: filters, joins, sorting, pagination
- **Backend**: JSON:API per `mcp_discovery.json`
- **CORS**: Ensure API allows `http://localhost:3000`
- **Project Setup**:
  - Use `create-react-app`
  - Include: `react-admin`, `@mui/material`, `@emotion/react`, `@emotion/styled`, `react-router-dom`
  - Do not use any deprecated or unmaintained libraries
  - Include complete and correct `App.js`, `index.js`, `dataProvider.js`, and `index.html`

---

## Response Format

Format the response as a JSResponseFormat:

class JSResponseFormat(BaseModel):  # must match system/genai/prompt_inserts/response_format.prompt
    code : str # generated javascript code (only)

---

## Run Instructions

```bash
npm install
npm start
```

Then open in browser: `http://localhost:3000`
