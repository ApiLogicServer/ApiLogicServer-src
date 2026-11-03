# Modernization samples

Projects built by recovering business requirements from existing code with AI, then rebuilding them as declarative GenAI-Logic rules.

| Project | Source | Script and requirements |
|---|---|---|
| `erpnext_credit_modernized` | Credit control from ERPNext, an open-source business application | `samples/requirements/erpnext_modernize` |
| `demo_eai_legacy` | The EAI demo with its docs removed, as a legacy starting point. `requirements_from_antigravity.md` and `requirements_from_claude.md` are the requirements two AIs recovered from its code | - |
| `demo_eai_modernized` | The legacy system rebuilt as declarative rules with GenAI-Logic, from the recovered requirements. 35 of 35 scenarios pass, with live Kafka. `transcript.md` is the run; `docs/requirements/demo_eai/ad-libs.md` lists the decisions left for review | `samples/requirements/demo_eai_modernize` |
| `demo_eai_native` | The same EAI demo (see `samples/requirements/demo_eai`) built by AI without GenAI-Logic: the comparison for `demo_eai_modernized` | `samples/requirements/demo_eai` |

`demo_eai_native` and `demo_eai_modernized` are an A/B pair on the same system: native AI against GenAI-Logic.

For the idea, the steps and what these experiments do and do not show, see the [Modernization Overview](https://apilogicserver.github.io/Docs/Modernization-Overview/).
