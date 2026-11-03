# A/B tests: GenAI-Logic vs native AI

The same requirement, built two ways: with GenAI-Logic, and by native AI without it.

| A (GenAI-Logic) | B (native AI) | What it shows |
|---|---|---|
| `basic_demo_genai_logic` | `bd_claude_native_ai` | The same procedural prompt. GenAI-Logic produced 5 declarative rules; native AI produced insert-only code with 4 confirmed silent-stale bugs |

The EAI pair, `demo_eai_modernized` and `demo_eai_native`, is in `samples/modernization`: it is an A/B test inside the modernization story.

The comparison document `logic/procedural/declarative-vs-procedural-comparison.md` is also copied into several other samples.
