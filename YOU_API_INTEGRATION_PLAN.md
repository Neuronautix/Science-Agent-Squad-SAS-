# You.com API Integration Plan

## Executive Assessment

All three You.com endpoints are worth integrating, but they serve different functions
in the swarm and should not be treated as interchangeable. The Research endpoint is
the most transformative addition; the Contents endpoint fixes a real fragility in the
current stack; the Search endpoint needs a correctness fix regardless.

---

## Current State

| Tool | You.com endpoint | Problem |
|---|---|---|
| `search_you_engine` | `https://ydc-index.io/v1/search` (unofficial/legacy URL) | Wrong base URL — will break when deprecated; returns snippets only |
| `scrape_webpage` | None — uses BeautifulSoup on raw HTTP | Fails on JS-rendered pages, fragile HTML parsing, BeautifulSoup dependency |
| *(none)* | Research API | Not used at all |

`scrape_page` is registered in `swarm_config.yml` but is not assigned to any persona's
tool list, so it is effectively dead.

---

## The Three Endpoints — What They Do and Where They Fit

### 1. Search — `GET /v1/search`
Returns real-time web and news snippets (title, URL, snippet text).

**Role in the swarm:** Discovery tool. Used to find recent papers, preprint pages,
news coverage, and Reddit threads that are not in PubMed or Semantic Scholar.

**Current coverage:** Partially — the tool exists but uses the legacy URL and parses
a response structure that may already be outdated.

**Verdict:** Fix the endpoint and response parsing. Keep as `search_web`.
Do not widen the assignment — it is already on all five research agents.

---

### 2. Research — `GET /v1/rag`
Multi-step reasoning: You.com searches the web, reads multiple pages, and returns
a synthesised, well-cited answer in a single API call.

**Role in the swarm:** Deep-synthesis tool for specific domain sub-questions.
When a specialist needs a structured answer on a precise question (e.g., "What does
current evidence say about the CAI scale's test-retest reliability?"), the Research
endpoint produces a citation-backed synthesis rather than a list of snippets to
manually reason over.

**This is not a replacement for agent reasoning.** The Research API produces a
synthesis on a narrow factual question; the specialist still critically evaluates
it, integrates it with KB findings, and applies domain-specific caveats. Think of it
as a "turbo search" that handles retrieval + initial synthesis in one step, saving
2–3 tool-call rounds per specialist.

**Verdict:** High value. Add as `you_research` tool.
Assign to: ClinicalPsych, EpiScope, NeuroCogs, CarePath — not to Dr. Nexus
(would short-circuit specialist consultation) and not to Journalist (who synthesises
from agent findings, not from direct searches).

**When to invoke it (add to persona.md Search Trigger rules):**
- When `search_pubmed` + `search_preprints` return insufficient evidence and the
  sub-question requires a synthesised answer rather than raw papers.
- When the task is to verify a specific claim (e.g., "confirm prevalence of X in
  population Y") rather than to map a broad literature.

---

### 3. Contents — `GET /v1/contents`
Returns clean HTML or Markdown content from any URL.

**Role in the swarm:** Full-text fetcher. Used after `search_web` or
`search_preprints` returns a URL the agent needs to read in full (preprint pages,
paper abstracts, methodology sections, Reddit threads).

**Why it is better than the current `scrape_webpage`:**
- You.com handles JS-rendered pages (the current BeautifulSoup approach cannot).
- Returns clean Markdown — directly usable in agent context without further parsing.
- No BeautifulSoup dependency.
- More reliable on academic publisher pages (Frontiers, MDPI, PubMed full-text).

**Verdict:** Direct replacement for `scrape_webpage`. Same tool name (`fetch_content`
or keep `scrape_page`), same interface, better implementation.
Assign to all four research specialists — `scrape_page` is currently registered but
unassigned; this is the moment to fix that.

---

## Recommended Fallback Chain Per Specialist

```
For a literature sub-question:

  1. search_knowledge_base       ← local KB first (zero API cost)
         ↓ (not found / insufficient)
  2. search_pubmed               ← peer-reviewed, with full abstracts
         ↓ (no results or pre-2023 only)
  3. search_preprints            ← Semantic Scholar (preprints, CHI, arXiv)
         ↓ (found URLs but need full text)
  4. fetch_content               ← You.com Contents: clean Markdown of target page
         ↓ (sub-question needs synthesis, not just raw papers)
  5. you_research                ← You.com Research: synthesised answer with citations
         ↓ (still missing recent news / grey literature)
  6. search_web                  ← You.com Search: snippets from live web
```

This chain is ordered by cost and reliability. KB and PubMed are free and precise;
You.com Research is the most expensive per call and should be a late fallback, not
the default first step.

---

## File-by-File Change Plan

### `automation/tools.py`

#### Change 1 — Fix `search_you_engine` (Search API)
- Update base URL from `https://ydc-index.io/v1/search` to the official
  You.com API endpoint.
- Update response parsing to match the current API response structure.
- Rename internally to `search_you_web` for clarity (keep registered name `search_web`
  in `swarm_config.yml` unchanged — no persona files need updating).

#### Change 2 — Add `you_research` (Research API)
New `@tool` function. Calls the You.com Research (`/v1/rag`) endpoint.

```
you_research(query: str, num_web_results: int = 5) -> str
```

Returns: synthesised answer text + inline citations + list of sources with URLs.
Instructs the agent to treat the output as a starting synthesis to critically
evaluate, not as ground truth.

Fallback: if `YOU_API_KEY` is not set, return a clear error with instructions.

#### Change 3 — Replace `scrape_webpage` (Contents API)
- Replace BeautifulSoup implementation with You.com Contents (`/v1/contents`) call.
- Keep the function name `scrape_webpage` so no config or persona changes are needed
  for existing tool registrations.
- Return format: clean Markdown (preferred) or plain text fallback.
- Keep `max_chars` parameter as a post-processing truncation step on the returned
  Markdown.
- Remove BeautifulSoup import (no longer needed).

---

### `swarm_config.yml`

#### Change 4 — Register `you_research` tool
```yaml
you_research:
  module: "automation.tools"
  function: "you_research"
  description: "You.com Research API: multi-step synthesis with inline citations for a specific sub-question"
```

#### Change 5 — Add `you_research` to specialist tool lists
Add `you_research` to: `ClinicalPsych`, `EpiScope`, `NeuroCogs`, `CarePath`.
Do NOT add to `Dr. Nexus` or `Journalist`.

#### Change 6 — Assign `scrape_page` to all specialists
`scrape_page` is registered but currently unassigned to any persona.
Add it to: `ClinicalPsych`, `EpiScope`, `NeuroCogs`, `CarePath`.
This was a gap before; the Contents API implementation makes it reliable enough
to actually use.

---

### `agents/*/persona.md` (all four research specialists)

#### Change 7 — Add `you_research` to Search Trigger rules
Add to the Behavior section of each specialist:

```
- Research Trigger: If search_pubmed + search_preprints return insufficient evidence
  for a specific claim, call you_research with a precise question to obtain a
  synthesised answer with citations. Treat the output as a starting point for
  critical evaluation, not as a citable source itself.
- Contents Trigger: If a search result URL needs to be read in full (preprint,
  methodology section, supplementary data), call scrape_page before concluding
  the evidence is unavailable.
```

---

### `Future_Improvements_TODO.md`

#### Change 8 — Add tracking items
Add to the Tool Capability section:
```
- [ ] Fix search_you_engine base URL (legacy ydc-index.io endpoint)
- [ ] Add you_research tool (You.com Research / RAG API)
- [ ] Replace scrape_webpage BeautifulSoup impl with You.com Contents API
- [ ] Assign scrape_page to all four research specialists in swarm_config.yml
```

---

## What This Does Not Change

- `search_preprints` (Semantic Scholar) remains — it provides structured metadata
  (DOI, arXiv ID, author list, year) that You.com Research does not return cleanly.
  The two tools are complementary: Semantic Scholar for discovery and metadata;
  You.com Research for synthesis on a known sub-question.
- `search_pubmed` remains — PubMed provides PMID-anchored, peer-reviewed records
  with structured abstract sections that no You.com endpoint replicates.
- The KB-first policy (`search_knowledge_base` before any external call) is unchanged.

---

## Risk Notes

- **You.com Research cost:** The Research API is more expensive per call than Search.
  The `max_tool_rounds_per_agent: 5` limit in `swarm_config.yml` already caps total
  tool calls per specialist; no additional guardrail is needed, but the tool docstring
  should explicitly tell the agent to call it at most once per sub-question.
- **Rate limits:** You.com APIs share the same `YOU_API_KEY`. Heavy parallel fan-out
  (multiple specialists dispatched simultaneously) could hit rate limits. Add a
  `Retry-After` / 429 handler to all three You.com tool functions.
- **Contents API on paywalled pages:** Publisher full-text (Elsevier, Springer) will
  return abstract-only or access-denied. The tool should surface this clearly rather
  than returning an empty string.

---

## Summary Table

| Change | File | Priority |
|---|---|---|
| Fix Search API base URL + response parsing | `tools.py` | High — current URL may already be broken |
| Add `you_research` tool | `tools.py` | High — most impactful new capability |
| Replace `scrape_webpage` with Contents API | `tools.py` | Medium — fixes JS-page gap |
| Register `you_research` in tool registry | `swarm_config.yml` | High (paired with Change 2) |
| Assign `you_research` to four specialists | `swarm_config.yml` | High (paired with Change 2) |
| Assign `scrape_page` to four specialists | `swarm_config.yml` | Medium |
| Add Research + Contents triggers to persona.md | `agents/*/persona.md` | Medium |
| Update TODO tracking file | `Future_Improvements_TODO.md` | Low |
