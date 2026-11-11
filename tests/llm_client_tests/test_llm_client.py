"""
Tests for prototypes/base/integration/ai/llm_client.py against a stub OpenAI-compatible endpoint
(no real LLM, no network, no Ollama needed).

Run:  python -m unittest tests/llm_client_tests/test_llm_client.py   (from the ApiLogicServer-src root)
"""
import importlib.util
import json
import os
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "api_logic_server_cli/prototypes/base/integration/ai/llm_client.py"
spec = importlib.util.spec_from_file_location("llm_client", SRC)
llm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(llm)

ENV_NAMES = ["APILOGICSERVER_LLM_BASE_URL", "APILOGICSERVER_LLM_MODEL", "APILOGICSERVER_LLM_API_KEY",
             "APILOGICSERVER_CHATGPT_APIKEY", "APILOGICSERVER_LLM_TIMEOUT"]


class Stub(BaseHTTPRequestHandler):
    reply_text = '{"chosen_supplier_id": 2, "reason": "fast"}'
    status = 200
    reject_response_format = False
    reject_temperature = False
    seen = []

    def log_message(self, *a):  # quiet
        pass

    def do_GET(self):   # /models probe
        self.send_response(200); self.end_headers(); self.wfile.write(b"{}")

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Stub.seen.append({"path": self.path, "auth": self.headers.get("Authorization"), "body": body})
        if Stub.reject_temperature and "temperature" in body:
            self.send_response(400); self.end_headers(); return
        if Stub.reject_response_format and "response_format" in body:
            self.send_response(400); self.end_headers(); return
        if Stub.status != 200:
            self.send_response(Stub.status); self.end_headers(); return
        out = json.dumps({"choices": [{"message": {"content": Stub.reply_text}}]}).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(out)


class TestLLMClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), Stub)
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/v1"
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        for n in ENV_NAMES:
            os.environ.pop(n, None)
        Stub.reply_text = '{"chosen_supplier_id": 2, "reason": "fast"}'
        Stub.status = 200
        Stub.reject_response_format = False
        Stub.reject_temperature = False
        Stub.seen = []
        llm._probe_cache.clear()
        llm._rejected_params.clear()
        llm.OLLAMA_BASE_URL = "http://127.0.0.1:9/v1"   # nothing listens: no accidental real Ollama

    def configure(self, **extra):
        os.environ["APILOGICSERVER_LLM_BASE_URL"] = self.url
        os.environ["APILOGICSERVER_LLM_MODEL"] = "test-model"
        for k, v in extra.items():
            os.environ[k] = v

    def test_not_configured_raises_not_available(self):
        with self.assertRaises(llm.LLMNotAvailable):
            llm.chat_json("s", "u")

    def test_json_reply(self):
        self.configure()
        self.assertEqual(llm.chat_json("s", "u")["chosen_supplier_id"], 2)
        self.assertEqual(Stub.seen[0]["path"], "/v1/chat/completions")
        self.assertEqual(Stub.seen[0]["body"]["model"], "test-model")

    def test_fenced_json_is_tolerated(self):
        self.configure()
        Stub.reply_text = '```json\n{"a": 1}\n```'
        self.assertEqual(llm.chat_json("s", "u"), {"a": 1})

    def test_non_json_raises(self):
        self.configure()
        Stub.reply_text = "I choose supplier 2"
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u")

    def test_json_but_not_object_raises(self):
        self.configure()
        Stub.reply_text = "[1, 2]"
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u")

    def test_retries_without_response_format_on_400(self):
        self.configure()
        Stub.reject_response_format = True
        self.assertEqual(llm.chat_json("s", "u")["reason"], "fast")
        self.assertEqual(len(Stub.seen), 2)
        self.assertNotIn("response_format", Stub.seen[1]["body"])

    def test_temperature_rejected_is_dropped_and_remembered(self):
        self.configure()
        Stub.reject_temperature = True
        self.assertEqual(llm.chat_json("s", "u", temperature=0.7)["reason"], "fast")
        self.assertEqual(len(Stub.seen), 2)                      # first rejected, retry worked
        self.assertNotIn("temperature", Stub.seen[1]["body"])
        Stub.seen.clear()
        llm.chat_json("s", "u", temperature=0.7)
        self.assertEqual(len(Stub.seen), 1)                      # remembered: one request, no temperature
        self.assertNotIn("temperature", Stub.seen[0]["body"])

    def test_failed_retry_is_not_remembered(self):
        self.configure()
        Stub.status = 400                                        # everything is rejected, not just the parameters
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u", temperature=0.7)
        Stub.status = 200
        Stub.seen.clear()
        llm.chat_json("s", "u", temperature=0.7)
        self.assertEqual(Stub.seen[0]["body"]["temperature"], 0.7)   # temperature still sent: nothing was cached

    def test_describe_shows_model_and_host_but_never_the_key(self):
        self.configure(APILOGICSERVER_LLM_API_KEY="sk-secret")
        text = llm.describe()
        self.assertIn("test-model @ 127.0.0.1:", text)
        self.assertNotIn("sk-secret", text)
        self.assertNotIn("/v1", text)

    def test_describe_when_nothing_configured(self):
        self.assertEqual(llm.describe(), "no LLM configured")

    def test_http_error_raises(self):
        self.configure()
        Stub.status = 500
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u")

    def test_unreachable_raises(self):
        os.environ["APILOGICSERVER_LLM_BASE_URL"] = "http://127.0.0.1:9/v1"
        os.environ["APILOGICSERVER_LLM_MODEL"] = "m"
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u")

    def test_api_key_sent_and_old_name_accepted(self):
        self.configure(APILOGICSERVER_CHATGPT_APIKEY="sk-old")
        llm.chat_json("s", "u")
        self.assertEqual(Stub.seen[0]["auth"], "Bearer sk-old")

    def test_new_key_name_wins(self):
        self.configure(APILOGICSERVER_CHATGPT_APIKEY="sk-old", APILOGICSERVER_LLM_API_KEY="sk-new")
        llm.chat_json("s", "u")
        self.assertEqual(Stub.seen[0]["auth"], "Bearer sk-new")

    def test_no_key_no_auth_header(self):
        self.configure()
        llm.chat_json("s", "u")
        self.assertIsNone(Stub.seen[0]["auth"])

    def test_probe_finds_local_ollama_but_needs_model(self):
        llm.OLLAMA_BASE_URL = self.url          # pretend the stub is Ollama
        with self.assertRaises(llm.LLMNotAvailable):
            llm.chat_json("s", "u")             # found, but no model configured
        os.environ["APILOGICSERVER_LLM_MODEL"] = "llama3.1"
        self.assertEqual(llm.chat_json("s", "u")["chosen_supplier_id"], 2)

    def test_key_alone_means_openai_default(self):
        os.environ["APILOGICSERVER_CHATGPT_APIKEY"] = "sk-x"
        base, model, key = llm._resolve()
        self.assertEqual((base, model, key), (llm.OPENAI_BASE_URL, llm.DEFAULT_OPENAI_MODEL, "sk-x"))

    def test_azure_is_a_stub(self):
        os.environ["APILOGICSERVER_LLM_BASE_URL"] = "https://x.openai.azure.com/openai"
        os.environ["APILOGICSERVER_LLM_MODEL"] = "m"
        with self.assertRaises(llm.LLMError):
            llm.chat_json("s", "u")


if __name__ == "__main__":
    unittest.main()
