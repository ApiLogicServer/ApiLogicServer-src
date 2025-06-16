You are a professional JavaScript developer building a complete React 18 admin app using React-Admin 4.x.

Your task:
Create a complete admin app based on a **JSON:API** schema. Do **not** use `ra-jsonapi-client`; instead, implement a **custom `dataProvider.js`** using `fetchUtils`.

### 📦 Tech Stack
- React 18
- React-Admin 4.x
- @mui/material
- @emotion/react
- @emotion/styled
- create-react-app

### ✅ Requirements

#### 📁 Project Structure
- Use `create-react-app` to scaffold the app.
- Place each resource (e.g., Customer, Order) in its own file under `src/`.
- Use a shared layout/settings component.

#### 🔌 dataProvider.js
- Implement full CRUD support:
  - `getList` (supporting pagination, sorting, and filtering)
  - `getOne`, `getMany`, `getManyReference`
  - `create`, `update`, `delete`
- Translate React-Admin queries into valid JSON:API requests.
- Support inclusion of related resources via joins and relationships.

#### 🔄 API Integration
- Use base URL: `http://localhost:5656/api`
- Derive resources and fields directly from the JSON:API schema.
- Render foreign keys using reference fields (e.g., `Order.customer_id` uses `ReferenceField` to display Customer name).

#### 🎯 Output
- Output the **entire working project**:
  - All component files
  - `dataProvider.js`
  - `App.js`, `index.js`
  - Any theme or layout code
  - `package.json`

Avoid mockups or placeholders — output real, compilable code.