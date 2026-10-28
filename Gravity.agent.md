<!-- gravity-cli 0.10.0 · sha256:27cc36705fa40bb71fcf05d2da63a8d8b69cc3f2ffe0a9e908b44ab79faff4f6 · kept up to date by the Gravity CLI; edit a copy, or delete this line to keep your edits -->
# Gravity.agent.md

You are a coding agent working in a folder where a person is building an **agent for Gravity**: a Python
program that Gravity runs for other people, with only the tools and models the agent declared. Read this file
completely before you write code. Then read `problem-to-agent.md` in this folder: it is the method for turning a
problem statement into an agent that holds up, with five worked examples. This file is the reference for the
platform it is built on. `Gravity.getting-started.md` is the plain-language overview to share with the person you
are working with.

You build with what the Gravity CLI gives you and nothing else. You cannot change Gravity itself, and nothing in
this file needs access to its servers or code. "Gravity" below means the hosted platform your agent is pushed to.

Gravity CLI 0.10.0 wrote this file and rewrites it on every update. Do not edit it: an edited copy is left
alone and stops getting updates (`gravity docs --force` replaces it). Put project notes in your own `AGENTS.md`,
`CLAUDE.md` or `agent.md`, which Gravity never touches. When this file and the platform disagree, the platform
wins: `gravity validate` and the hosted build are the judges. Facts here were checked against the live dev
deployment on 2026-10-25 and the platform changes merged to its dev branch that this release goes out with (slot
`ask_in`, the X developer-app tools, the approval-order rule, paged result lists); a claim marked "not verified" was
read from code or docs and never observed live.

## 0. The rules, in one screen

1. An agent is a folder: `manifest.yaml`, `requirements.txt`, `src/` (with `src/agent.py`), optional `tests/`.
   Nothing else ships.
2. `manifest.yaml` declares everything the agent may touch: inputs, tools, approvals, triggers, memory, outputs.
   Gravity enforces it on every call. An undeclared tool is refused whatever the code says.
3. `src/agent.py` defines `async def graph()` returning a **compiled** LangGraph graph. Read the three
   environment variables **inside** it, never at import. Imports are absolute from `src/`.
4. The agent never holds an API key. Tools come over MCP from `GRAVITY_GATEWAY_URL`, models from
   `GRAVITY_LLM_URL`, both with `GRAVITY_RUN_TOKEN`. There is no `OPENAI_API_KEY`.
5. On the platform, load tools with `await gravity.tools()` (section 5 has the loader): a call that needs the
   person's approval is held through it, and the same call made through a plain MCP client fails there with
   `APPROVAL_REQUIRED`. Gravity decides which calls need approval from the tool and the person's own setting, not
   only from your `required_for` list (section 10). To ask the person something mid-run, use `gravity.ask()`, never
   your own `interrupt()`.
6. The final state sets `result` **every run**. The screen is drawn from the shape of `result` (section 9), so name
   it for a reader. A report also sets `corpus`, which Gravity renders as Markdown, Word, PowerPoint or CSV. The
   agent writes no renderer and no UI code.
7. Code owns every fact (counts, money, dates, ranking, dedupe). The model reads text into structured fields and
   writes sentences around numbers code computed. Never let the model invent a number, name, link or quote.
8. Anything irreversible is a draft, or sits behind `approvals.required_for` with a fallback for when the person
   says no.
9. Every tool result goes through a check that turns a gateway refusal (plain text, not an exception) into an
   error. A failed source is named in the result, never silently empty.
10. Test the logic with fake tools and a fake model, then `gravity validate`, `gravity run`, `gravity build`,
    `gravity push`. A pushed version is frozen: fix by raising `version` and pushing again.
11. Never put keys, tokens or passwords in any file, fixtures included. The hosted build runs a secret scanner
    and refuses the upload on any hit. Secrets a person must supply are `type: secret` inputs.
12. Ask only what applies: a question that depends on another answer gets `show_if`, "upload or paste" is a
    `choose_one` group, never label prose such as "only when delivering to Gmail". The platform hides, drops and
    checks them on every run (section 8).
13. Remember through the platform: the notebook (`state["memory"]`) or `gravity.memory` collections, never a file
    or a module variable. An agent that does several things declares `actions` and branches on
    `state["actions"]` (section 10).

## The bar: an agent is software, not a prompt

Gravity does not list an agent that a person could have got from a chat assistant in one to three prompts. Check
the idea against this list before you build; `problem-to-agent.md` (sections 1 to 7 and 17) says how.

- **A product, not an answer.** The agent behaves like an app: it asks for the few facts the request left out,
  covers every side of the problem the person would otherwise check by hand, and shows a result they can act on.
  Several steps, several sources, one outcome.
- **Real data only.** Every name, number, date, price, link and quote comes from something the agent read in this
  run, and the source is shown. If it could not be found, the result says so. Nothing fills a gap.
- **Fact-checked in code.** What the model extracts is checked against the source text before it is shown. What
  fails the check is dropped and counted (rule 7 and section 11).
- **Personal to the request.** Country, budget, role, market, tone, and the person's own data (their site, their
  sent mail, their profile) change what comes back. A generic result is a failure.
- **Honest about its limits.** What it could not read, what is an estimate (with its basis and a date), what is
  unverified.
- **Acts only with consent.** Anything that reaches other people or cannot be undone is a draft first or waits for
  the person's approval, and has a fallback.
- **Safe to leave running.** It remembers whom it already contacted, never repeats an effect, stops when someone
  says no, and respects caps and working hours.

Gravity has two kinds of agent. *Research* agents (job-scout, pain-point-discovery, study-abroad-advisor) read many
sources and report. *Acting* agents (lead-gen, hiring) also do the work: they write and send messages with approval,
read replies, follow up, book interviews, keep a tracker and remember every person they dealt with. Build toward
the second kind wherever the problem calls for action.

## 1. How Gravity runs an agent

```
you (gravity CLI)                          Gravity
-----------------                          -------
gravity init, edit files
gravity validate                           the same checks the hosted build runs
gravity run  /  gravity dev        --->    the real gateway and models, on accounts you connected
gravity build, gravity push        --->    re-validate, scan, build an ARM64 image, start a runtime
                                           review by the Gravity team, then listed for users
a user runs it from /app, chat,
a schedule or a webhook            --->    the control plane starts a run; the gateway serves its tools and models
```

| Part | What it does |
|---|---|
| Control plane | Accounts, agents and versions, threads and runs, approvals, schedules, webhooks, review. `gravity login/push/agents/runs/logs` talk to it. Default address `https://agents.dev.gravity.fast`. |
| Gateway | The only way out. Serves tools over MCP (streamable HTTP) and models over an OpenAI-compatible API. Checks every call against the run's declared tools, holds calls that need approval, meters model and tool spend against the run's budget, and keeps memory. A tool runs on **Gravity's own account** where Gravity covers it (section 6), else on the **caller's own connected account**. |
| Runtime | Your image, one session per conversation thread, ARM64 Linux, Python 3.12. It loads your entrypoint, runs the graph, streams step events, and returns `result`. |
| Run token | `GRAVITY_RUN_TOKEN`: scoped to the tools this run may call (plus an approval list and a budget). The agent only ever sees this token. |
| `gravity` package | Preinstalled in the hosted image: `gravity.tools()` (approval-aware tools), `gravity.memory` (collections, notebook, previous run), `gravity.ask()` (pause for an answer), `gravity.MemoryQuotaError`, `gravity.Corpus` and its parts, `gravity.REJECTED`. It is **not on PyPI and cannot be installed outside Gravity**; PyPI packages named `gravity` and `gravity-sdk` are unrelated, so never `pip install` them. Import it behind a guard (section 5): locally those features are off, so only a hosted run exercises them. |

### A hosted run, step by step

1. A person starts it from `/app`, the dashboard chat, a button under a result (one of your `actions`), a
   schedule (India time, at most every 5 minutes; for the whole flow or one action), a `github.push` webhook, or a
   chat follow-up. Gravity applies the caps (20 manual or chat runs in any rolling 24 hours; a small free allowance,
   then credits), merges defaults and slot picks into `inputs`, applies the input rules (a hidden question's value
   is dropped, a visible required one must be there, for every kind of run), picks the run's actions, seals
   `secret` inputs, and queues the run. One live run per thread.
2. The run is prepared and handed to your runtime (it waits for the runtime to be ready, up to `timeout_seconds` plus
   two minutes), then the outputs the person asked for are delivered, then it finishes. If the agent needs an
   approval the run is **parked** for up to 7 days.
3. Dispatch mints a run token (tools, approvals, budget, the person's connected accounts), opens sealed secrets,
   loads the notebook if the manifest declares one (`memory.notebook_kb`, or the older `state`), and invokes the
   runtime session for that thread.
4. The runtime sets the environment, imports your entrypoint **fresh for this run**, and runs
   `graph.astream({"inputs": {...}, "memory": {...}, "actions": [...], "action": ..., "action_inputs": {...}},
   stream_mode="updates")` (`memory` only with a notebook, the action keys only with `actions`) with a remote
   checkpointer and store injected, `recursion_limit` 100, and the checkpoint saved after every step. Step events
   stream to the timeline; a heartbeat every 30 s keeps it alive.
5. Tool calls go to the gateway (`tools/list` returns exactly the run's declared tools; names use `_` for `.`).
   Model calls go to `GRAVITY_LLM_URL` and are costed per call. At the per-run budget (default **$1.00**) the
   gateway answers `402 BUDGET_EXCEEDED`.
6. When the graph ends, `result`, `corpus`, `source` and `memory` are stored (the notebook only if the run
   **completed** and fits its cap), the outputs are rendered and delivered, and the run finishes. If an action it
   ran has `then`, the next action starts as its own run on the thread. A scheduled run whose result differs from
   the last one emails the person a one-line summary (counts, never content).
7. A run that outlives its timeout, or whose runtime stops signalling for two minutes, is started again, up to 3
   more times (4 starts in all), resuming from its last checkpoint, before it fails. Design nodes to be safe to run
   twice.

The same pipeline serves every surface, so a result must read well in the run card, chat and history without
agent-specific code.

### What a local run does and does not do

`gravity run` runs your graph in your own virtualenv (`.venv` in the folder if present) against the real gateway.
`gravity login` stores a gateway token for your account; each run trades it for a run token scoped to the
manifest's tools, so an undeclared tool is refused locally exactly as hosted, and tools act on the accounts **you**
connected with `gravity connect`. `gravity dev` serves a local dashboard over the same runs (form from the
manifest, live timeline, approvals, result, history), and runs from `gravity run` in the same folder appear in it.

`gravity run` applies the show/hide and required rules (`--input platforms=x,linkedin` for a multi-select), but not
the hosted type checks, so `--input n=5` arrives as the string `"5"` locally and the number `5` hosted. It runs the
default actions or `--action name --action-input k=v` and answers `gravity.ask()` with `--answer "question=answer"`
(else its default). `gravity memory ls | show | clear` reads `.gravity/memory/`, which only fills when the `gravity`
SDK is importable (see section 10).

Locally you do **not** get: the checkpointer and durable pauses (a call that needs approval holds for 240 s, then
`APPROVAL_TIMEOUT`; with no terminal, or `GRAVITY_UNATTENDED=1`, it is rejected; `gravity.ask()` never pauses),
`recursion_limit`, the model budget (local run tokens are not metered), the `gravity` package (it cannot be installed
outside Gravity, so `gravity.memory`, `gravity.ask`, `gravity.tools` and `gravity.Corpus` are unavailable: guard the
import and test those paths on a hosted run), `browser.read` and `browser.act`, outputs and renderers, the result
screen and its action buttons, or schedule chains. Tools that run on Gravity's own accounts (section 6) use an
account you connected with `gravity connect` instead, or answer `NEEDS_RECONNECT`; `web.fetch_proxied` works.

### Limits to design for

| Item | Value |
|---|---|
| Run time | `runtime.timeout_seconds`: schema 10 to 28800, default 300. Reference agents use 300 to 900. |
| Run budget | $1.00 per hosted run. It covers model calls **and** paid tools (tools on Gravity's account, `web.fetch_proxied`, browser time). A model call past the budget answers `402 BUDGET_EXCEEDED`; a tool answers a `BUDGET_EXCEEDED:` text. The check runs before a call, so the last call can overshoot. Set `max_tokens` on every call and keep at most two model calls in flight. |
| Graph steps | `recursion_limit` 100 super-steps |
| Dependencies | Locked for `aarch64-manylinux2014`, CPython 3.12, **wheels only**. A package with no ARM64 wheel fails at `gravity validate` or the image build. No compilers, no browser, no TeX (a wheel such as Typst typesets PDFs). |
| Disk | No persistent disk. Memory (section 10) and the store are the only things that survive. |
| Network | Outbound is open today (no filter in the code), but the address is an AWS datacenter: Reddit archives, Capterra, Product Hunt, Glassdoor and Indeed refuse it whatever the client. A source that works from your laptop is not verified until a hosted run reads it. Design for HTTPS. |
| Files in | Upload at most 25 MB; the agent receives a signed https link valid 12 hours. |
| Secrets in | At most 4096 bytes; replaced by placeholders in stored checkpoints. Never copy one into `result` or `corpus`. |
| Email out | An output `destination: gmail.send` (Gravity delivers the result to one address, no attachment) is limited to 200 per thread per rolling day. Your own `gmail.send` tool calls are not counted there: they accept `cc`, `bcc` and attachments (`{"name", "data": "data:<type>;base64,..."}`; PNG, JPEG, GIF, WEBP or PDF, at most 10 MB each) and need approval as section 10 describes. |
| Environment | `GRAVITY_GATEWAY_URL`, `GRAVITY_LLM_URL`, `GRAVITY_RUN_TOKEN`, and `GRAVITY_UNATTENDED` (`1` when nobody is watching: a schedule, a chain, a webhook). `gravity run` sets the same. The SDK reads the other variables; your code should not. No vendor keys exist. |
| Memory | An item up to 64 KB, 10,000 items per collection, 25 MB per person per agent, 5,000 writes per run, items kept 1 to 730 days, the notebook up to 256 KB (section 10). |

## 2. The build loop

From a problem statement to a published agent. `problem-to-agent.md` explains each step; this is the order.

1. **Read the statement into a contract**: outcomes, rules and edge cases as testable lines. Name what you will
   refuse or reinterpret, and why. (problem-to-agent section 1)
2. **Research what exists**, then decide build or wrap. (section 2)
3. **Probe every tool and data source** from where the agent will run. Save dated real answers as test fixtures.
   (section 3)
4. **Decompose into modules**, each with a source of truth; decide what code computes and what the model may
   decide. (sections 4 and 5)
5. **Write the spec** with numbered acceptance criteria that name their check. (section 6)
6. **Scaffold**: `gravity init my-agent --template minimal|structured|deepagent|chat`, or `gravity init --here`
   in an existing project. Write `manifest.yaml` first, then `requirements.txt`, then the modules.
7. **Build in order**: pure logic with tests, parsers over fixtures, the graph against a fake world, the report
   through the renderers, prompts last. (section 8)
8. `gravity validate`, then `pytest` as its own step, then `gravity run --input name=value`, then `gravity build`
   and `gravity push`.
9. **Test as the user would**, from the real page, on every surface; turn each complaint into a general rule, a
   test and a version bump. (sections 9 and 10)
10. Shape the result so the platform can draw it; ship; record what you learned. (sections 12 and 13)

| Command | What it does |
|---|---|
| `gravity init <name> [--template T] [--here]` | Scaffold a working agent, or only a `manifest.yaml` into this folder |
| `gravity validate [path]` | The build's checks, locally; compiles `requirements.lock` for the platform |
| `gravity run [path] --input k=v` | Run locally. `--input k=@file` reads a value from a file; `--reply "text"` continues a chat; `--action a --action-input k=v` runs one action; `--answer "question=answer"` answers `gravity.ask()` |
| `gravity dev [path]` | Local dashboard: form, live timeline, approvals, result, history |
| `gravity schedule [path]` | Fire `triggers.schedule` locally (`--now`, `--cron`); approvals are answered "no" |
| `gravity memory [ls\|show\|clear] [collection]` | What a local run kept in `.gravity/memory/` and the notebook |
| `gravity build [path]` | Package `build/agent.zip` (validates first) |
| `gravity push [path]` | Upload and build the hosted version; waits until `ready` or `failed` |
| `gravity agents` | Your agents: version, status, review, Gravity's notes, why one is off |
| `gravity runs <agent>`, `gravity logs <run id>` | Hosted runs and their timeline (mechanics only for other people's runs) |
| `gravity tools [text]` | The gateway's live tool list, grouped by app; needs no sign-in |
| `gravity connect [app]` | List or connect your own accounts (Gmail, Slack, Firecrawl...) for local runs |
| `gravity login`, `gravity logout`, `gravity whoami` | Sign in with your Google account; the session lives in the OS keychain |
| `gravity adapt <slot> <name> --tools a,b` | A model writes a slot adapter; kept only if its tests pass |
| `gravity guide [--save]` | The longer builder guide shipped with the CLI |
| `gravity help`, or `-h` on any command | The command list, or one command's options |
| `gravity docs`, `gravity update`, `gravity changelog` | Refresh these files; update the CLI; what changed |

Project-side files: `.gravity/` holds `payload.json` (deleted after a run), `thread.json`, `memory.json` (the
notebook), `memory/` (collections, `previous.json`, a saved notebook), `store.json`, `runs/<id>/` (the last 50)
and `run.lock` (one live run per folder). `build/` holds the zip and
`build.json`. Neither is shipped.

## 3. The folder

```
my-agent/
  manifest.yaml        required  what the agent is and may do (section 4)
  requirements.txt     required  direct dependencies with version ranges; may be empty, must exist
  requirements.lock    generated by gravity validate / build, for the platform; never edit it
  src/                 required  all code; the entrypoint lives here
    agent.py                     defines graph (section 5)
    ...                          your modules, one file per concern
  tests/               optional  shipped if present
  tools_needed.yaml    optional  describes a tool that is not in the catalog yet (section 6)
```

`gravity build` packs exactly `manifest.yaml`, `requirements.txt`, `requirements.lock`, `tools_needed.yaml`,
`src/` and `tests/`, minus dotfiles, dot-directories, `__pycache__` and `.pyc`. Data files, notebooks, `.venv/`,
`.gravity/`, `samples/`, `README.md` and `build/` are **not** shipped; code that reads them fails when Gravity
runs it. Put data an agent needs under `src/`, and fixtures under `tests/`.

| Template | Shape | Pick it for |
|---|---|---|
| `minimal` | One file, one ReAct node over the declared tools, answers a `query` input | A first agent, or one step with tools |
| `structured` | `state.py`, `prompts.py`, `gateway.py`, `nodes/agent.py`, `agent.py` | A pipeline that will grow: one file per node |
| `deepagent` | The `deepagents` harness: planning, sub-agents, a to-do list (filesystem denied) | Open-ended research. Heavier and slower |
| `chat` | State carries `messages`; the platform replays the thread each turn | Anything conversational |

All four declare Python 3.12, `timeout_seconds: 300` and the tool `example.echo`, and use
`ChatOpenAI(model="openai/gpt-6-luna", base_url=GRAVITY_LLM_URL, api_key=GRAVITY_RUN_TOKEN)`. They load tools with
the plain MCP client, which is fine until the agent has a gated tool (section 5). Declaring a `messages` key in the
state is what makes an agent a chat: never add it to a one-shot agent "just in case". With `messages`, use
`Annotated[list, add_messages]` and return only the **new** messages, because each turn the platform sends only the
new user turn and the history comes from the checkpoint.

## 4. `manifest.yaml`

Only `name` and `runtime` are required. Unknown fields are rejected (`UNKNOWN_FIELD`), so a field the platform does not
know is reported, not dropped; `display` is the one exception. UTF-8 YAML, at most 64 KB. `gravity validate` prints
every problem at once. If `gravity push` answers `UNKNOWN_FIELD` for a field `gravity validate` accepted, the hosted
platform is older than your CLI: remove the field.

```yaml
contract: v1                       # only v1
name: inbox-digest                 # lowercase letters, digits, single hyphens; at most 64; appears in URLs
version: 1.0.0                     # strict semver; bump to publish again
description: One line a person reads before running it.   # at most 500 characters
kind: interactive                  # transform | interactive (default) | monitor

runtime:
  framework: langgraph             # the only framework
  python: "3.12"                   # quoted; the schema allows 3.10 to 3.13 but validate and the build need 3.12
  entrypoint: src/agent.py:graph   # file:object, relative, no ".."
  timeout_seconds: 300             # 10 to 28800

dependencies:
  lockfile: requirements.lock      # leave as is; the build needs exactly this name at the zip root

inputs:                            # the person's form; arrives as state["inputs"]
  - name: send_to                  # lowercase letters, digits, underscores
    type: email                    # text | textarea | number | boolean | static-dropdown | multi-select | action-choice | email | url | date | secret | file
    label: "Where to send the digest"   # at most 200; write a question plus a hint
    required: true                 # required only while it is asked
    show_if: { deliver: gmail }    # asked only when the "deliver" slot is gmail; names a slot or an earlier input
    # options: [a, b]              # static-dropdown and multi-select, required there, at most 100
    # accept: [pdf, csv]           # file only: extensions without the dot
    # default: "..."               # matches the type; never on file or secret
  - name: labels
    type: multi-select             # several of `options`; the value is a list
    label: "Which labels to read"
    options: [work, personal, promotions]
    min: 1                         # min and max: multi-select only, both optional
  # - name: goal
  #   type: action-choice          # one of this agent's actions; that action runs instead of the defaults
  #   label: "What do you want to do first?"
  #   actions: [digest, reply_drafts]

# choose_one:                      # "either / or": once one is filled the others are not asked
#   - label: "Your notes"
#     inputs: [notes_file, notes_text]
#     required: true               # one of them must be filled

permissions:
  tools:                           # every tool the code calls, by Gravity name, at most 50
    - gmail.read
    - gmail.draft
    - gmail.send
  models:
    tier: standard                 # standard | premium; accepted, not enforced anywhere today

approvals:
  required_for: [gmail.send]       # each must also be declared in permissions.tools or an adapter

triggers:                          # at least one of manual, schedule, webhook
  manual: true                     # default true
  schedule:
    cron: "0 8 * * *"              # five fields, Asia/Kolkata
    consumer_can_change: true      # default true
  # webhook: [github.push]         # the only source today

# state: { max_kb: 64 }            # the older spelling of the notebook alone; never beside `memory`
memory:                            # memory across runs (section 10); leave out for none
  notebook_kb: 64                  # the small notebook, state["memory"]; 1 to 256
  notebook_per: user               # user (every conversation of one person) | thread (one conversation)
  collections:                     # keyed records, gravity.memory.collection(<name>); at most 20
    seen: { per: user, keep_days: 90, max_items: 5000, max_item_kb: 4 }   # keep_days 1-730 (30); max_items to 10,000; max_item_kb to 64 (16)

slots:                             # swappable adapters (section 10)
  deliver:
    label: "Deliver the digest to"
    default: gravity
    # multiple: true               # several picks; each pick's account is asked for and its tools granted
    adapters:
      gravity: []                  # kept in Gravity
      gmail: [gmail.draft]
  x_send:                          # a choice only one step needs: asked when that step runs, not at setup
    label: "How should I send your X messages?"
    default: manual
    ask_in: reply_drafts           # the action that asks it, after its own questions; the pick is kept for later runs
    # show_if: { channels: "X message" }   # only when that step's answers (or setup answers, or other slots) match
    adapters:
      x_api: [x.user_lookup, x.send_dm]
      manual: []
    options:                       # how each pick reads, when the app's name alone does not say it
      x_api: { title: "My X developer app", about: "Sends through your own X app; X bills your developer account." }
      manual: { title: "I'll send them myself", about: "I write each message; you send it." }

actions:                           # what the agent can do (section 10); leave out for one entry point
  - name: digest
    label: "Make the digest"
    default: true                  # runs on a conversation's first run, with the other defaults, in order
  - name: reply_drafts
    label: "Draft replies"
    requires: [digest]             # offered only once these ran in the conversation
    per_row: true                  # works on the rows the person selects: action_inputs["rows"]
    # inputs: [...]                # its own questions, same rules as above
    # schedule: { cron: "0 7 * * *", consumer_can_change: true }   # the person can turn it on
    # run_once: true               # never scheduled or repeated once it succeeded
    # then: [digest]               # run these next, each its own run in the conversation
offer_as: buttons                  # buttons (default) | question: how the actions show under the result
offer_label: "What next?"

# accounts:                        # a site account the person signs in to once on Gravity (section 6, browser.*)
#   - { name: linkedin, site: linkedin.com, label: "Your LinkedIn", purpose: "send messages you approve" }

outputs:                           # what a person may ask the result to become (section 9), at most 8
  summary: {renderer: markdown, label: "Summary", destinations: [download, gmail.draft, gmail.send]}
  report:  {renderer: docx, label: "Report (Word)"}

display:                           # optional hint for how the result shows; never fails a push
  view: report                     # document | report | table | chart | code | files
  field: summary                   # the result key to show
  # chart: {type: line, x: date, y: [reach, likes]}   # up to three y fields

resources:
  memory_mb: 512                   # 128 to 4096; accepted, ignored by the runtime today
```

Rules the validator enforces beyond field types:

- **Inputs**: names unique and not equal to a slot name; `static-dropdown` and `multi-select` need `options`, and no other type may have
  them; `accept` is for `file` only; a default must match its type and be one of the options; `file` and `secret`
  never have a default. A `secret` is sealed when submitted and kept out of every API response, log and
  checkpoint; use it for any key, password or token.
- **Tools**: `app.action`, lowercase, Gravity's own names (never a vendor slug like `GMAIL_FETCH_EMAILS`); no
  duplicates; every name must exist in the catalog (`TOOL_NOT_FOUND`, with a "did you mean"). Output
  `destinations` other than `download` must exist in the catalog too.
- **Approvals**: `required_for` may only name declared tools. An **imported** write tool must be listed there
  (`APPROVAL_REQUIRED`) or the gateway refuses the run. Curated write tools are not forced, but gate anything
  irreversible (`gmail.send`, `slack.send`, `linkedin.create_post`).
- **Schedule**: five fields of digits, `*`, `/`, `-` and commas (no `@daily`, no `MON`); values in range; **not
  both** a day of the month and a weekday; never faster than every 5 minutes; India time. `"0 8 * * *"` is daily at
  08:00, `"0 9 * * 1-5"` weekdays at 09:00, `"*/30 * * * *"` every 30 minutes. The cron is the default; each
  consumer makes their own schedule (one per person for the whole flow, plus one per action that has its own schedule), kept on the version they scheduled until that version is retired. An agent cannot tell a
  scheduled run from a manual one: no trigger field is sent.
- **Triggers**: something must be able to start the agent; `kind: monitor` needs a schedule or a webhook.
- **Slots**: the pick arrives as `state["inputs"][<slot>]` (a list for `multiple: true`). A run is granted
  `permissions.tools` plus only the picked adapters' tools. A slot with `ask_in: <action>` is not asked at setup: that
  action asks it after its own questions (when its `show_if` holds; it may name that action's inputs), the run gets the
  pick's tools and asks to connect the pick's app if needed, and the pick is kept for later runs. Until it is asked, the
  `default` applies, so make the default the pick that needs nothing (no account, no tools). `options` gives each
  adapter a `title` and an `about` line for the person; without it the app's name is shown.
- **Conditions** (`INVALID_CONDITION`): a `show_if` names a slot or an input declared above it, with values that
  input can take (an option, an adapter, `true`/`false` for a boolean). Every condition in one `show_if` must hold;
  a multi-select or multiple slot holds when any pick matches. A hidden question is never asked, never required,
  and its value is dropped, on every surface and for every run (manual, chat, webhook, schedule). A `choose_one`
  member is not `required` on its own; set `required` on the group. A required group with a paste box in it is
  how "upload or paste" is required (a required file alone is still refused by the hosted build).
- **Actions** (`INVALID_ACTION`): names unique; `requires` and `then` name other declared actions and never loop;
  at least one is `default: true`, and a default action's `requires` are defaults declared before it; a
  `run_once` action has no `schedule` and is not a `then` target; an action's own inputs have no action-choice.
- **Accounts** (`INVALID_ACCOUNT`): sites are linkedin.com or x.com; names unique identifiers; `browser.read` or `browser.act` needs at least one account, and `browser.act` must be under `approvals.required_for` (`APPROVAL_REQUIRED`).
- **Memory** (`INVALID_MEMORY`): `memory` and `state` are not both declared; collection names are identifiers;
  there is no shared-across-people collection.
- **Quote** `python: "3.12"` and write `version: 1.0.0` as a plain semver (`1.0` is a YAML float and is refused).
- **Limits**: 50 inputs, 50 tools, 100 options per dropdown, 20 file extensions, 8 outputs, 20 actions, 5 accounts,
  20 memory collections, names 64 characters, labels 200, description 500; the zip at most 30 MB.

`kind` changes what the platform does after the run:

- `transform`: all input at the start, a result at the end. Gravity can deliver it (section 9), so the agent usually needs no write tools.
- `interactive`: calls tools mid-flow, may continue over turns. **Only this kind** gets follow-up runs, chat
  "do more", and the free "not quite it" rerun; the user's words arrive as `inputs["message"]`. Other kinds get a
  restyle of the stored corpus instead.
- `monitor`: needs a schedule or a webhook, and changes nothing else at run time; to remember the last run, declare `memory`.

## 5. `src/agent.py` and the code rules

```python
import json
import os
from typing import Any, TypedDict

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph

try:
    import gravity          # preinstalled on the platform; not on PyPI, not in requirements.txt
except ImportError:         # gravity run, gravity dev, pytest
    gravity = None


class State(TypedDict, total=False):
    inputs: dict            # the person's form answers, keyed by inputs[].name (hidden questions dropped)
    memory: dict            # only with a notebook (memory.notebook_kb): what the last completed run kept
    actions: list           # only with `actions`: what this run does, in order (section 10)
    action: Any             # the first of them
    action_inputs: dict     # the chosen action's own answers; `rows` for a per-row action
    result: Any             # required in the FINAL state: what the person gets


async def load_tools() -> dict:
    """Hosted, a gated tool must come from gravity.tools() (it pauses the run for approval).
    Anywhere else the MCP client serves the same tools under the same names."""
    if gravity:
        return {t.name: t for t in await gravity.tools()}
    token = os.environ["GRAVITY_RUN_TOKEN"]
    client = MultiServerMCPClient({"gravity": {
        "transport": "streamable_http",
        "url": os.environ["GRAVITY_GATEWAY_URL"],
        "headers": {"Authorization": f"Bearer {token}"},
    }})
    return {t.name: t for t in await client.get_tools()}     # exactly the declared tools, named gmail_read


def payload(raw: Any) -> Any:
    """A tool result as data. The gateway reports refusals as plain text, not as an exception."""
    if isinstance(raw, list):
        raw = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in raw)
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except json.JSONDecodeError:
            raise RuntimeError(raw[:300]) from None
    if isinstance(raw, dict) and raw.get("successful") is False:
        raise RuntimeError(str(raw.get("error"))[:300])
    return raw.get("data", raw) if isinstance(raw, dict) else raw


async def graph():
    token = os.environ["GRAVITY_RUN_TOKEN"]            # read inside graph(), never at import
    model = ChatOpenAI(model="openai/gpt-6-luna", base_url=os.environ["GRAVITY_LLM_URL"], api_key=token, max_tokens=2500)
    tools = await load_tools()

    async def work(state: State):
        data = payload(await tools["gmail_read"].ainvoke({"query": "is:unread newer_than:1d", "max_results": 20}))
        ...
        message = {"recipient_email": state["inputs"]["send_to"], "subject": "Digest", "body": "..."}
        raw = await tools["gmail_send"].ainvoke(message)   # gmail.send is under approvals.required_for
        text = raw if isinstance(raw, str) else json.dumps(raw, default=str)
        if "APPROVAL_REJECTED" in text or "APPROVAL_TIMEOUT" in text:
            payload(await tools["gmail_draft"].ainvoke(message))   # the fallback: keep a draft
            delivery = "kept as a draft"
        else:
            payload(raw)
            delivery = "sent"
        return {"result": {"unread": len(data), "delivery": delivery}}

    wf = StateGraph(State)
    wf.add_node("work", work)
    wf.set_entry_point("work")
    wf.add_edge("work", END)
    return wf.compile()                                 # no checkpointer, no store: the platform injects its own
```

| Rule | Right | Wrong (fails the load or the run) |
|---|---|---|
| `graph` is an `async def` factory returning a **compiled** graph | `async def graph(): ... return wf.compile()` | `graph = asyncio.run(build())` at import (validate refuses it); a plain `def`; a hand-rolled object with `astream` (works in `gravity run`, not hosted) |
| Environment is read inside `graph()` | `os.environ[...]` inside it | module-level reads: a cached helper module carries one run's token into the next |
| Imports are absolute from `src/` | `from nodes.agent import build` | `from .nodes import x`, `from src.nodes import x` |
| Every tool called is declared | `gmail.read` under `permissions.tools` | calling an undeclared tool (`TOOL_NOT_DECLARED`) |
| No catalog write-tool name appears undeclared in `src/` | declare it, or keep it out of the source | a write tool's name (`gmail.send` or `gmail_send`) as a string, such as a dict key or an argument: `validate` reports `UNDECLARED_TOOL_CALL` (comments, docstrings and tests are skipped) |
| Accounts only through tools, models only through `GRAVITY_LLM_URL` | `tools["gmail_read"]`, `ChatOpenAI(base_url=...)` | your own Gmail credentials, `OPENAI_API_KEY` |
| The final state sets `result` on **every** run | `return {"result": {...}}` | a last node that returns nothing: hosted the run completes with a `null` result, and a key the next run does not send keeps its old value, so a stale `result` can survive |
| No checkpointer or store passed to `compile()` | `wf.compile()` | passing one: it is replaced |
| `messages` only for conversations, with `add_messages` | section 3 | a plain list reducer (replaces the history) |
| No `interrupt()` of your own | gated tools pause the run for you; `gravity.ask()` asks a question | a bare `interrupt()`: `UNSUPPORTED_INTERRUPT` fails the run |
| A gated call is never wrapped in a broad `except` | call it plainly; if you must catch, `except GraphBubbleUp: raise` first (`from langgraph.errors import GraphBubbleUp`) | `except Exception` around it: that catches the pause for approval. Hosted, the platform raises a caught pause again when the node ends, so the person is still asked, but everything after your `except` already ran once and runs again on resume; under `gravity run` nothing catches it for you |
| Memory calls are few per run | `find(limit=500)` once and reuse the list; `has_many(keys)` for many keys | `get(key)` inside a loop over every record: each call is one blocking request, and hundreds of them stall the run |

Also:

- The input state is `{"inputs": {...}}`, plus `memory` with a notebook, plus `actions`, `action` and
  `action_inputs` with `actions`, plus `messages` if the state declares it. `result` is any JSON-serialisable value (fallbacks `brief`, `outline` are read if it is
  missing); a dict of short named fields reads best.
- After approval a hosted run **re-runs the node that made the gated call from its start**. Put a gated call at the
  end of its own node, after nothing expensive or side-effecting. Several gated calls in one node are approved in
  turn and the gateway answers a repeat with the stored result, so each effect happens once, but work between them
  repeats. Two approvals at once: make them parallel nodes. A node must ask for its approvals in the same order on every pass:
  decisions come back by position, so a memo that skips a call this same run already made hands the next call the wrong
  approval and the run stops with `APPROVAL_OUT_OF_ORDER`. Let such a call through again (the gateway returns its first
  answer without repeating it); skip only what an earlier run made.
- Put pure logic (scoring, parsing, dedupe, formatting) in plain functions under `src/` with tests that need no
  network. Keep the graph thin and one job per node.
- Keep nothing in module-level variables between runs. A warm session may keep them; that is not a contract.
- First turn of a chat: the text comes from `inputs["message"]`, else `query`, `prompt`, `input`, else the JSON of all
  inputs with secrets masked.
- A webhook run gets `inputs = {..., "event": {"repository", "ref", "commits": [{id, message, added, modified,
  removed}]}}`.

## 6. Tools

A tool is an action on a person's account, or on the open web, that the gateway performs for the agent. Names are
`<app>.<action>`, lowercase, Gravity's own. In the manifest use the dot; in code use the underscore
(`tools["gmail_read"]`). The agent is given only the tools in `permissions.tools` (plus the picked adapters'). On
the platform a tool runs either on **Gravity's own account** (the person connects nothing and the cost counts
against the run's budget) or on **the person's own connected account**. The set on Gravity's account changes: on
2026-10-25 it was `apollo.enrich_person`, `browser.*`, `byteforms.*`, `exa.*`, `firecrawl.*`, `hunter.*`,
`scrapecreators.*`, `supadata.get_transcript`, `web.fetch_proxied` and `web.render`, and the live list (what
`gravity tools` reads, `https://gateway.dev.gravity.fast/tools`) carries a `gravity_account` flag on each tool. A
missing connection answers `NEEDS_RECONNECT` as text, so route every result through `payload`. The pages do not ask
a person to connect an app Gravity covers.

Catalog of this release: 56 curated tools and 1374 imported ones in 12 apps: calendar (38), confluence (63), drive (79), github (715), gmail (50), jira (91), linear (39), linkedin (20), notion (51), sheets (42), slack (135), whatsapp (51).

**Curated tools** (reviewed; prefer these):

| Tool | Does | Changes things | Account to connect |
|---|---|---|---|
| `apollo.enrich_person` | match one person in Apollo from their name and company domain (or LinkedIn URL) and return their work email, title and profile links; uses the person's own Apollo account and its credits | no | `apollo` |
| `browser.act` | do one typed action as the person on a site account they signed in to (linkedin.com send_dm, connect, comment; x.com send_dm, reply), with the text given; paced and capped per account per day by the gateway | yes | none |
| `browser.read` | read a page of a site the person signed in to once (an account the manifest declares) through Gravity's browser worker, as that person; returns the final url, the page text and its links | no | none |
| `byteforms.create_form` | create a public Byteforms form from text, email and phone fields, with an optional close date (stop_submissions_after) and submission cap; returns its id and public_id for the link; runs on Gravity's own Byteforms account where Gravity connected one | yes | `byteforms` |
| `byteforms.get_form` | read one Byteforms form by its numeric id (fields, options, link) | no | `byteforms` |
| `byteforms.get_responses` | read the responses to one Byteforms form by its numeric id, newest first, with a cursor for more | no | `byteforms` |
| `byteforms.list_forms` | list the forms on the Byteforms account | no | `byteforms` |
| `calendar.read` | list events on the connected Google Calendar | no | `googlecalendar` |
| `drive.read` | download a file from the connected Google Drive | no | `googledrive` |
| `exa.contents` | read the text of up to 10 URLs from Exa's index; check each URL's status, because the call succeeds even when a page fails | no | `exa` |
| `exa.search` | search the web with Exa, including category 'people' (public profiles) and 'personal site' (portfolios); on Gravity's account through Composio Instant only type auto and at most 10 results, without page text (read pages with exa.contents) | no | `exa` |
| `example.echo` | echoes back its input, for templates and plumbing tests | no | none |
| `firecrawl.scrape` | read one web page through Firecrawl (rendered in a browser, with its proxies, from a chosen country) as markdown or raw HTML; for pages that refuse plain HTTP clients | no | `firecrawl` |
| `firecrawl.search` | search the web through Firecrawl and get the top results with their page content, tailored to a country | no | `firecrawl` |
| `forms.create` | create an empty Google Form with a title in the connected Google account; forms created through the API start unpublished | yes | `googleforms` |
| `forms.get` | read a Google Form's structure, settings, publish state and its responder link | no | `googleforms` |
| `forms.list_responses` | list the responses submitted to a Google Form, with paging and an optional filter for responses after a timestamp | no | `googleforms` |
| `forms.publish_settings` | publish or unpublish a Google Form and turn response collection on or off, for example to close a form at its deadline | yes | `googleforms` |
| `forms.update` | apply a batch of changes to a Google Form in one atomic call (title, description, settings such as verified email collection, and questions); the API cannot create file-upload questions | yes | `googleforms` |
| `github.compare` | compare two refs (base...head) with the commits and changed files between them | no | `github` |
| `github.get_commit` | read one commit with its changed files, line counts and patches | no | `github` |
| `github.list_commits` | list commits on a repository branch, filterable by date range, author or path | no | `github` |
| `github.list_pr_files` | list the files a pull request changes, with line counts and patches | no | `github` |
| `github.list_pr_reviews` | list the reviews submitted on a pull request | no | `github` |
| `github.list_pull_requests` | list pull requests on a repository, filterable by state and branch | no | `github` |
| `github.search_issues` | search issues and pull requests with GitHub qualifiers (repo:, author:, reviewed-by:, is:pr, created:) | no | `github` |
| `gmail.draft` | create a Gmail draft | yes | `gmail` |
| `gmail.read` | read the connected Gmail inbox | no | `gmail` |
| `gmail.send` | send an email from the connected Gmail | yes | `gmail` |
| `hunter.find_email` | find the most likely work email for a person from their name and company domain, with a confidence score; runs on Gravity's account where Composio Instant covers it, charged to the run's budget | no | `hunter` |
| `hunter.verify_email` | check whether an email address is deliverable (valid, accept_all, risky or invalid) before writing to it; runs on Gravity's account where Composio Instant covers it, charged to the run's budget | no | `hunter` |
| `linear.create_issue` | create an issue in a connected Linear team | yes | `linear` |
| `linear.get_issue` | read one Linear issue by id | no | `linear` |
| `linear.list_issues` | list open issues in the connected Linear workspace | no | `linear` |
| `linear.list_teams` | list the connected Linear workspace teams | no | `linear` |
| `linkedin.create_post` | publish a post on LinkedIn as the connected member or an organisation they manage | yes | `linkedin` |
| `linkedin.whoami` | read the connected LinkedIn member's id, name and headline (the author of their posts) | no | `linkedin` |
| `scrapecreators.linkedin_post` | read one public LinkedIn post by URL (text, author, date, engagement and comments); on Gravity's account through Composio Instant | no | `scrapecreators` |
| `scrapecreators.linkedin_profile` | read one public LinkedIn person profile by URL (experience with descriptions, education, about and recent activity) without the person's or the user's login; on Gravity's account through Composio Instant, 1 credit a profile | no | `scrapecreators` |
| `scrapecreators.reddit_search` | search Reddit posts or comments by keyword with sort and timeframe, one page per call with a cursor; on Gravity's account through Composio Instant, no Reddit API key needed | no | `scrapecreators` |
| `scrapecreators.social_profiles` | find a person's linked profiles on other social platforms from one known profile; on Gravity's account through Composio Instant | no | `scrapecreators` |
| `scrapecreators.twitter_profile` | read one public X/Twitter profile by handle (bio, links, verification, audience); on Gravity's account through Composio Instant | no | `scrapecreators` |
| `scrapecreators.twitter_tweets` | read the public tweets X shows for one handle (about 100 popular ones, not a full history); on Gravity's account through Composio Instant | no | `scrapecreators` |
| `sheets.append` | append a row to a connected Google Sheet | yes | `googlesheets` |
| `sheets.read` | read values from a connected Google Sheet | no | `googlesheets` |
| `slack.find_user` | find a Slack user by name, handle or email, for mentions | no | `slack` |
| `slack.list_channels` | list channels in the connected Slack workspace | no | `slack` |
| `slack.read_history` | read message history of a Slack channel | no | `slack` |
| `slack.send` | post a message to a connected Slack channel | yes | `slack` |
| `supadata.get_transcript` | fetch the transcript of a YouTube video with the caller's own Supadata API key (api_key argument) | no | none |
| `web.fetch` | read the text content of a web page by its URL | no | `composio_search` |
| `web.fetch_proxied` | read a public web page or API (GET) through Gravity's rotating proxies, for sites that refuse cloud addresses (Reddit RSS, PullPush, Product Hunt, LinkedIn and X pages); returns the final url, status, content_type and content, HTML as text (format text) or the body as sent (format raw) | no | none |
| `web.render` | render a public web page in a browser and read its main content as markdown, for pages built by JavaScript that web.fetch returns empty | no | `firecrawl` |
| `web.search` | search the web; returns results with titles, links and snippets | no | `composio_search` |
| `x.send_dm` | send a direct message on X to one account (participant_id from x.user_lookup) from the person's own X developer app, billed to their X API account; X delivers it only when the recipient accepts messages from them | yes | `twitter` |
| `x.user_lookup` | look up an X account by its @username (without the @) through the person's own X developer app; returns its id (what x.send_dm takes), name, bio and counts | no | `twitter` |

- `web.search`, `web.fetch`, `web.fetch_proxied` and `example.echo` need no account from the person. `web.fetch`
  takes `urls`, a list. `supadata.get_transcript` takes the caller's own `api_key` argument: model it as a `secret`
  input. `web.render`, `firecrawl.*`, `hunter.*`, `exa.*`, `scrapecreators.*`, `byteforms.*` and
  `apollo.enrich_person` run on Gravity's account. `forms.*` needs the person's Google account, and forms made
  through the API start unpublished (`forms.publish_settings` opens and closes them). The last column of the table
  names the app a person would connect when a tool is not covered by Gravity's account.
- **Imported tools** are the same apps' other actions, synced from the vendor and unreviewed (guarantee
  `experimental`). Their names are verbose (`github.create_an_issue`, not `github.create_issue`), so look them up:
  `gravity tools github`, or `gravity tools issue`. Any imported tool that **changes something** must be under
  `approvals.required_for`, with a fallback, or `validate`, the hosted build and the gateway refuse it. Reads need
  nothing extra. Use an imported tool only when no curated one does the job.
- `web.search` finds pages and does not read them (whether a result carries a snippet is not verified): discovery is "search, then read each page".
  `web.fetch` returns markdown but is an index, not a browser: a page built by JavaScript comes back as a short
  shell with status success, so treat anything under about 500 characters, or with challenge wording, as unreadable
  and say so. For pages that refuse the sandbox or need JavaScript use `firecrawl.scrape` or `web.render`; cap the
  paid calls per run and degrade to one line under "could not do" when a call is refused or the budget is spent. Do not pass a
  `location` to a render: routing through another country measured 36 s against 8 s.
- `web.fetch_proxied` GETs a URL through Gravity's rotating proxies, for sources that refuse the sandbox's cloud
  address: Reddit RSS (`/r/<sub>/search.rss`) and Product Hunt pages answered 200 through it on 23 Oct 2026, PullPush
  through the same proxies on 15 Oct. It is not a browser and changes no TLS fingerprint: Reddit's HTML and `.json`, Capterra, Glassdoor, G2 and Trustpilot
  still answer 403. LinkedIn profile and post pages came back 200 with their JSON-LD for 7 of 8 profiles on 23 Oct;
  some profiles answer LinkedIn's 999 from every address, so confirm a person another way when that happens. X
  profile pages carry the latest posts with dates and links. A blocked status (403, 407, 429, 502, 503 or 999) is tried on up to three proxies. Arguments: `url`, `format` (`text`, the default, turns HTML into lines of text; `raw` returns
  JSON, XML or RSS as sent), `max_chars` (default 50,000, at most 200,000). It returns `url` (after redirects),
  `status`, `content_type`, `content`, `chars`, `truncated`, `attempts`; a 403, 404 or 429 is a result with that status, not
  an error, so check `status`. Each call costs $0.0002 plus $0.005 per MB read (a body stops at 2 MiB), and a run gets at most 200 calls, a refused URL included.
  Private, internal and metadata addresses, ports other than 80/443/8080/8443, and non-http(s) URLs answer
  `URL_REFUSED`. Prefer it over a `proxy_url` secret input: the person supplies nothing.
- `browser.read` and `browser.act` use a real signed-in browser (Steel, a hosted browser Gravity pays for) as the
  person, on a site they signed in to once on Gravity (My agents, then Accounts). They work only in hosted runs;
  locally they answer `NOT_SIGNED_IN`. You cannot open or script the browser: these two tools are the whole
  interface. Declare the site under `accounts` (`linkedin.com` or `x.com`, at most 5), list both tools in
  `permissions.tools` and `browser.act` under `approvals.required_for`. The login and session stay in Gravity's
  vault, and agent code never sees them. `browser.read {account, url}` returns `url`, `text` (up to 40,000
  characters) and `links` (up to 200) for a page of that account's own site only; a redirect to another site is
  refused. `browser.act {account, action, target, text}` does one typed action: `send_dm` (a LinkedIn profile URL,
  first-degree connections only; on X a handle or a URL), `connect` (a LinkedIn profile URL, note optional, at most
  300 characters), `comment` (a LinkedIn post URL), `reply` (an X post URL); `text` is required except for
  `connect`. It is paced (at least 20 seconds between actions on one account) and capped per account per day,
  counted before the action so a failed try uses one (LinkedIn: 25 DMs, 15 notes, 10 comments; X: 15 DMs, 10
  replies). Refusals come back as text codes: `NOT_SIGNED_IN` (ask the person to sign in again, under "could not
  do"), `NOT_ALLOWED` (the person has not allowed this agent to use the account), `NOT_CONNECTED` (the page offers
  no Message or Connect button, or the account takes no DMs from them), `TOO_SOON`, `DAILY_CAP`, `TOO_LONG`,
  `URL_REFUSED`, `BLOCKED_BY_SITE`. Browser time costs $0.10 an hour against the run's budget. Whether the person is
  asked before each action depends on their approval setting (section 10), so never assume they saw it.
- `x.user_lookup` finds an X account by its @username (without the @) and returns its id, name, bio and counts;
  `x.send_dm` sends a direct message to that id. Both run through **the person's own X developer app** (Composio's X
  toolkit has no shared app), so each person connects theirs and X bills their developer account; X delivers a message
  only when the recipient accepts messages from them. Offer it as a slot pick beside a pick that needs nothing
  (`manual`: the agent writes the text, the person sends it), asked by the step that needs it with `ask_in`.
  `x.send_dm` changes things: list it under `approvals.required_for`.
- Outbound HTTPS is open, so code may read public pages and APIs directly (`httpx`, `curl_cffi`). Anything that acts
  on an account still goes through a tool, so the person's connection and approvals apply.
- Locally, `gravity connect <app>` attaches **your** account to your local runs (`gravity connect` alone lists what is
  connected). A tool with no connected account answers `NEEDS_RECONNECT`.
- **A tool that is not in the catalog**: name it `app.action`, write the code that calls it
  (`tools.get("notion_create_page")`), leave it out of `manifest.yaml` (validate refuses unknown names), and describe
  it in `tools_needed.yaml` (name, app, does, `kind: read|write`, args with type
  `string|number|boolean|list|object`, returns, one example). Nothing reads that file automatically: post it to the
  Gravity team. Once the tool is added, upgrade the CLI and declare it. Some kinds are not added (bulk deletes,
  anything that moves money).

## 7. Models, embeddings and images

All three go through `GRAVITY_LLM_URL` with `GRAVITY_RUN_TOKEN`, metered against the run's budget.

```python
model = ChatOpenAI(model="openai/gpt-6-luna", base_url=os.environ["GRAVITY_LLM_URL"], api_key=token, max_tokens=2500)
emb = OpenAIEmbeddings(model="voyageai/voyage-4-lite",        # or google/gemini-embedding-2
                       base_url=os.environ["GRAVITY_LLM_URL"], api_key=token,
                       check_embedding_ctx_length=False)       # send text, not OpenAI token ids
```

- Every reference agent uses `openai/gpt-6-luna`. Other model names are forwarded to the provider; which ones work
  on the gateway's key is not verified beyond those named here and below. `openai/*` embeddings hit a stale key:
  use the two above.
- Images: POST to `<GRAVITY_LLM_URL>/chat/completions` with `google/gemini-2.5-flash-image` or
  `openai/gpt-5-image-mini` and `"modalities": ["image", "text"]`. The picture returns as a data URL at
  `choices[0].message.images[0].image_url.url`, which is what a corpus section's `images` takes. Make pictures in the
  last node: the whole state is checkpointed after every step.
- Every call: `max_tokens` set, structured output (`model.with_structured_output(Schema)`), a short system prompt,
  only the fields the model needs, at most two calls in flight, one or two retries, a fallback when a call fails.
  A failed model call drops the prose, not the run.
- `permissions.models.tier` is accepted and not enforced: do not rely on it as a cost cap.

## 8. Inputs: the form a person fills in

Few fields, each one changing the result; a label that reads as a question plus a hint. The `/app` page asks them
one at a time.

| Type | The person gets | Arrives in `state["inputs"]` as |
|---|---|---|
| `text`, `textarea` | One line, many lines | string |
| `number`, `boolean` | A number, a switch | number, bool |
| `static-dropdown` | One of `options` | string |
| `multi-select` | Any of `options`, between `min` and `max` | list of strings |
| `action-choice` | One of the agent's `actions` (that action runs) | string, and `state["actions"]` is that action |
| `email`, `url`, `date` | A validated field: a wrong form is refused on the question itself ("Enter a web address, like example.com") | string; a `url` typed as `example.com` arrives as `https://example.com` |
| `secret` | A masked field, sealed, never shown again | string, for that run only |
| `file` | An upload limited by `accept` | a signed https link: accept a link, a path or text in your loader |

- Hosted, **every run is checked server-side**: a visible `required` input must be there for manual, chat, webhook
  and scheduled runs alike, and a hidden one (its `show_if` fails, or the unfilled half of a `choose_one`) is
  dropped. Write `show_if: { deliver: gmail }` instead of "only when delivering to Gmail" in a label.
- The **type is checked on every hosted run** too (local `gravity run` does not check it, so convert defensively): a `number`, `email`, `url`, `date` or `boolean` answer of the wrong
  form ("fifty", "not-an-email", "my notion page") is refused with what to type, so your code never sees it. Pick
  the type that matches: a website or a page link is `url`, not `text`. A number cannot carry `min`/`max` (only a
  `multi-select` can), so when your agent keeps a number in a range, say so in the label and in the result ("You
  asked for 50 leads; one run looks for 3 to 20") instead of changing it silently.
- A **required** `file` input on its own is refused by the hosted build (`FILE_INPUT_UNSUPPORTED`) although
  `gravity validate` accepts it. For "upload or paste", put the file and a textarea in a `choose_one` group with
  `required: true`: either one satisfies it. Do not rely on a file input for a scheduled run (not verified).
- On a follow-up run `inputs["message"]` holds the person's new words; an agent that ignores it just repeats itself
  on a paid run.

## 9. Output: `result`, `corpus` and what Gravity renders

| Key | What it is | Who reads it |
|---|---|---|
| `result` | A small dict: counts, a headline, short lists, where something was delivered. **Required.** | The run card, logs, follow-up runs, chat edits |
| `corpus` | The full deliverable as structured content. Optional, but **required for any `outputs` to work** | Every format a person can download |
| `source` | Optional `"live"` or `"stub"` label | The page |

`result`: short named fields; numbers as numbers (`14`, not `"14 emails"`); lists of rows as lists of dicts with the
same keys; say what did not work (`"unavailable": [{"source": "...", "reason": "..."}]`); the one-sentence answer in
`headline` or `verdict` and a longer one in `summary`; a sentence for every empty case instead of a missing section.

`corpus` is a plain dict (or `gravity.Corpus`, which is stricter and only exists hosted). Only `title` is required:

```python
corpus = {
    "title": "Inbox digest, 3 Oct",
    "subtitle": "Last 24 hours",
    "summary": "**14 unread**, 3 need a reply today.",           # 2 to 4 sentences, the answer first
    "sections": [{
        "heading": "Needs a reply",                              # states the point, not the topic
        "body": "Three threads are waiting on you.",             # short paragraphs, - bullets and **bold** only
        "bullets": ["Contract renewal (Acme)"],
        "facts": [{"label": "Unread", "value": 14, "source": "s1"}],
        "table": {"columns": ["From", "Subject"], "rows": [["acme.com", "Renewal"]]},   # every row as long as columns
        "notes": "speaker notes / read-out",
        "images": [{"src": "data:image/png;base64,...", "alt": "...", "caption": "..."}],
        "sections": [],                                          # one level of nesting, same shape
    }],
    "sources": [{"id": "s1", "title": "Gmail: unread, last 24h", "url": "https://mail.google.com"}],
}
return {"corpus": corpus, "result": {"title": corpus["title"], "unread": 14}}
```

Declare which formats a person may ask for under `outputs`; Gravity renders each from the one corpus, on its side
(the renderer is not in your image, so you cannot call it):

| Renderer | The person gets | Built from |
|---|---|---|
| `markdown` | A formatted page; also what is emailed | Everything |
| `docx` | A Word document | Title, headings, prose, bullets, facts and tables as tables, notes as a read-out, sources |
| `pptx` | A slide deck | Title slide, summary, each section as slides (about 10 lines each), each table on its own slide, notes as speaker notes, sources |
| `rows` | A CSV file | **The first table** only, so put the most useful table first; an error if there is none |

Corpus rules: every number in `facts` with a `source` id; every source once in `sources` (with a title or a url);
nest at most one level; a table row shorter or longer than `columns` is rejected; images are `png`, `jpeg`, `webp`
or `gif` data URLs, at most 8 MB each and 12 per corpus; in `body`, headings, links and numbered lists come through
as plain text. A corpus that breaks a rule fails when Gravity renders or delivers it, with the field named, so check it in your own tests.

`destinations` says where an output may go: `download` (default), `gmail.draft`, `gmail.send`. **Only those three
are delivered**: another catalog tool name passes `validate` and then delivers an error receipt. **Gravity** sends
the email, from the person's own connected account, when they choose: the agent needs no Gmail tool for that and
must not declare `gmail.send` for it. One address, the content in the body, no attachment.

Follow-up edits ("shorter", "as bullets", "in Spanish") are the platform's job: it rewrites the stored output using
only what it already says, checks that no number, date, link, address or mention was added or changed (removing or rephrasing is allowed, except in translations and tone changes), has a model look for unsupported claims, and
saves a new version. The agent does not run, so write no revise or redraft nodes. New work ("read #design too")
becomes a proposed new run on the same thread, started only after the person clicks to confirm. Post Slack messages
as `markdown_text`, never `blocks`, so they can be edited.

### How a result becomes a screen (GenUI)

Gravity draws every result itself, on `/app`, in chat and in run history, with one component library. An agent
ships no HTML, CSS or view code, and nothing in `result` runs as code: strings are escaped, links must be
`http(s)`, and unknown block types and fields are dropped. What you control is the **shape and the names in
`result`**, plus an optional hint. Shape results for the renderer, not for a screen.

**How the screen is chosen**, on every read, from the stored result (the page computes nothing):

1. An override set by the Gravity team for that agent, if one exists. You cannot set it.
2. Your `_layout`, if it names at least one real field: it is read as hints (below) and the planner is skipped.
3. The layout planner, a small model that sees only the *shape* of the result (key names, types, masked samples,
   never the content) and decides how each field is drawn, never what is left out. Its answer is cached per agent
   version and shape: renaming, adding or removing a key plans again, changing values does not.
4. Deterministic rules, which always run as the floor.

A final tidy pass drops bookkeeping, keeps one component per collection and folds duplicates. An agent that returns
well-named data gets a good screen with no hint at all. Long lists show five rows at a time (ten for a table) with a
range and previous and next arrows beside their title; every row stays on the page for search, filters and copy. A
summary filed under Details or another tab (key `summary`, `tldr`, `overview` or `key_points`) moves to lead the first
tab, and a site icon for a subdomain falls back to its main domain.

**What the floor draws, and what makes it pick it**

| Component | You get it by returning | The floor picks it when |
|---|---|---|
| Headline line | `headline`, `verdict`, `recommendation` or `summary`: one sentence | the first of those that is at most 160 characters |
| Prose page | a markdown string | longer text under `summary`, `reply`, `report`, `brief`, `conclusion`; `##` sections become tabs from 3 sections up |
| Number tiles | an object of numbers | at most 4 tiles; the rest go to Details; never a 0, never the count of a list that is also shown |
| Facts | an object of scalars, or one record | label and value rows under "Details" |
| Cards | a list of records with a title column | long text columns, more than 6 columns, or sentence-like titles; each row opens to its detail |
| Table | a list of records, or `{"columns": [...], "rows": [...]}` | short columns, at most 6; sortable, stacks on a phone |
| Chart | one label plus one number per record (bar); keys `top_*`, `best_*`, `by_*`; parts that add up to a `*budget` (stacked); `<x>_min` with `<x>_max` (range) | the data has that shape. In a test a dated series with no name column came out as a table, so ask for a line chart through `_layout` |
| Timeline, steps | records with a date and a what; keys `timeline`, `plan`, `itinerary`, `schedule`, `roadmap`, `steps` | a column pair or key like that; 4 or more dated rows also get a scrubber |
| Quotes, chips, bullets | `quote` with `author`; a list of strings of 24 characters or fewer; longer strings | the shape matches |
| "Could not do" notice | `unavailable`, `warnings`, `errors`, `not_covered`, `couldnt_check` | at most 3 items |
| Sources | a list named `sources`, `references` or `citations` with a URL on every row; or a top-level `url` | favicon cards |
| Hero, side by side, carousel | a ranked list with images or places; 2 to 3 rows with 3 or more comparable columns; a list with images | 4 or more ranked rows become "Top picks compared" |
| Drafts | a string or `{subject, body}` under `draft`, `reply`, `message`, `email_body`, `cover_letter` | gets Copy and Edit; 200 characters or more also gets Rewrite |
| Interactive | a loan row (amount, rate, term) gives a what-if calculator; 12 or more money rows a range slider; 3 or more comparable rows a compare tray; a `stages`/`pipeline`/`funnel` list a funnel | derived from the data only; a hint cannot create them |
| Next steps | the manifest's `actions` | always added by Gravity; an agent cannot draw or change buttons |

**Shape the result so that it draws well**

- Name keys for a reader (`programmes`, `shortlist`, `why`, `deadline`). The one-sentence answer goes in `headline`
  or `verdict`; the longer summary in `summary`. A sentence for every empty case goes there too: an empty list is
  dropped unless its key is one of `alerts`, `matches`, `deals`, `drafts`, `flagged`, `issues`, `changes`,
  `results`, `found`, which then reads "None this run".
- Lists of records with the same keys. Each row gets a title (`title`, `name`, `company`, `role`, `programme`),
  a `url`, short state words under `tier`, `band`, `fit`, `status`, `verdict`, `stage` or `priority` (they become
  badges; the first word sets the tone: strong, likely, done, verified read as good; check, partial, possible,
  missing, unknown as caution; not, failed, rejected as bad), and long text under `why`, `summary`, `evidence` or
  `reason`. Nested lists are records too (`people: [{name, headline, why, url}]`).
- Numbers are numbers (`score: 87`), never `"87/100"` and never a formatted copy beside the raw one. Money sits in a
  key such as `price`, `budget` or `fee` with a `currency` nearby. Dates are `2026-10-12` or written out. A column
  `score`, `points`, `rating` or `fit_score` draws as a bar.
- Name bookkeeping so it folds away: suffixes `_read`, `_skipped`, `_dropped`, `_failed`, `_cap`, `_version`, tallies
  such as `pages_read`, and `model`, `tokens`, `cost_usd`, `status`. Every top-level boolean is treated as
  bookkeeping, and a count that sits beside the list it counts (`leads_count`) is dropped. Echoes of the inputs
  are gathered into one "What you asked for" block.
- A column named `id`, `key`, `slug`, `*_id`, `*_code`, `*_key`, or starting with `_`, is never drawn, so do not put
  something the reader needs there. Images come from columns named `image` or `src`; Gravity adds site icons and
  photos itself and ignores an agent's own `photos` or `logos`.
- Do not return HTML, SVG, a JSON string or a markdown table as the only structure. A base64 PDF under `pdf_b64`
  becomes an Open and Download button. Do not split one list into several with identical columns (they fold).

**Optional hints.** `_captions: {"leads_found": "Leads found"}` renames a heading. `_layout` is a list of blocks, or
`{"blocks": [...]}`; an object with only `tabs` does nothing. A block can say:

| Field | Effect |
|---|---|
| `type` | `metrics`, `chart`, `steps`, `timeline`, `facts`, `quotes`, `chips`, `callout`, `cards`, `table`, `bullets`; `hero`, `versus`, `carousel` and `sources` only count as `cards`; interactive types are ignored |
| `key` | a real field of `result` (dotted for a nested one). If no block names a real field, the hints are ignored |
| `caption` | the heading, at most 60 characters (longer is ignored); it beats `_captions` |
| `tab` | a tab name, at most 80 characters. Tabs only exist when the screen has two or more heavy collections, at most 5 |
| `weight` | exactly `lead`, `supporting`, `detail` or `noise` (`noise` is never shown) |
| column roles | on `cards` and `table`: `title`, `subtitle`, `href`, `image`, `rank`, `chips`, `meta`, `facts`, `sections`, `columns` |
| `kind`, `x`, `y` | on a `chart` block: `bar`, `line`, `area`, `slope`, `stack`, `range`; this is how to ask for a line chart |

`limit`, `fold`, `note`, `height`, `compare`, `join` and any interactive field are dropped. **A `_layout` that omits a
list hides that list**, and an unnamed `summary` falls back to a "Written summary" heading, so name every list you
want shown and name `summary` with a `callout`. Hints cannot add behaviour such as compare or what-if. Without
hints you rely on names and shapes, which is usually enough.

```python
result = {
    "headline": "Found 6 leads and drafted 4 emails",
    "summary": "Six companies fit your product. Four have a named buyer.",
    "stats": {"leads_found": 6, "with_buyer": 4},
    "leads": [{"company": "Acme", "url": "https://acme.com", "fit": "strong", "buyer": "Ana", "score": 90, "why": "..."}],
    "pipeline": [{"name": "Lead 1", "stage": "sent", "last_contact": "2026-10-12"}],
    "could_not_do": ["Could not read the pricing page of Acme 3"],
    "pages_read": 41,                                  # bookkeeping: folds away
    "_captions": {"leads_found": "Leads found"},
    "_layout": [
        {"type": "callout", "key": "summary", "weight": "lead"},
        {"type": "metrics", "key": "stats", "weight": "lead"},
        {"type": "cards", "key": "leads", "title": "company", "href": "url", "caption": "Leads to contact", "weight": "lead"},
        {"type": "table", "key": "pipeline", "caption": "Where everyone stands", "tab": "Pipeline", "weight": "supporting"},
        {"type": "bullets", "key": "could_not_do", "caption": "What it could not do", "weight": "detail"},
    ],
}
```

**Keys that steer the "What next" area** (all optional; every action name must be declared in the manifest, or it is
dropped):

| Key | Shape | Effect |
|---|---|---|
| `_offer` | list of action names | which steps to offer and in what order; the first is "Do now" |
| `_offer_notes` | `{action: "line"}`, 160 characters each | the line under that step |
| `_waiting` | `{action: "what it waits on"}`, 80 characters | a greyed step "after ..." |
| `_stages` | `{items: [{name, about, opens}], at: n, note, of: {action: index}}`, 2 to 8 items | a "Step 2 of 5" bar; it guides and never blocks |
| `_meanwhile` | `[{action, why, icon?}]`, up to 2 | steps worth doing while a slow one runs |
| `_keep_running` | `{action: {title, does, off}}`, up to 3, only actions with a schedule | "Works on its own" rows with an On/Off switch |
| `_focus` | `{fields: [top-level keys], about: "one line"}`, up to 12 fields | on a run started by a non-default action, those fields lead on a tab named for the step |

The manifest's `display` only matters when no layout is served; do not rely on it. A result that is not a dict is
shown as a page of text.

## 10. Add-ons

**Approvals.** Load tools through `gravity.tools()` (section 5) and list every tool that reaches other people or cannot
be undone under `approvals.required_for`. **Who is asked is decided by Gravity, not only by your list.** Each person
sets how much they want to be asked (`important`, the default, `always` or `never`), and can stop being asked about
one tool for one agent after approving it three times in a row. Gravity classifies tools itself: money, permanent
deletion, security and ownership changes always ask; on the default setting it also asks for tools that reach people
or publish (sending mail or messages, posting, `browser.act`); a routine write such as a draft does not ask even if
you list it; on `never`, or for a trusted tool, only the first group asks. An imported write tool still has to be
listed (section 4). So **never assume the person saw a send**: make the effect safe by design (drafts first, caps,
a pause switch) and write the fallback. When a call is held: in `gravity run` you are asked (`y` approves, anything
else rejects) and the call waits 240 s (locally every `required_for` tool is asked, so local and hosted differ);
`gravity dev` shows buttons; hosted, it is the person's approval inbox and the run pauses durably for up to 7 days,
then fails "approval timed out". Approved, the call runs with the arguments the person saw. Not approved, the tool
returns text containing `APPROVAL_REJECTED` or `APPROVAL_TIMEOUT` and does nothing, so **always write the fallback**
(keep a draft). A scheduled run that waits for approval is cancelled by the next scheduled tick, which then starts
fresh; a live manual run makes the tick skip.

**Slots and adapters.** When results may go to different platforms, split a base agent from one small file per
platform: `src/adapters/__init__.py`, `src/adapters/<slot>/__init__.py` (the slot's contract as a docstring),
`src/adapters/<slot>/<name>.py` with one async function, and `tests/test_<slot>_adapters.py` that checks every
adapter file has the function, calls only its declared tools and returns a non-empty string. For a `deliver` slot the
function is `async def deliver(report: dict, call, inputs: dict) -> str`, where `call("app.action", args)` is the only
way out. Declare `slots.<slot>.adapters.<name>: [tools]`; the person picks one and only its tools are granted. A
declared adapter with no file, or an adapter file that is not declared, fails `validate`. `gravity adapt` has a
model write one (up to 3 attempts) and keeps it only if its tests pass. Delivery is a slot, not a tool: drafts
before sends, and the default keeps everything on the page. A choice that only one step needs (how to send a message)
is a slot with `ask_in`, asked by that step (section 4).

**Memory across runs.** Four layers, do not confuse them:

| Layer | Declared by | What it is |
|---|---|---|
| Thread checkpoint | nothing (compile with none) | Every state key, per conversation thread, saved after each step. A key the next run does not send keeps its value. |
| The notebook, `state["memory"]` | `memory: {notebook_kb: N}` (or the older `state: {max_kb: N}`) | What the last **completed** run returned under `memory` (or saved with `gravity.memory.save_notebook`); `{}` the first time. Per person and agent (`notebook_per: user`, the default) or per conversation (`thread`). Saved only on success; over the cap it is discarded whole. |
| Collections, `gravity.memory.collection(name)` | `memory.collections.<name>: {per, keep_days, max_items, max_item_kb}` | Keyed records with limits and expiry, per person (`per: user`) or per conversation (`per: thread`). The tool for "leads already shown", "posts I made", a shortlist, a cache. |
| `langgraph.config.get_store()` | nothing | Per person and agent items by namespace and key: `aget`, `aput`, `asearch`, `alist_namespaces`. Its items count toward the same 25 MB and never expire. Do not use it: use collections. Locally in `.gravity/store.json`. |

```python
from gravity import MemoryQuotaError, memory

seen = memory.collection("seen")                  # declared under memory.collections
fresh = [d for d in domains if d not in seen.has_many(domains)]   # one call for many keys
for d in fresh:
    try:
        seen.put(d, {"band": band_of(d), "shown_at": today})       # a dict, at most max_item_kb
    except MemoryQuotaError:
        skipped += 1                                               # nothing was written; say so in the result
seen.get("acme.com")                              # the value, or None
seen.find(where={"band": "Hot"}, limit=50)        # [(key, value)], newest first; equality on top-level fields
seen.delete("acme.com"); seen.count()
memory.notebook()                                 # the notebook as the last completed run left it
memory.save_notebook({"last": "acme.com"})        # becomes the notebook when this run completes
memory.previous()                                 # this conversation's last finished run, or None
```

- There is no user id in the API: the run decides whose memory it is, so code can never reach another person's.
  A write over a limit raises `MemoryQuotaError` and writes nothing; the run goes on.
- Items expire `keep_days` (default 30) after their last write; a per-conversation collection goes with its
  conversation, and everything goes with the person's account or when they remove the agent. The person sees
  and deletes what an agent keeps on My agents; the builder never sees the content.
- `previous()` is `{"action", "actions", "inputs" (no secrets), "result", "finished_at", "truncated"}`; a result
  over 256 KB is left out and `summary` describes its shape instead.
- Every call is one blocking request to the platform, even inside an `async` node.
  Read a collection once with `find(limit=...)` and keep the list, check many keys with `has_many`, and write only
  what changed. A run that makes hundreds of calls in a row is slow; the platform keeps it alive, but the person
  waits.
- Update memory **after** the side effect succeeded, so a failed delivery is retried. Keep the notebook small.
  A follow-up such as "compare 1 and 2" can be answered from memory with no search.
- Under `gravity run` the same calls use `.gravity/memory/` with the same limits, but only if the `gravity` SDK can
  be imported, and it cannot be installed outside Gravity. You cannot exercise memory locally: keep the logic in
  plain functions, fake `memory` in tests, and check the real thing on a hosted run.

**Actions: an agent that does more than one thing.** Declare them (section 4) and branch in the graph:

```python
async def route(state: State):
    todo = state.get("actions") or ["find"]          # [] or absent: an agent without actions
    ...
    if "contacts" in todo:
        rows = state["action_inputs"].get("rows", [])  # the numbers (as strings, "2") of the rows the person selected, 1 to 200
```

- The first run of a conversation does the `default: true` actions, in order, in one run. After a result the
  person gets the actions whose `requires` have completed in the conversation, as buttons or as one "What next?"
  question (`offer_as`, `offer_label`). Gravity draws them from the manifest; return `_offer: [names]` in the
  result to choose and order which to show (an undeclared name is dropped, so an agent can never invent one).
- A click starts that action on the same conversation with the last run's inputs and the action's own answers
  (its `inputs`, asked first, under the same rules). No AI routing. A typed message that names an action
  ("write emails for #2") is proposed as that action. `memory.previous()` and the conversation's collections hand
  the new run what the last one found.
- `run_once`: never scheduled, and skipped by a whole-flow schedule after it once succeeded. `then: [b]`: when
  this action completes, `b` runs as its own billed run on the thread; a failure stops the chain. Loops are refused.
- An `action-choice` input lets the person pick what runs first from the form.

**Asking mid-run.** `gravity.ask("Approve this scoring sheet?", options=["approve", "edit", "cancel"],
default="approve")` pauses the run exactly as an approval does and returns the person's answer (one of the options,
or free text when there are none; options may be action names). A run nobody watches (a schedule, a chain, a
webhook) gets the default at once; with no default it waits and the person is emailed. Like a gated call, the node
re-runs from its start on resume, so ask early in its own node. Under `gravity run` the answer comes from
`--answer`, else the default, else the first option.

**Schedules and webhooks.** `triggers.schedule` (Asia/Kolkata, at least 5 minutes apart) is the whole flow: the
default actions and their `then` chains. Each action with its own `schedule` gets an on/off switch (and the time,
if `consumer_can_change`), one per person per action; it needs defaults for its required inputs, since a tick has
nobody to ask. A scheduled run is an ordinary run with the person's saved inputs, re-checked at every tick against
the version it is pinned to. A scheduled action whose `requires` never ran in the conversation is skipped and the
person is told once. A scheduled run with a new result emails a one-line summary. A tick is paid for with credits and is skipped, with the person told, when the agent is off or paused, the inputs no longer fit, or there are no credits. `gravity schedule` fires the
whole flow locally and answers approvals "no". `triggers.webhook: [github.push]` starts a run from a push (deliveries are HMAC-signed;
there is no CLI command to create one, so do not make an agent depend on a webhook).

**Conversation.** A `messages` state key, `add_messages`, the `chat` template. Tool-call turns are not kept in the
stored transcript.

## 11. The standard an agent is reviewed against

`problem-to-agent.md` section 7 holds the full rules with the evidence behind each. The short form:

1. **Code does the facts, the model does the prose.** Counting, ranking, money, dates, dedupe, thresholds and
   comparison are Python with tests.
2. **Grounding is a gate, not an instruction.** A number, date, URL or quote the model returns survives only if code
   finds it in the source it claims. Drop what is not there, and count the drop.
3. **Never invent, and label every figure** as read from the page, resolved by the agent, or estimated (with the
   basis and a date). Never hand the person a chore ("please confirm"): resolve it or estimate it.
4. **Cite sources** next to every claim and in `sources`. A link the agent built is shown only after it answered.
5. **Fail loudly, degrade honestly.** Every tool result through `payload`; every source reports ok, partial, failed
   or skipped with the reason; the run raises only when every source failed; a module keeps its partial rows when its
   time runs out and says so.
6. **Drafts before sends.** Irreversible actions are drafts or approvals with a fallback.
7. **The answer first, ranked by what matters**, deterministic (same input, same numbers, same order, ties broken by
   name), bounded and honest about size ("first 200 rows", `rows_skipped`).
8. **Small prompts.** Only the fields the model needs, clipped payloads, structured output, `max_tokens`.
9. **Page text is untrusted data.** Pages reach the model under a system prompt that says so, and code grounds every
   name, number and URL that comes back. No write tools driven by content read from the web.
10. **Fix the mechanism, never the case.** A complaint about one company is fixed for every company; each rule is
    tested with more than one site.

## 12. Testing

| What | How |
|---|---|
| The manifest and the build's checks | `gravity validate`: the same schema as the server, the entrypoint, imports, undeclared write tools, `python == 3.12`, adapters; compiles the ARM64 lockfile |
| Your logic | `pytest tests/` on plain functions with fixtures saved from real answers; no network |
| The graph | A fake world: fake tools returning gateway-shaped payloads, a fake model answering each schema deterministically, one test that runs the whole graph and asserts every rule, plus one test per loud failure |
| A real run | `gravity run --input ...` or `gravity dev`, against the real gateway and models; record time, calls and cost |
| As the user | Push, then run from the real page as a user would, with an uploaded file, on every surface |

Run `pytest` as its own step **before** `gravity validate`, `build` and `push`, and do not let a pipe hide its exit
code. Tests run in your own virtualenv, where the `gravity` package is not installed, so import it behind a guard.
Local runs are not metered and do not pause for approvals or questions: a hosted run is the only check of budget,
checkpointing, durable approvals, `gravity.ask()`, action buttons, chains and outputs. Test each action with
`gravity run --action`, and each `show_if` with the inputs that hide and show it.

## 13. Publish and review

1. `gravity validate`, then `gravity build` (packs `build/agent.zip` and `build/build.json`), then `gravity push`.
2. The control plane stores the zip and starts the build: it re-validates with the same rules (the manifest must
   match the one in the zip, the name and version must match, Python 3.12, no required `file` input outside a
   `choose_one` group that has a non-file member,
   `requirements.lock` at the root, no undeclared write tool), scans for secrets (a hit blocks the build; a
   dependency audit is report-only), builds the ARM64 image and starts a runtime. `gravity push` waits (up to 45
   minutes) and `gravity agents` shows `queued`, `building`, `ready`, or `failed` with the reason.
3. The first builder to push a name owns it. The same version with the same source is a no-op; the same version with
   different source is refused (409: bump `version`). A pushed version is frozen.
4. A new version is **private** until the Gravity team approves it. Review states: not
   submitted, submitted (pending), approved, rejected (notes of at least 10 characters). An agent is listed only
   while its **newest** version is ready, public and approved, so pushing a new version takes the agent off the shelf
   until that version is approved. An off switch refuses new runs and pauses schedules.
5. Only the two newest ready versions of an agent and the newest public one keep a runtime; older ones become
   `legacy` and cannot be re-pushed. A push can fail at runtime creation when Gravity's capacity is full: try again
   later or tell the team.
6. There is no submit command. Tell the team what the agent does, example inputs, the accounts it needs, and what a
   good result looks like. `gravity agents` shows their notes and why an agent is off.
7. The team may try your latest private version with connections that differ from yours: an optional tool must degrade
   to one refused call and one line, not a fan-out of refusals. You can also run your own not-yet-approved version
   from the web app.

## 14. Errors you will meet

| Code or message | Meaning | Fix |
|---|---|---|
| `MALFORMED_YAML`, `INVALID_MANIFEST`, `MISSING_FIELD`, `UNKNOWN_FIELD`, `LIMIT_EXCEEDED` | Not valid UTF-8 YAML, empty, a field missing or unknown, or over a limit | Read the location and remediation; `gravity validate` prints every issue at once |
| `INVALID_CONTRACT_VERSION`, `INVALID_FRAMEWORK`, `INVALID_PYTHON_VERSION` | `contract` is not `v1`; `framework` is not `langgraph`; Python is unquoted or not 3.12 | `contract: v1`, `framework: langgraph`, `python: "3.12"` |
| `INVALID_AGENT_NAME`, `INVALID_AGENT_VERSION`, `INVALID_ENTRYPOINT` | Bad slug; not semver or unquoted; not `file.py:object` inside the project | Fix the field |
| `INVALID_INPUT`, `DUPLICATE_INPUT` | An input or slot name, options, accept, default, a clash, an adapter name | Section 4 |
| `INVALID_TOOL_NAME`, `DUPLICATE_TOOL`, `TOOL_NOT_FOUND` | Malformed or repeated tool name; not in the catalog (also in a slot or an output destination) | `gravity tools <text>`; upgrade the CLI if a tool was added recently; or `tools_needed.yaml` |
| `APPROVAL_REQUIRED` (validate, build, gateway) | An imported write tool has no approval | List it under `approvals.required_for`, with a fallback |
| `APPROVAL_REQUIRED` (inside a hosted run) | A gated tool was called through the plain MCP client | Load tools with `await gravity.tools()` (section 5) |
| `INVALID_APPROVAL`, `INVALID_TRIGGER`, `INVALID_KIND`, `INVALID_OUTPUT` | `required_for` names an undeclared tool; nothing can start the agent, a bad cron, both day fields, faster than 5 minutes; a monitor without a trigger; a bad output name or destination | Section 4 |
| `INVALID_CONDITION`, `INVALID_ACTION`, `INVALID_MEMORY` | a `show_if` on a later input or a value it cannot take, a `choose_one` member required alone; an action that requires or chains to an undeclared one or loops, no default action; `memory` beside `state`, a bad collection | Section 4 |
| `INVALID_ACCOUNT` | an account on a site other than linkedin.com or x.com, a name used twice or not an identifier; `browser.*` declared with no account to act through | Section 6 |
| `UNDECLARED_TOOL_CALL` | Source names a catalog write tool the manifest does not grant | Declare and gate it, remove the call, or make a deliver-only tool an output `destination` |
| `FILE_INPUT_UNSUPPORTED` (hosted build only) | A required `file` input | Make it optional, add a text fallback |
| `SECRET_FOUND` (hosted build only) | The secret scanner matched something in the upload | Remove it, fixtures included; rotate it if it was real |
| `TOOL_NOT_DECLARED`, `TOOL_UNAVAILABLE` (run time, as tool text) | Code called a tool the manifest does not grant; the tool is not served | Declare it, or stop calling it |
| `NEEDS_RECONNECT` | The account for that tool is not connected, or its sign-in lapsed | `gravity connect <app>`; hosted, the person connects it on `/app` |
| `APPROVAL_REJECTED`, `APPROVAL_TIMEOUT` | A gated call was not approved | Expected: your fallback must run |
| `APPROVAL_OUT_OF_ORDER` | A resumed node asked for its approvals in a different order, or skipped a call this run had already made, so a decision went to the wrong call | Ask in the same order on every pass; let the call through again (section 5) |
| `UNSUPPORTED_INTERRUPT` | The code called `interrupt()` itself | `approvals.required_for` for a tool, `gravity.ask()` for a question |
| `MemoryQuotaError` (`MEMORY_QUOTA`) | A memory write over a limit: item size, items in the collection, 25 MB, 5,000 writes, the notebook's cap | Nothing was written: lower the volume, raise the manifest's limit, or skip and say so |
| `gravity.memory.MemoryError` | An undeclared collection, a key that is empty or over 512 characters, a non-dict value | Declare it under `memory.collections`; keys are short text, values dicts |
| "namespace 'c' is the platform's" | `get_store()` was used on a reserved namespace | Use `gravity.memory` for collections |
| `Fill in the required input(s): …`, `pick one of …` (hosted, 400) | A visible required input is missing, or a dropdown, multi-select or action choice is out of bounds | Check `show_if` and defaults; `gravity run` reports the same |
| "X needs Y to run first", "X runs once" | An action's `requires` has not completed in the conversation, or a `run_once` one already ran | Expected; the buttons show only what may run |
| `402 BUDGET_EXCEEDED` | The run spent its model budget | Fewer or smaller calls; `max_tokens`; at most two in flight |
| `URL_REFUSED`, `FETCH_FAILED`, `PROXY_LIMIT` (`web.fetch_proxied`) | Not a public http(s) URL on a web port; no proxy reached the page (connections or timeouts on three proxies); the run used its 200 proxied fetches | Fix the URL; retry later or degrade to one line under "could not do"; fetch fewer pages |
| `NOT_SIGNED_IN`, `NOT_ALLOWED`, `NOT_CONNECTED`, `TOO_SOON`, `DAILY_CAP`, `TOO_LONG`, `BLOCKED_BY_SITE` (`browser.*`) | The person has not signed in to the site or allowed this agent; the page or account does not allow it; actions are paced (20 s) and capped per day | Say so under "could not do" (section 6) |
| "finished without a result" (`gravity run`), `null` result (hosted) | The final state has no `result` | Return `{"result": ...}` |
| "could not load the agent" | An import error, a relative import, env read at import, or the graph built at import | Section 5 |
| Lockfile will not compile | A dependency has no Linux ARM64 wheel | Pick another version or package |
| 409 "version exists" | The same version was pushed with different source | Raise `version` |

## 15. Where the other documents are wrong

`gravity guide` (the builder guide), `AGENT_STANDARD.md` and `problem-to-agent.md` are all useful, and each has lines
the code has outgrown. When they disagree with this file, this file and the code win.

| A document says | The code does |
|---|---|
| "There is no Gravity SDK" / "No Gravity imports" | `import gravity` exists on the platform and is required there for approval-gated tools, `gravity.memory` and `gravity.ask()` |
| "Only approvals can pause a run" | `gravity.ask()` pauses for a question too |
| Memory is `state.max_kb` only | `memory.notebook_kb` (same thing) plus collections with limits and expiry |
| Manual runs are not checked for required inputs | Every run is, after the input rules |
| Each tool runs on the person's own account | Gravity's own account first where it covers the tool (section 6) |
| One schedule per agent | One for the whole flow plus one per action |
| Hand-rolled `astream` objects are fine | Hosted needs a compiled LangGraph graph |
| `timeout_seconds` is 10 to 900, "900 s cap" | 10 to 28800 |
| "Outbound HTTPS only" | Outbound is open and unfiltered; HTTPS is a safe assumption, not an enforced rule |
| "Undeclared network imports (warning)" | Only tool-name string literals are scanned |
| Triggers are manual and schedule | `webhook: [github.push]` exists |
| Input types lack `secret` | `secret` exists |
| The bundle omits `tools_needed.yaml` | It ships |
| "The final state has no result" is a server error | Hosted completes with `null`; only `gravity run` warns |
| Local runs share one test account | `gravity login` runs act on accounts you connected; the shared account is for `GRAVITY_DEV_TOKEN` only |
| About 1,100 or 1,400 tools | See the live count in section 6 |
| `permissions.models.tier` caps spend, `resources.memory_mb` is clamped | Neither is enforced today |
| Experimental tools never run hosted | They run, gated by approval |

`problem-to-agent.md` describes five Gravity agents as worked examples. Their source belongs to Gravity and is not in
your folder: read them as examples of structure, and follow the method.

## 16. Before you hand it over

- [ ] `manifest.yaml`: `contract: v1`, a clear `description`, input labels that read as questions, `python: "3.12"`
- [ ] Every tool the code calls is declared; every account action goes through a tool; every imported write tool is
      under `approvals.required_for`; tools are loaded with the `gravity.tools()` fallback loader
- [ ] `src/agent.py` defines `async def graph()` returning a compiled graph; environment read inside it; imports
      absolute from `src/`
- [ ] Every tool result goes through `payload`; a failed source is named in the result
- [ ] Questions that depend on another answer use `show_if`; "upload or paste" is a `choose_one`; no required
      `file` input on its own
- [ ] Numbers, counts, ranking and dates come from code; the model never owns a number
- [ ] Irreversible actions are drafts or approvals, with a fallback that does not assume the person saw the prompt; no broad `except` swallows `GraphBubbleUp`
- [ ] The final state sets `result` every run; a report also sets `corpus`, with its formats under `outputs`
- [ ] `result` is shaped for the screen (section 9): keys named for a reader, numbers as numbers, bookkeeping named to
      fold away, a sentence for every empty case
- [ ] Every figure traces to a source; nothing invented; failures named
- [ ] Memory goes through the notebook or `gravity.memory`, with `MemoryQuotaError` handled; several jobs are
      `actions`, each tested with `gravity run --action`
- [ ] Tests: fake world, a full-graph test with injected failures, `pytest` as its own step
- [ ] `gravity validate` passes; a `gravity run` or `gravity dev` run produced the result you expect
- [ ] No keys or secrets in any file; nothing the code needs lives outside `src/` and `tests/`

## 17. Contract v2 (preview): capabilities instead of tools

Everything above is contract v1, which is what Gravity's hosted platform runs. Contract v2 is a preview: build on it
only when the person says their gateway serves v2 (`gravity connect` and `gravity check` work against it). The CLI
reads both, picked by the manifest's `contract`; `gravity guide --contract v2` is the full v2 guide and
`AGENT_STANDARD_V2.md` its exact rules.

In v2 the manifest never names an app or a tool. It names **capabilities**, `<shape>.<verb>` (`message.list`,
`issue.create`), and the person picks the app (Gmail or Outlook, Linear or Jira) and the place in it (a channel, a
project) when they set the agent up. Records come back in the shape's own fields whichever app they picked.

```yaml
contract: v2                        # capabilities: the agent names what it reads and changes, the user picks the app
name: inbox-digest
version: 1.0.0
description: Summarises your unread email from the last day and sends you a short digest.
kind: monitor                       # transform | interactive | monitor
runtime:
  framework: langgraph
  python: "3.12"
  entrypoint: src/agent.py:graph
  timeout_seconds: 300
dependencies:
  lockfile: requirements.lock
models:
  tier: standard                    # v2 has no `permissions`: the model tier is top-level
inputs:
  - { name: send_to, type: email, label: "Where to send the digest", required: true }
sources:                            # what it READS: gravity.read("inbox")
  inbox:
    capability: message.list        # <shape>.<verb>; `gravity capabilities message` lists them
    default_app: gmail              # the app it is built for; the user may pick another
    label: "Your email"             # the question the user answers at setup
    window: 24h                     # 24h, 7d, 4w back; next_24h ahead; since_last_run
    filters: { unread: true }       # the shape's standard filters only
writes:                             # what it CHANGES while it runs: gravity.act("send", draft={...})
  send:
    capability: message.send
    default_app: gmail
    label: "The account to send the digest from"
  draft:
    capability: message.create      # the fallback when sending isn't approved
    label: "Drafts, in the same account"
    same_as: send                   # the same app and place as `send`: the user is asked once
outputs:                            # what the platform delivers after the run, where the user picks
  digest:
    renderer: markdown
    label: "The digest"
    destinations: [download, document.create]
    default: { destination: download }
approvals:
  required_for: [message.send]      # each call waits for a person's yes
# built_ins: [supadata.get_transcript]   # tools built into the gateway, no app to pick
triggers:
  manual: true
  schedule: { cron: "0 8 * * *", consumer_can_change: true }
memory: { notebook_kb: 64 }         # memory across runs, as in v1
# state: { max_kb: 64 }             # the older spelling of the notebook alone; never beside `memory`
resources:
  memory_mb: 512
# display, choose_one, actions, offer_as, offer_label: the same as in v1 (section 4)
```

What changes from v1:

- No `permissions`, `slots` or `accounts`. What the agent reads goes under `sources`, what it changes while it runs
  under `writes`, and what the platform delivers afterwards under `outputs`, whose `destinations` are capabilities too.
  `models.tier` is top-level. `built_ins` names the gateway's own tools that need no app.
- `actions` is the same as in v1: what a *person* can ask the agent to do (section 10). It is not what the agent
  changes; that is `writes`.
- Code reads and writes by the names the manifest gives, through the `gravity` SDK (on the platform; locally
  `uv pip install -e <platform repo>/packages/gravity-sdk`, it is not on PyPI yet):

```python
import gravity

inbox = await gravity.read("inbox", filters={"unread": True})   # {"records": [...], "complete": ...}
done = await gravity.act("send", draft={"to": ["a@b.co"], "subject": "Digest", "text": text})  # the shape's fields
tools = await gravity.tools()   # one LangChain tool per source and write: sources_inbox, writes_send
```

- `gravity validate` checks that every `gravity.read` / `gravity.act` / `gravity.built_in` name in the code is
  declared, and warns about a source or write with no `default_app` or an output with no `default`.
- `gravity capabilities [shape|capability|--app <app>]` lists what exists and which apps serve it;
  `gravity check <capability> --app <app>` tries one on the person's own account (a write only previews unless `--run`).
- `gravity run --use inbox=outlook --use send=outlook` (or `--setup picks.yaml`) picks the apps for a local run,
  as a person's setup would; anything not picked runs on its `default_app`. `gravity init my-agent --contract v2`
  starts from the v2 templates.

The v2 errors:

| Code | Means | Fix |
|---|---|---|
| `UNKNOWN_CAPABILITY` | Not `<shape>.<verb>`, or no app serves it (an app or tool name written as a capability) | `gravity capabilities <shape>` |
| `CAPABILITY_BLOCKED` | Policy keeps every agent off it | Use a capability that does the job directly |
| `INVALID_SOURCE` | A source names a write, or its `window` is not a time range | Sources read (`list`, `search`, `get`); changes go under `writes` |
| `INVALID_FILTER` | A filter the shape does not have, or a value outside its standard ones | The shape's filters, from `gravity capabilities <shape>` |
| `INSTANCE_MISMATCH` | A setup made for another agent version | Set the agent up again for this version |
| `MISSING_PICK` | A required source or write has no app, an app needs a place nobody picked, or a required input is empty | Pick it (`--use name=app:resource=id`) |
| `INVALID_PICK` | The app cannot do the capability, the builder limited `apps`, or the place does not fit the app | `gravity capabilities <capability>` shows who can |
| `UNKNOWN_FIELD` on `permissions` or `sources` | A v1 field in a v2 manifest, or the other way round | Keep each manifest to one contract |
