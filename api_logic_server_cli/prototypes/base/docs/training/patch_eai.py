import re

with open('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/docs/training/eai_subscribe.md', 'r') as f:
    text = f.read()

# Fix 1: Exceptions inside the mapper, not caller. 
text = re.sub(
    r'(?s)XYZ_EXCEPTIONS: dict\[str, str \| None\] = \{.*?\}',
    '# Note: EXCEPTIONS dicts must be defined per-model inside XyzMapper.py, NOT here in the consumer.',
    text
)

text = re.sub(
    r'exceptions=XYZ_EXCEPTIONS',
    '',
    text
)

# Fix 2: Return a named dict `children`, NOT a flat `extras` list
text = re.sub(r'extras', 'children', text)
text = re.sub(r'list\[child_model_instance\]', 'dict[str, list[model_instance]]', text)
text = re.sub(
    r'Child rows with no FK to parent go in `children` list \(returned separately from `parse\(\)`\)',
    'Child rows natively map to a named `children` dictionary (e.g. `{"pieces": [...], "parties": [...]}`) to avoid isinstance dispatch in the caller.',
    text
)

# Fix 3: No session.rollback() inside catch block
text += "\n> **CONSUMER ROLLBACKS:** NEVER call `session.rollback()` in your Kafka consumer's `except` block. The outer framework or test harness relies on explicit rollbacks. Adding it manually masks errors and poisons the session."

# Fix 4: CONSUME_DEBUG guard
text += "\n> **API DEBUG GUARD:** In `api/api_discovery/*_kafka_consume_debug.py`, your endpoint MUST include a guard: `if not os.getenv('CONSUME_DEBUG'): return 'Debug disabled', 403`."

# Fix 5: confluent_kafka vs subprocess
text += "\n> **TEST PUBLISHERS:** Your test script (`test/send_xyz.py`) MUST use `confluent_kafka.Producer` to construct and send messages. Do NOT use `subprocess.run` calling `docker exec`."

# Fix 6: No re-parsing
text += "\n> **NO RE-PARSING:** Do NOT call `ET.fromstring(payload)` inside the consumer listener. The `XyzMapper.parse` method is the only place parsing should occur."

with open('/Users/val/dev/ApiLogicServer/ApiLogicServer-dev/org_git/ApiLogicServer-src/api_logic_server_cli/prototypes/base/docs/training/eai_subscribe.md', 'w') as f:
    f.write(text)

print("eai_subscribe.md patched")
