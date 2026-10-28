These projects were built with native AI, not GenAI-Logic.

- `demo_eai_native`: the EAI demo (see `requirements/demo_eai`) built by AI without GenAI-Logic.
- `demo_eai_legacy`: the same system with its docs removed, as a legacy starting point. `requirements_from_antigravity.md` and `requirements_from_claude.md` are requirements two AIs recovered from its code.
- `demo_eai_modernized`: the legacy system rebuilt as declarative rules with GenAI-Logic, from the requirements recovered from its code (`requirements/demo_eai_modernize`, built by Claude). 35 of 35 scenarios pass, with live Kafka. `transcript.md` is the run; `docs/requirements/demo_eai/ad-libs.md` lists the decisions left for review.
