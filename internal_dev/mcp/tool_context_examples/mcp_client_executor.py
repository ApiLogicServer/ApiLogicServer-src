import requests
from typing import List, Dict, Any, Union
import re
import openai

class MCPClientExecutor:
    def __init__(self, plan: List[Dict[str, Any]], llm=None):
        self.plan = plan
        self.results = []
        self.llm = llm or self.default_llm

    def run(self):
        i = 0
        while i < len(self.plan):
            step = self.plan[i]

            if step.get("llm_call"):
                print(f"Calling LLM after step {i}")
                next_steps = self.llm(step, self.results, self.plan)
                self.plan[i+1:i+1] = next_steps  # insert after current
                i += 1
                continue

            expanded_steps = self.expand_step(step)
            for substep in expanded_steps:
                result = self.execute_step(substep)
                self.results.append(result)

            i += 1

    def expand_step(self, step: Dict[str, Any]) -> List[Dict[str, Any]]:
        # check for $[*] fan-out
        fan_out_keys = self._find_fan_out_keys(step)
        if not fan_out_keys:
            return [self.substitute(step, self.results)]
        
        ref_step_index, attr = fan_out_keys[0]  # only handling 1 fan-out for now
        items = self._extract_list_from_result(self.results[ref_step_index], attr)
        return [self.substitute(step, self.results, row, ref_step_index) for row in items]

    def execute_step(self, step: Dict[str, Any]) -> Any:
        url = step["base_url"].rstrip("/") + "/" + step["path"].lstrip("/")
        method = step["method"].upper()
        params = {p["name"]: p["val"] for p in step.get("query_params", [])}
        body = {p["name"]: p["value"] for p in step.get("body", [])}

        print(f"Executing {method} {url} with body={body} params={params}")
        resp = requests.request(method, url, json=body if method in ['POST', 'PATCH'] else None, params=params)
        resp.raise_for_status()
        return resp.json()

    def substitute(self, step: Dict[str, Any], context: List[Any], row: Dict[str, Any] = None, ref_index: int = None):
        def resolve(val):
            if isinstance(val, str) and val.startswith("$"):
                match = re.match(r"\$(\d+)(\[\*\])?\.(\w+)", val)
                if not match:
                    return val
                step_index, star, key = match.groups()
                step_index = int(step_index)
                if star:
                    return context[step_index]
                if row and int(step_index) == ref_index:
                    return row.get(key)
                return context[step_index].get(key)
            return val

        new_step = {**step}
        new_step["body"] = [{**p, "value": resolve(p["value"])} for p in step.get("body", [])]
        new_step["query_params"] = [{**p, "val": resolve(p["val"])} for p in step.get("query_params", [])]
        return new_step

    def _find_fan_out_keys(self, step):
        fan_outs = []
        for p in step.get("body", []):
            if isinstance(p["value"], str) and "[*]" in p["value"]:
                match = re.match(r"\$(\d+)\[\*\]\.(\w+)", p["value"])
                if match:
                    fan_outs.append((int(match.group(1)), match.group(2)))
        return fan_outs

    def _extract_list_from_result(self, result, key) -> List[Dict[str, Any]]:
        if isinstance(result, dict) and "data" in result:
            result = result["data"]
        return [row for row in result if key in row]

    def default_llm(self, step, results, plan):
        prompt = f"""
        User Goal: {step.get('llm_goal')}
        Step Result: {results[-1]}

        Based on the result, provide next tool_context step(s) as JSON list:
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        return eval(response.choices[0].message.content)  # or json.loads() if response is valid JSON