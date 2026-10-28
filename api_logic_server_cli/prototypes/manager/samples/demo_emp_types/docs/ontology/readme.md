# Ontology for demo_emp_types

This folder describes the `demo_emp_types` system in the standard format that governance, data-catalog and
knowledge-graph tools understand: the business concepts, how they relate, and the rules that govern them.

| File | What it is | Who it is for |
|---|---|---|
| `demo_emp_types.html` | A plain-English page: the things the system knows about, the kinds of employee, and every business rule with the requirement behind it | Business users, reviewers, auditors |
| `demo_emp_types.ttl` | The same content as an OWL ontology (Turtle format) | Governance and catalog tools, ontology editors such as Protégé |
| `render_ontology.py` | Script that turns the `.ttl` into the `.html` page | Whoever maintains this folder |

Start with the `.html` page. Open it in any browser.

---

## What is an ontology?

An ontology is a shared, precise description of a business domain. It names the things the business cares about
(Employee, Department, Order), says how they relate (an Employee works in a Department), and states what kinds of
each thing exist (an Employee is salaried, hourly or commissioned, and may also be military).

Think of a glossary that a computer can read. A glossary says what a word means. An ontology also says how
the words connect, so tools can follow those connections, check them, and reuse them across systems.

**Why organizations use them for governance.** If every system defines "employee" or "controlled good" in its
own way, reports disagree and audits get hard. An ontology gives everyone one vocabulary, and lets a catalog
answer questions such as "which systems use this concept?"

**What an ontology does not do.** It describes meaning. It does not stop a bad transaction. Saying "only hourly
employees may belong to a union" in an ontology documents the policy, but nothing rejects a violating record.

**How this system fills that gap.** In GenAI-Logic, the business rules are enforced by the rule engine on
every change, whether it comes from the API, the Admin app or a message. This ontology links each rule to the
concepts it governs, so the two work together:

- The ontology says what things *mean*.
- The rules make sure the data *stays true* to that meaning.

In the `.html` page, section 3 lists each rule next to the original requirement text. Rules marked
**added by AI** were not in the requirements. They are judgment calls, such as "an order amount must be
greater than zero", which a person should confirm.

---

## How to create the outputs

### 1. View the page (nothing to install)

Open `demo_emp_types.html` in a browser.

### 2. Regenerate the page after the ontology changes

From the Manager root, with the Manager's virtual environment active:

```bash
source venv/bin/activate
pip install rdflib          # once
cd samples/demo_emp_types/docs/ontology
python render_ontology.py demo_emp_types.ttl
```

This rewrites `demo_emp_types.html` next to the `.ttl`. Add a sentence to any concept or rule in the `.ttl`
(an `rdfs:comment`) and it appears on the page.

### 3. Create or update the `.ttl` itself

There is **no export command yet**. `demo_emp_types.ttl` was written with the AI assistant from three sources in the
project, and the same approach works for another project:

- `database/models.py` for the concepts, fields and relationships
- `logic/logic_discovery/*.py` for the rules
- `docs/requirements/` for the requirement text each rule traces to

Ask the AI assistant in the project:

> Create an OWL ontology in Turtle for this project, saved to `docs/ontology/<project>.ttl`, using
> `docs/ontology/demo_emp_types.ttl` in samples/demo_emp_types as the model. Include the type hierarchy,
> and one rule individual for every rule in `logic/logic_discovery/`, linked to what it derives or validates.
> Mark rules the requirements did not ask for as `inferred`. Then run `render_ontology.py` on it.

Review the result before relying on it. The AI writes the ontology by reading the code, and nothing yet
checks that it agrees with the rules the engine actually enforces.

### 4. Check the `.ttl` is well-formed (optional)

```bash
python -c "import rdflib; g=rdflib.Graph(); g.parse('demo_emp_types.ttl'); print(len(g), 'triples')"
```

This confirms the file parses. It does not test the logic. For that, open the `.ttl` in
[Protégé](https://protege.stanford.edu/) and run a reasoner, which flags contradictions in the model.

---

## Status

This is an early example for one sample project, not a shipped feature. The `.ttl` is hand-maintained, so it can
drift from the code. A command that generates it directly from the models and rules is the intended next step.
