# Getting Started with Genai-Logic react apps

GenAI-Logic (`genai-logic genai-add-app`) [docs here](https://apilogicserver.github.io/Docs/Admin-Vibe/), from `ui/admin/admin.yaml`.

We then *Vibed it* to add dashboards, cards, trees and maps:

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

# To run the app:

```bash
# security for react apps in progress, disable for now...
genai-logic add-auth --provider-type=None
cd ui/react-admin
npm install
npm start
```

Open your browser at [http://localhost:3000](http://localhost:3000).

