"""Plug a real model into injection_lab.py  ([RUN] — nothing here runs by default).

The harness calls   model(messages, tools) -> {"answer": str, "tool_calls": [{"name": str, "args": dict}]}
  messages: OpenAI-style list of {"role": "system"|"user"|"assistant"|"tool", "content": str}
  tools:    the tools granted for this case (may be empty under least_privilege)
The harness — not the model — executes tool calls against MOCK tools, applies the
permission list and the confirmation gate, and scores the result.

Option A (stays offline): a local OpenAI-compatible server, e.g. Ollama or llama.cpp
  export HMD007_BASE_URL=http://localhost:11434/v1   HMD007_MODEL=<local model name>
Option B (hosted API): set HMD007_BASE_URL to the provider's OpenAI-compatible endpoint,
  HMD007_MODEL, and HMD007_API_KEY. Data sent = the fictional cases in cases.json only.
Then:
  export HMD007_ENABLE=1
  python3 injection_lab.py --model adapter_template:model --out results-<model>-<date>.md --json results-<model>-<date>.json

Record for the video: provider, exact model id/version, date, temperature, and the
full JSON. Run each condition at least 3 times if the model is not deterministic and
report the spread; 20 cases is a demo, not a security evaluation.
Native tool-calling APIs (e.g. Anthropic, OpenAI "tools") work too: translate `tools`
into the provider's schema and convert its tool calls back into the dict above.
"""
import json
import os
import urllib.request


def model(messages, tools):
    if os.environ.get("HMD007_ENABLE") != "1":
        raise RuntimeError("adapter disabled: set HMD007_ENABLE=1 and HMD007_BASE_URL/HMD007_MODEL (see docstring)")
    base = os.environ["HMD007_BASE_URL"].rstrip("/")
    payload = {"model": os.environ["HMD007_MODEL"], "temperature": float(os.environ.get("HMD007_TEMPERATURE", "0")),
               "messages": [m if m["role"] != "tool" else {"role": "user", "content": f"TOOL RESULT ({m.get('name')}): {m['content']}"}
                            for m in messages]}
    req = urllib.request.Request(base + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + os.environ.get("HMD007_API_KEY", "none")})
    with urllib.request.urlopen(req, timeout=120) as r:
        text = json.load(r)["choices"][0]["message"]["content"] or ""
    start, end = text.find("{"), text.rfind("}")
    try:
        out = json.loads(text[start:end + 1])
    except ValueError:
        return {"answer": text, "tool_calls": []}  # non-JSON reply: treat as plain answer, no tools
    return {"answer": str(out.get("answer", "")), "tool_calls": out.get("tool_calls") or []}
