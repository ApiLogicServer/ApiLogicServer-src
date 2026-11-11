"""
LLM client - one small, vendor-neutral way for rules and events to ask a language model a question.

This runs INSIDE your API Logic Server process.  There is no extra server or sidecar: it makes an
HTTP call to an endpoint you configure.  Whatever runs behind that endpoint (a vendor's cloud, or a
process you run yourself such as Ollama or vLLM) is up to you.  No SDK, no new dependency (urllib only).

It speaks the OpenAI-compatible chat protocol (POST {base_url}/chat/completions), which OpenAI, Ollama,
vLLM, LM Studio and others accept.

Configuration (environment variables)
    APILOGICSERVER_LLM_BASE_URL   e.g. http://localhost:11434/v1 (Ollama) or https://api.openai.com/v1
    APILOGICSERVER_LLM_MODEL      model name, e.g. gpt-4o or llama3.1
    APILOGICSERVER_LLM_API_KEY    optional for local endpoints; also accepted: APILOGICSERVER_CHATGPT_APIKEY
    APILOGICSERVER_LLM_TIMEOUT    seconds, default 30

If BASE_URL is not set:
    - an API key present            -> OpenAI (https://api.openai.com/v1, model default gpt-4o)
    - no key                        -> a quick check for a local Ollama (http://localhost:11434/v1);
                                       needs APILOGICSERVER_LLM_MODEL since Ollama has no default model
    - nothing reachable             -> raises LLMNotAvailable

Callers should catch LLMError and use their deterministic fallback (see the supplier-selection pattern in
docs/training/probabilistic_logic.md).  This client never installs or downloads anything.

Azure OpenAI is NOT supported yet (see _azure_notes below) - untested, so deliberately a stub.

Usage
    from integration.ai.llm_client import chat_json, LLMError
    try:
        result = chat_json(system="You are a supply chain expert.", user=prompt)   # -> dict
    except LLMError as e:
        ...  # fallback, and record why (e.g. in the audit row)
"""

import json
import logging
import os
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

OPENAI_BASE_URL = "https://api.openai.com/v1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_OPENAI_MODEL = "gpt-4o"
DEFAULT_TIMEOUT = 30.0
PROBE_TIMEOUT = 0.5

_probe_cache: dict = {}    # base_url -> bool, one probe per process


class LLMError(Exception):
    """The call failed (network, HTTP error, bad reply).  Caller should use its fallback."""


class LLMNotAvailable(LLMError):
    """No endpoint is configured or reachable.  Not an error condition for callers with a fallback."""


# ---------------------------------------------------------------------------------------------
# Azure OpenAI - stub only (untested).  It is NOT plain OpenAI-compatible:
#   1. URL:     https://<resource>.openai.azure.com/openai/deployments/<deployment>/chat/completions
#               (the deployment name is in the path; "model" in the body is ignored)
#   2. Query:   ?api-version=<version>   (required)
#   3. Header:  "api-key: <key>"         (instead of "Authorization: Bearer <key>")
# To add it: detect "openai.azure.com" in the base url and build the url/headers accordingly.
# ---------------------------------------------------------------------------------------------
_azure_notes = "Azure OpenAI is not supported by llm_client yet - see comment above"


def _env(*names: str, default: str = "") -> str:
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


def _is_reachable(base_url: str) -> bool:
    """Quick check that something answers at base_url (used only to find a local Ollama)."""
    if base_url in _probe_cache:
        return _probe_cache[base_url]
    ok = False
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/models", timeout=PROBE_TIMEOUT):
            ok = True
    except Exception:
        ok = False
    _probe_cache[base_url] = ok
    return ok


def _resolve() -> tuple:
    """Returns (base_url, model, api_key) or raises LLMNotAvailable."""
    base_url = _env("APILOGICSERVER_LLM_BASE_URL")
    model = _env("APILOGICSERVER_LLM_MODEL")
    api_key = _env("APILOGICSERVER_LLM_API_KEY", "APILOGICSERVER_CHATGPT_APIKEY")

    if base_url and "openai.azure.com" in base_url:
        raise LLMError(_azure_notes)

    if not base_url:
        if api_key:
            base_url = OPENAI_BASE_URL
            model = model or DEFAULT_OPENAI_MODEL
        elif _is_reachable(OLLAMA_BASE_URL):
            base_url = OLLAMA_BASE_URL
            if not model:
                raise LLMNotAvailable("Local Ollama found, but APILOGICSERVER_LLM_MODEL is not set")
        else:
            raise LLMNotAvailable("No LLM configured (set APILOGICSERVER_LLM_BASE_URL / _MODEL / _API_KEY)")
    if not model:
        raise LLMNotAvailable("APILOGICSERVER_LLM_MODEL is not set")
    return base_url.rstrip("/"), model, api_key


def _post(url: str, body: dict, api_key: str, timeout: float) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def chat_text(system: str, user: str, temperature: float = 0.0, json_mode: bool = False) -> str:
    """Ask the model; returns the reply text.  Raises LLMError (or LLMNotAvailable)."""
    base_url, model, api_key = _resolve()
    timeout = float(_env("APILOGICSERVER_LLM_TIMEOUT", default=str(DEFAULT_TIMEOUT)))
    body = {"model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    url = base_url + "/chat/completions"
    try:
        try:
            reply = _post(url, body, api_key, timeout)
        except urllib.error.HTTPError as e:
            if json_mode and e.code == 400:      # endpoint may not support response_format: retry without
                body.pop("response_format")
                reply = _post(url, body, api_key, timeout)
            else:
                raise
        return (reply["choices"][0]["message"]["content"] or "").strip()
    except urllib.error.HTTPError as e:
        raise LLMError(f"LLM HTTP {e.code} from {url}") from e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise LLMError(f"LLM endpoint unreachable ({url}): {e}") from e
    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise LLMError(f"Unexpected LLM reply from {url}: {e}") from e


def chat_json(system: str, user: str, temperature: float = 0.0) -> dict:
    """Ask the model for a JSON object; returns it as a dict.  Raises LLMError if the reply is not JSON.

    Tolerates markdown code fences around the JSON, which some models add despite being asked not to.
    The caller must still validate the content (e.g. that a chosen id is one of the candidates).
    """
    text = chat_text(system, user, temperature=temperature, json_mode=True)
    if text.startswith("```"):
        text = "\n".join(text.split("\n")[1:-1]).strip()
    try:
        result = json.loads(text)
    except ValueError as e:
        raise LLMError(f"LLM reply was not valid JSON: {text[:200]!r}") from e
    if not isinstance(result, dict):
        raise LLMError(f"LLM reply was JSON but not an object: {text[:200]!r}")
    return result
