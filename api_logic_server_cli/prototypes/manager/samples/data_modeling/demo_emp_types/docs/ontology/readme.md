# Ontology for demo_emp_types

Generated, not written: `ontology_gv.py` reads `database/models.py`, `ui/admin/admin.yaml` and `logic/logic_discovery/`
and writes everything in this folder. Regenerate it; do not edit it.

| File | What it is | Who it is for |
|---|---|---|
| `demo_emp_types.html` | Plain-English page: kinds of employee, every rule with its requirement and origin, column lineage, validation result | Business users, reviewers, auditors |
| `demo_emp_types.ttl` | OWL ontology: classes, subtypes (defined classes), properties, and every rule as a linked individual | Catalog and ontology tools (for example Protégé) |
| `demo_emp_types.shapes.ttl` | SHACL shapes for the constraints | Any SHACL tool, to check data after the fact |
| `genai-logic.ttl` | The shared rule vocabulary (`gl:`), the same for every project | Tools reading the `.ttl` |
| `lineage.csv`, `lineage.json` | Column-level lineage: which columns feed which | Catalogs, impact analysis |

## What it says

The ontology says what things *mean*; the rules make sure the data *stays true* to that meaning. The ontology does not
stop a bad transaction. The rule engine does, on every change from every path. The shapes let other tools check data.

- **Rules** are `gl:Sum`, `gl:Count`, `gl:Formula`, `gl:Copy` (derivations) and `gl:Constraint`, each linked to what it
  derives or validates (`gl:derives`, `gl:validates`), what it reads (`gl:dependsOn`: the lineage), and the requirement
  behind it (`gl:requirement`).
- **`gl:origin`** is `specified` when the rule matches a line of the requirement, else `inferred`: a judgment call the AI
  made (see `docs/requirements/ad-libs.md`). It is a match on the requirement text, so review it.
- **Constraints** are SHACL shapes. "translated" shapes state the condition in SHACL; "descriptive" shapes carry only the
  message, because the condition is code.

## How to regenerate

From the Manager root:

```bash
python system/ApiLogicServer-Internal-Dev/ontology_gv.py demo_emp_types      # or samples/data_modeling/demo_emp_types
```

No packages are needed to generate. If `rdflib` and `pyshacl` are installed, the files are parsed and the project's own
data (`database/db.sqlite`) is validated against the shapes; otherwise that step is skipped and the generator says so.
In an AI session, say: `create the ontology (validate it if rdflib is available)`.
