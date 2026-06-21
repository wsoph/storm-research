#!/usr/bin/env python3
"""Self-contained anysearch client for the storm-research skill.

Stdlib only (no `requests`, no pip installs). Talks to anysearch's anonymous
HTTP API directly via JSON-RPC 2.0. UTF-8-safe stdout so Chinese survives a
Windows cp1252 console.

Subcommands
-----------
  search "<query>" [--max N] [--json]
      Single query -> numbered source list  [S#] title -- url / snippet
  multi "<q1>" "<q2>" ... [--max N] [--json]
      Up to 5 queries in ONE batch_search HTTP call. Sources numbered globally.
  extract <url> [--json]
      Full-page fetch. Anti-bot sites (Zhihu/Xiaohongshu/WeChat) often fail;
      on failure prints  EXTRACT_FAILED: <reason>  and exits 0 so the caller
      falls back to the snippet instead of crashing.

Exit codes: 0 on success (and on graceful extract failure); 1 on network/RPC error.
"""
import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.request

ENDPOINT = "https://api.anysearch.com/mcp"
TIMEOUT = 40

# UTF-8-safe stdout/stderr (Windows consoles default to cp1252).
out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
err = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Markdown item shape returned by the API:
#   ### 1. Title
#   - **URL**: https://...
#   - snippet text (one line)
ITEM_RE = re.compile(
    r"###\s+\d+\.\s+(?P<title>.+?)\n\s*-\s*\*\*URL\*\*:\s*(?P<url>\S+)\s*\n"
    r"\s*-\s*(?P<snippet>.*?)(?=\n###|\n---|\Z)",
    re.S,
)
# batch_search prefixes each group with "## Query N: <text>"
QUERY_SPLIT_RE = re.compile(r"^##\s+Query\s+\d+:\s*(.+?)\s*$", re.M)
# extract failure signatures (graceful fallback, not a crash)
FAIL_SIGNS = ("proxies exhausted", "extract_fetch_failed", "extract proxies",
              "all proxies failed", "fetch failed")


def call(tool, args):
    """POST a tools/call and return the text payload. Raises RuntimeError on RPC/HTTP error."""
    payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": tool, "arguments": args},
    }).encode("utf-8")
    req = urllib.request.Request(
        ENDPOINT, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        raise RuntimeError("network error: %s" % (getattr(e, "reason", e),))
    except Exception as e:  # noqa: BLE001 - surface anything else cleanly
        raise RuntimeError("request failed: %s" % (e,))
    if isinstance(data, dict) and data.get("error"):
        raise RuntimeError("rpc error: %s" % json.dumps(data["error"], ensure_ascii=False))
    text = ""
    for part in data.get("result", {}).get("content", []):
        if part.get("type") == "text":
            text = part.get("text", "")
    return text


def parse_items(text):
    """Extract [{title,url,snippet}] from a search/batch markdown block."""
    items = []
    for m in ITEM_RE.finditer(text or ""):
        items.append({
            "title": m.group("title").strip(),
            "url": m.group("url").strip(),
            "snippet": " ".join(m.group("snippet").split()),
        })
    return items


def render(items, start=1):
    """Numbered, human/agent-readable source list starting at [S{start}]."""
    lines = []
    for i, it in enumerate(items, start):
        lines.append("[S%d] %s -- %s" % (i, it["title"], it["url"]))
        if it["snippet"]:
            lines.append("     %s" % it["snippet"])
    return "\n".join(lines)


def cmd_search(a):
    text = call("search", {"query": a.query, "max_results": a.max})
    items = parse_items(text)
    if a.json:
        out.write(json.dumps(items, ensure_ascii=False, indent=2) + "\n")
    elif items:
        out.write(render(items) + "\n")
    else:
        out.write("(no results)\n")
    out.flush()
    return 0


def cmd_multi(a):
    queries = a.queries[:5]  # API caps batch at 5
    text = call("batch_search",
                {"queries": [{"query": q, "max_results": a.max} for q in queries]})
    # Split the combined output into per-query groups, keeping global S# numbering.
    groups, parts = [], QUERY_SPLIT_RE.split(text or "")
    if len(parts) >= 3:
        # parts = [preamble, qtext1, body1, qtext2, body2, ...]
        for i in range(1, len(parts) - 1, 2):
            groups.append((parts[i].strip(), parts[i + 1]))
    else:
        groups.append(("", text or ""))

    all_items, counter = [], 1
    if a.json:
        payload = []
        for qtext, body in groups:
            its = parse_items(body)
            payload.append({"query": qtext, "results": its})
            all_items.extend(its)
        out.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    else:
        for qtext, body in groups:
            its = parse_items(body)
            header = "== %s ==" % qtext if qtext else "== results =="
            out.write(header + "\n")
            out.write((render(its, counter) if its else "(no results)") + "\n\n")
            counter += len(its)
            all_items.extend(its)
    out.flush()
    return 0


def cmd_extract(a):
    text = call("extract", {"url": a.url})
    low = (text or "").lower()
    if not text or any(s in low for s in FAIL_SIGNS):
        reason = (text or "empty response").strip().splitlines()[0][:200] if text else "empty response"
        if a.json:
            out.write(json.dumps({"ok": False, "reason": reason, "url": a.url},
                                 ensure_ascii=False) + "\n")
        else:
            out.write("EXTRACT_FAILED: %s\n" % reason)
        out.flush()
        return 0  # graceful: caller falls back to snippet
    if a.json:
        out.write(json.dumps({"ok": True, "url": a.url, "content": text},
                             ensure_ascii=False) + "\n")
    else:
        out.write(text + "\n")
    out.flush()
    return 0


def main():
    p = argparse.ArgumentParser(prog="search.py", description="anysearch client (stdlib-only)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="single query")
    s.add_argument("query")
    s.add_argument("--max", type=int, default=5)
    s.add_argument("--json", action="store_true")
    s.set_defaults(fn=cmd_search)

    m = sub.add_parser("multi", help="up to 5 queries in one batch call")
    m.add_argument("queries", nargs="+")
    m.add_argument("--max", type=int, default=5)
    m.add_argument("--json", action="store_true")
    m.set_defaults(fn=cmd_multi)

    e = sub.add_parser("extract", help="full-page fetch (graceful on anti-bot failure)")
    e.add_argument("url")
    e.add_argument("--json", action="store_true")
    e.set_defaults(fn=cmd_extract)

    a = p.parse_args()
    try:
        sys.exit(a.fn(a))
    except RuntimeError as ex:
        err.write("SEARCH_ERROR: %s\n" % ex)
        err.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
