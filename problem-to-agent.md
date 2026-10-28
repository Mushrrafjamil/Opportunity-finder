<!-- gravity-cli 0.10.0 · sha256:82557d2d70979d681d7eb0810a10b44d0ed56cb23f3dc3b81f652b11761b1c59 · kept up to date by the Gravity CLI; edit a copy, or delete this line to keep your edits -->
# From a problem statement to an agent that holds up

**Updated:** 2026-10-25. **Worked examples:** five agents built from one-paragraph briefs between 14 and 25 October
2026, all hosted on the Gravity dev platform and run from the consumer page. Three **research** agents:
pain-point-discovery (1.0.5, five versions, about a dozen hosted runs), job-scout (1.0.16, sixteen versions in two
days) and study-abroad-advisor (1.0.22, twenty-two versions in two days). Two **acting** agents, which do the work
and not only report: lead-gen (1.3.13 hosted, 1.4.0 ready to ship) and hiring (0.1.48 hosted, built over three days). **Companions:**
`Gravity.agent.md` in this folder (how an agent is written, the rules that fail a load, the tools, and how a result
is drawn) and `Gravity.getting-started.md` (the plain overview). If this file and the platform disagree, the
platform wins.

## Why this file exists

None of the three agents came out of a prompt. Each came out of a loop that ran for days, every version an
answer to something a real run showed, and the loop is the same for all three. This file writes it down so
the next problem statement gets the same treatment without re-learning it: what to read, what to verify,
what to write before code, which rules make the output honest, how to test as the user, and how a complaint
becomes a general rule and a version. Each step carries its instances from the three builds, so an agent
(a person or a coding model) can see what the abstract step looked like in practice.

| Agent | The brief, as it arrived | Why one prompt could not deliver it |
|---|---|---|
| pain-point-discovery | "Customer Pain Point Discovery": eight outputs (themes with counts and trend, competitor weaknesses, why people leave, why products shut down or pivoted, opportunities checked against existing products, the user's own product apart, the user's country, method and limits), eight rules, ten edge cases, country tailoring | a model answering from memory cannot count unique people, cannot prove a 30-day trend, cannot link a quote to a real post, and breaks on the first keyword with two meanings |
| job-scout | an agent that finds jobs or internships tailored to a person (country, city, qualifications, experience), says how likely they are to be selected, compares the jobs, drafts the mail, finds the application link, the company's reputation and other people's experience, and people to contact; uses the best platforms for that country; handles error cases; is tested like a user would use it | nobody has the hiring data a "chance of selection" needs; the boards differ per country and refuse datacenter clients unevenly; drafts written by a prompt read as machine writing |
| study-abroad-advisor | a study-abroad consultant: universities within a budget, eligibility, scholarships and alumni, the job market, a timeline, cover letters, "and more", for Germany, the US, the UK and Australia; build on open source first; "test the whole thing after building, like a user would". The same day it grew three times: a named suite (timeline, uni finder, scholarship matcher, document checklist, expense calculator, accommodation guide), "no empty cells: resolve or estimate, never make anything up, say when it is an estimate", then an education-loan finder with yearly repayments | it is several products in one, each with its own source of truth and arithmetic; every fact lives on a page and a wrong number is worse than a missing one; the output is read as a product screen, cell by cell; the brief keeps growing while you build |
| lead-gen | "Find me 30 UK restaurant groups that would buy my rota software, get me the right person, write to them and keep at it." | the right person, a working email, a real recent fact and a follow-up in the same thread cannot come from memory; sending, replies, opt-outs and timing need state and consent |
| hiring | a hiring desk for one role: research the role, find people or take applications, score them against the owner's criteria, write outreach in the owner's voice, send it, read replies, test, book interviews, draft the offer | every fact about a candidate must be checked, a score may follow only the owner's criteria, each outward email, invite and offer needs the owner's OK, and the process runs over days |

Four properties of such a brief decide the method:

1. **It is several products in one.** Each needs its own source of truth and its own arithmetic. A single
   prompt that "knows" tuition fees, hiring odds or churn reasons is the thing users already distrust in
   commercial tools.
2. **Every fact lives somewhere** (a programme page, a job board's JSON, a Reddit thread, a bank's rates
   page), and a wrong number is worse than a missing one. So the model may read, but code must own every
   number.
3. **The output is read as a product screen**, not a document. Reviewers judged it cell by cell ("why no
   rates", "Germany is free", "why did it not find IBM", "it says scholarships found but I can't see them").
4. **The brief keeps growing while you build.** The spec has to absorb additions without a rewrite, which
   means modules with one fact source each, shared failure handling and one result shape.

## What Gravity expects from an agent

An agent is its own software, an automation system, and not a prompt wrapped in a form. A person can get a simple
answer from a chat assistant in one to three prompts; Gravity lists only what that cannot do. In practice:

| We expect | Which means |
|---|---|
| A job done from end to end | Several steps and sources, one outcome the person can act on. If one clever prompt would do it, do not build it here |
| Data that is real | Every figure, name, link, date and quote comes from something read in this run, with its source. A gap is stated, never filled |
| Everything fact-checked in code | The model extracts; code checks the extraction against the source text and drops what is not there, counting the drops |
| Personal to the request | Country, budget, role, market, voice and the person's own data change the result. A generic result is a failure |
| Honest limits | Failed sources, estimates (with their basis and a date) and unverified items are said in plain words |
| Action only with consent | Drafts before sends; approvals with a fallback; caps; a stop switch; an effect never happens twice |
| A reader's screen | Keys named for a reader, numbers as numbers, a sentence for every empty case (§12) |

What we do not want: an answer from memory with a list of names, a wrapper around one prompt, a table of guesses, a
number nobody checked, a link nobody opened, an email that goes out unseen, or a result that is a wall of prose.

There are two generations of agent. The **research** agents (the first three) gather and compare information and
report it. The **acting** agents (lead-gen and hiring) do the work too: they write and send messages once the person
approves, read replies, follow up, book interviews, keep a tracker and remember every person they dealt with. The
method below is the same for both. §17 adds what acting needs.

## A request becomes an app, not an answer

A user types one sentence. A chat model answers it from memory with a list of names, and the
user's next step is to go and check deadlines, prices, process and what is nearby, one site at a
time. In Gravity that sentence is served by an agent that behaves like an app: it asks for the few
facts the sentence left out, looks at the problem from every side the user would otherwise check
one by one, and shows a comparison the user can act on. Write each use case in this shape before
designing anything:

| Step | What to write |
|---|---|
| Request | The sentence as a user would type it. |
| Becomes | The kind of app the agent is. |
| Asks for | The inputs. Few fields, each one changes the result. |
| Fronts | Every side of the problem the user would check next, each with a readable source. |
| Shows | A comparison or a plan with the source and status on every item. Never a list of names. |

A front earns its place only when a readable source exists for it and it changes what the user
does. When that source is empty or blocked, the front gets its own "nothing found" line instead
of disappearing.

**Rental finder**

- Request: "Find me a two-bedroom flat in Delhi under 25,000 a month near my office in the north."
- Becomes: a rental finder for one city.
- Asks for: country and city; budget; bedrooms, or shared and for how many people; the places the
  user goes regularly (office, college, a class) and how they travel; what matters in the area
  (quiet, market, metro).
- Fronts: live listings, each with the site it is on and whether it is still available; the going
  rate for that area, so each listing reads as cheap, fair or dear; the area itself: what is nearby
  (market, hospital, gym, main road), how it is connected, what people who live there say; the
  journey to each place the user goes, time and route at the hour they travel; the next locality
  over, where a cheaper or better flat a few minutes away is one the user never searched for; the
  trade-off between two options written out (this one costs more but sits on the main road and is
  ten minutes from the office).
- Shows: the flats side by side with area, commute, price against the area rate and source, then
  the "also consider" localities.

**Health insurance picker for parents**

- Request: "Pick a health insurance plan for my parents, both over 65, in Pune."
- Becomes: a plan comparison for seniors.
- Asks for: ages, city, existing conditions, budget, the policy they already hold.
- Fronts: plans that accept their age; what each covers and does not (existing conditions and their
  waiting periods, eyes, dental, day care, room-rent cap, co-pay); the hospitals near them that are
  cashless under each plan; the premium at their age and how it rises each year; renewal terms
  (lifetime renewal, what changes at renewal, how often it comes up); the insurer's claim record
  (settlement ratio, time to pay, complaints); the application (tests, documents, porting the
  current policy without losing served waiting periods).
- Shows: a full comparison report, plan by plan, with the pick and the reason.

## The method at a glance

```
problem statement
   │  read as outcomes, rules and edge cases; say what you will refuse and why         §1
   ▼
research: products, living open source, quality markers; build or wrap               §2
   ▼
probe the platform's tools and every data source, from where the agent will run      §3
   ▼
decompose into modules, each with a fact source; code decides, the model extracts    §4 §5
   ▼
spec with a testable acceptance table                                                §6
   ▼
build: honesty rules in code, one file per concern, failure boundaries               §7 §8
   ▼
unit tests with fixtures and fakes ─► local real run ─► gravity push ─► run from the page as a user   §9
   │                                                                              │
   └── the user's screenshot ─► root cause ─► a general rule ─► next version ◄────┘   §10 §11
   ▼
result shaped for the platform's renderer (no view code)                             §12
   ▼
ship: push, wait for the build, re-run hosted, tell the team; reconcile spec and README  §13
```

| Step | What you produce | Done when |
|---|---|---|
| 1. Read the statement into a contract | outcomes, rules and edge cases as testable lines; a traceability table; refusals and reinterpretations with reasons | every clause has a planned mechanism, a test and a place in the output |
| 2. Research what exists | a dated "prior art used" list: mechanisms taken, tools rejected and why; quality markers for the output | build-versus-wrap decided with a reason |
| 3. Probe the platform and every source | what each gateway tool really returns and where it fails; an access table per source: URL, fields a 200 returns, measured rate limit, how it fails | probed from the machine the agent will run on, not only your laptop; fixtures saved with dates |
| 4. Decompose into modules | one row per promise: fact source, what code computes, what the model does | no row without a fact source |
| 5. Split code from model | the list of what code computes and what the model may decide; a node pipeline with one job per node | "the model never owns a number" holds for every figure in the output |
| 6. Write the spec | `docs/<date>-<agent>-agent.md` | problem, outcome, scope, assumptions, numbered acceptance criteria that name their check, architecture, file impact, alternatives, verification plan |
| 7. Apply the honesty rules | grounding gate, labelled tiers, failure boundaries, bounded model calls, capped paid tools, checked prose, small memory | each rule is code with a test, not prompt wording |
| 8. Build in order | pure logic and tests, parsers over fixtures, the graph against a fake world, the report through every renderer, prompts last | the fake-world test keeps every rule; pytest runs as its own step before validate, build and push |
| 9. Test as the user, on every surface | a run log with time, calls, cost, counts and what each run showed; the matrix of profiles | local run, hosted run, consumer page, run history all read as a user would |
| 10. A complaint becomes a rule | a findings table: what the user saw, the root cause, the general rule and its version | each finding traced to the page or mechanism, fixed for every site, tested, bumped, re-run with the same inputs |
| 11. Probe the slow module | a tiny agent that runs one module against the real gateway and logs the model's input | the module's blanks are explained from its inputs, not guessed from the graph |
| 12. Shape the result for a reader | reader-facing keys, numbers as numbers, a layout hint with tab names; no view code | thin, empty, failed and global runs each carry a sentence where a section would be; checked in chat and history |
| 13. Ship and record | check the diff, push, hosted re-test, tell the team; README and spec verification | the spec's results section matches the deployed version |

## 1. Read the statement into a contract

Read the use case three times, each time pulling out one kind of line:

- **Outcomes**: the sections the user gets. Turn every noun into a feature row. The pain-point statement
  had eight; job-scout's paragraph had ten.
- **Rules**: the numbers and constraints. Turn every adjective into a rule. Pain-point: at least 3 different
  people per theme, at most 10 posts from one thread, growth only with 5 or more posts in the last 30 days,
  buying intent only when the post says so, never invent a cause, own product never mixed with competitors,
  every claim linked.
- **Edge cases**: the ways real data breaks the rules. A keyword with two meanings, non-English posts,
  deleted posts, sarcasm, a pivoted product, non-product reasons for leaving, fewer than 50 complaints, a
  named competitor with nothing.

Write the rows into the spec before any code. Every later complaint ("why did it not find IBM") must map
back to a row, and a row with no test is not done.

| Words in the job-scout statement | What it became | Where |
|---|---|---|
| "internship / jobs" | one manifest with a `looking_for` dropdown; internship boards differ per country | `manifest.yaml`, `src/boards.py` |
| "tailored to user (country, city, qualifications, experience)" | the profile (resume into skills, years, education, university) and the location, seniority and education factors | `src/profile.py`, `src/scoring.py` |
| "best platforms for that country" | a routing table per country; a source is listed only after a request from this machine returned real rows | `src/boards.py`, `src/sources.py` |
| "chances of his getting selected" | a fit band (Strong / Good / Fair / Long shot) with named factors and "what would raise it"; never a probability, because nobody has the hiring data and a percentage would be invented | `src/scoring.py` |
| "job compare option" | a side-by-side table; a follow-up "compare 2 and 4" answered from the last run's memory without a search | `src/corpus.py`, `scoring.follow_up` |
| "help user make tailored mail" | an application note per job and a message per contact: the model writes, code checks, Gmail receives drafts, nothing is sent | `src/writer.py`, `src/voice.py`, the `deliver` slot |
| "find the job form/portal/link" | the direct link in every row, with its kind (ATS, listing, search page) | `sources.apply_kind` |
| "company reputation and other people's experience" | rating and review count from the review site locals read, cited; experiences as linked snippets | `src/reputation.py` |
| "alumni or people to contact" | public search results only: alumni of the user's university, recruiters and hiring managers; the LinkedIn handle and how to send | `src/people.py` |
| "handle multiple error cases / edge cases" | every source failure is a row in `unavailable`, never a crash; a model failure drops the prose, not the run; no resume means unscored, said plainly | `src/agent.py`, `sources.gather` |
| "test the whole thing like a user would" | hosted runs started from the real page with an uploaded file, screenshots, a matrix of profiles | §9 |

Three things belong in this step and nowhere else:

- **Name what you will reinterpret and why**, in the spec, so the user reads the reasoning before the first
  run. The hiring probability became a band. The study-abroad "admit percentage" that every commercial
  counsellor sells was rejected for the same reason: no honest dataset outside the US; "chances" became
  criteria met plus awards per year.
- **List what is out of scope with the reason.** Auto-apply: no browser in the sandbox, and the platform
  policy is drafts before sends.
- **Pin what the statement left unsaid in code, not in a prompt.** "Take the user's country into account"
  became a dropdown of 30 countries plus "Other / global", each mapped to app-store codes, country subreddits,
  currency and locale tokens (the pain-point agent's `countries.py`). A rule that lives only in a prompt is
  a wish; a rule in code with a test is a contract.

Keep a traceability table from the first day and fill it in as you build: one row per clause, where it is
enforced, the test that proves it, and where the user sees it. The pain-point table, all paths inside the
pain-point agent:

| Statement clause | Mechanism | Test | Where the user sees it |
|---|---|---|---|
| Themes with post counts | `analysis.measure` and `theme_stats`: counts from the post list | `test_measure_orders_by_people_and_reports_dropped_themes` | theme table, "Posts" |
| Unique people per theme | `analysis.people`: distinct public handles | `test_theme_needs_three_people_and_a_thread_counts_ten_at_most` | "People" column |
| At least 3 different people | `MIN_PEOPLE = 3`; smaller themes dropped and counted | same | method section, dropped themes |
| At most 10 posts per thread | `cap_threads`, `THREAD_CAP = 10` | same | counts |
| 30-day trend, only with 5 or more recent posts | `analysis.trend`: last 30 days against the monthly average of the earlier window, `MIN_RECENT_FOR_TREND = 5`, growing above 1.25, fading below 0.75 | `test_trend_guard_and_labels` | trend pill, or "too few to tell" |
| Buying intent only when the post says so | `buying_intent`: a regex over fixed phrases ("looking for", "would pay", "switching", ...) | `test_buying_intent_needs_the_words` | buying-intent pill |
| Never invent causes | every quote must be a substring of the post or page the run read (`quote_in`, `verified_quote`), otherwise dropped; a failure without evidence says "no reason found" | `test_quotes_must_be_in_the_post` | quotes with links; the post-mortem lines |
| Competitor weaknesses | `competitor_view`: the themes where posts name the product | `test_product_match_and_competitor_view_reports_zero` | competitor table |
| A competitor with nothing gets an explicit line | `competitor_view` emits a zero row | same | "no complaints found" |
| Why people leave, where they went | classifier fields `left_product`, `went_to`, `reason`; `churn_records`; one model call groups reasons into fixed categories; Capterra's "switched from" and "reasons for switching" fields feed it directly | `test_churn_records_and_country_view`, `test_capterra_reviews_carry_switching_fields` | churn table |
| Non-product reasons kept apart | classifier field `non_product_reason`, counted separately | fake-world graph test | churn table |
| Why products shut down or pivoted | `failures` node: web search, up to 3 pages read, status shut_down / pivoted / still_running / unknown, reasons quoted from page text | `test_full_run_keeps_every_rule` | shut-down products section |
| Opportunities checked against existing products | `opportunities` node: web search per problem, verdict open / partly solved / crowded with the products found | same | verdict pills |
| Own product in its own section | classifier field `about_own_product`; `_own_section` in `corpus.py` | same | "Your product" |
| Every claim linked | every `Post` carries its URL; quotes carry the link; the corpus has a sources table | `test_pullpush_submission_and_comment_become_posts` and the other parser tests | links on every quote |
| Country and location | `countries.profile`; `country_view`; `mentions_country` needs one strong token or two weak ones | `test_country_mentions_need_a_strong_token_or_two_weak_ones` | "In your country" |
| Keyword with two meanings | classifier field `on_market`; a context word from the plan call is appended to one-word names in searches | fake-world graph test | dropped, "the keyword in a different meaning" |
| Non-English posts | `is_english` stopword heuristic | `test_english_heuristic` | dropped count |
| Deleted posts | `[deleted]` and `[removed]` bodies become `None` at parse time | `test_removed_reddit_items_are_none` | dropped count |
| Sarcasm or praise | classifier field `praise_or_sarcasm`: not a complaint | fake-world graph test | counts |
| Fewer than 50 complaints | `THIN_RUN = 50`; `thin_suggestions` proposes broader keywords | `test_thin_suggestions_mention_the_count` | thin-data note |
| A source that fails | per-source status with a reason; the run raises only when every community source failed | `test_collect_names_a_failed_source_and_keeps_the_others`, `test_every_source_down_fails_loudly` | method section, source chips |

## 2. Research what exists, then decide build or wrap

Ask three questions in this order and write the answers into the spec's "Prior art used" section with
dates, so the next builder does not repeat the search. The point is to take mechanisms, not to find
something to wrap.

1. **Who solved it commercially, and what do they actually show?** Simplify, Teal, Jobright, Huntr and
   LinkedIn Premium each do a part of job search (matching, a match score, tracking, cover letters); none
   shows a hiring probability. That settled the band decision: mirror what the best products present, do
   not invent what none of them has. For study abroad there are no counsellor APIs, and the catalogues are
   commission-biased.
2. **What open source is alive, and does it need a browser or a login?** Check the last commit and the run
   requirements, not the star count. AIHawk and its forks were dead or Chrome-bound; `python-jobspy` 1.3.0
   was revived in October 2026, pure HTTP, with ARM64 wheels; Greenhouse, Lever and Ashby publish official
   board JSON. Every study-abroad repo was under 30 stars and prompt-only, so three designs were borrowed
   rather than code: parallel specialists that say "not found", a tiered pool with an evidence map and
   source labels, structured requirement tables with a quality-check node. The pain-point research took
   `zachwelch98/reddit-research` (one evidence quote per score, dissolve clusters under 3 people),
   `AdvancingTitans/pain-miner` (keyless sources, counter-evidence, no opaque composite score), GummySearch's
   theme taxonomy (pain and anger, solution requests, advice requests, money talk), Unwrap's trend rule (a
   recent high at least 25% above the prior peak, which became the 1.25 ratio), Capterra's "switched from /
   reasons for switching" fields as the shape of a churn record, and Keaveney's switching categories for
   grouping churn reasons. Nothing found did churn extraction, post-mortems, unique-person counts and 30-day
   trends together with linked evidence, so the agent was built here.
3. **Which sources can the sandbox reach?** That is §3.

Decide at this stage what cannot live inside an agent. Scrapling's stealth browser and Crawl4AI need
Chromium or Firefox and about a gigabyte of memory, so they cannot be installed from a pip lock in the
sandbox image. If rendered page reads are wanted for every agent, they are a gateway tool on the platform,
not a dependency of one agent.

**Research for quality, not only for data.** Job-scout's first hosted drafts were rejected as machine
writing: skill dumps, "I would welcome the opportunity", "aligns with", nothing specific to the posting,
every note alike. The fix was not a prompt tweak. Two research passes over recruiter and corpus studies
(Juzek and Ward 2025, Kobak et al. 2024, Liang 2024, Pew 2026, Wikipedia's signs of AI writing, Dalton's
six-point email, Lerner's 8,000 recruiting messages, Reed, CV Genius, Viscusi) gave measurable markers, and
those became `job-scout/src/voice.py`: a banned vocabulary, no exclamation marks or dashes, no lists of
three, one concrete number from the resume, a contraction, uneven sentence lengths, and for a message to a
person exactly one question and more words about them than about you. When the user says the output
"feels like AI", find the measured markers and check them in code.

**Answer "will X improve the quality?" with a measurement.** Each aid proposed during the job-scout build
was tried and recorded with what it did and did not change:

| Aid | Result | Kept? |
|---|---|---|
| Webshare datacenter proxies | serve LinkedIn, Naukri, StepStone; still 403/401 from Glassdoor and Indeed reviews; time out on AmbitionBox | no (pain-point kept them for the Reddit archives only, see §7) |
| Scrapling (browser-free Chrome impersonation) | reads Indeed reviews and AmbitionBox from a home address, not through a datacenter proxy | no |
| Crawl4AI | needs Chromium, cannot run in the sandbox | no |
| Firecrawl (search and rendered scrape) | real headlines and ratings in search; renders AmbitionBox for 1 credit; Glassdoor's wall holds (96 s vendor error) so it is marked `render: false` | yes, on the caller's own account |

The study-abroad build met the same question from the other side: a scraping library proposed because it is
popular was tried on the real failure list first, and 12 of 15 failures were stale URLs; the rest needed a
browser the agent image cannot hold.

## 3. Probe the platform and every data source before designing

This is the step most builds skip, and the one that decided most of each design. Do not design against what
a tool is called; design against what it returns.

**The platform.** Half a day of probing settled questions that would otherwise have surfaced as mysterious
empty sections:

- `web.search` (Exa through Composio) returns an answer and cited URLs, no snippets, so discovery means
  "search, then read every candidate page". `web.fetch` returns markdown for several URLs per call but
  serves an index: JavaScript-built sites (Home Affairs, IND, Campus France) come back as a 250-character
  shell with status "success". The study-abroad agent treats anything under 500 characters or with challenge
  wording as unreadable and says so. The pain-point probes found the same tools answering 501 to a `site:`
  query and 403 on a Reddit thread, so that agent reads its sources itself.
- The model is reached only through `GRAVITY_LLM_URL`, and the gateway reserves credit per in-flight
  request: an unbounded request reserves the whole output window against the shared OpenRouter balance and
  fails with 402, as do more than two concurrent calls. Long list extractions hit
  `LengthFinishReasonError` unless the cap is raised for list schemas.
- The sandbox: outbound HTTPS only, no browser, `python:3.12-slim` on arm64 so wheels only (no TeX; Typst's
  wheel typesets the PDF), tools only through the gateway, `timeout_seconds` per run (900 s cap),
  `state.max_kb` for memory between runs. File inputs arrive hosted as signed links.
- A hosted "Try it" run executes as the shared `builder:local` identity, whose tool connections differ from
  the CLI identity's. An optional tool (Firecrawl here) must degrade to one refused call and one line under
  "could not do", not a fan-out of refusals.
- Sibling agents are the style guide: `blog-scout` for `_payload`, search adapters and the "never quiet"
  rule, `slack-ops-review` for `gravity.tools()` and approvals, `job-scout` for the file-input loader shape
  and follow-ups from memory.

**Every data source.** For each one record the exact URL, what a 200 returns (the fields you will keep), the
rate limit you measured, and exactly how it fails. The pain-point spec's "Data access" table is the
template. What those probes found on 14 October 2026:

- Reddit's own JSON answers 403 to every client; `old.reddit.com` redirects to login; `search.rss` works at
  about one request per 20 seconds.
- PullPush returns 100 full items per call and answers 429 after about 6 calls in 20 seconds, so it is paced
  at one call per 3.5 seconds with two retries.
- Hacker News Algolia, the per-country App Store review feed, Google Play through `google-play-scraper` and
  unauthenticated GitHub issue search (10 a minute) all work keyless.
- Capterra and Product Hunt review pages answer 403 to plain clients and 200 to `curl_cffi` with a browser's
  TLS fingerprint. G2 and Trustpilot refuse every client, with or without proxies.

**Then probe again from where the agent will run.** The sandbox is a datacenter address on AWS. The hosted
pain-point run got 403 from PullPush, Capterra and Product Hunt, all of which answered 200 from a home
address; Reddit fell back to RSS and collected about 140 posts instead of 1,000 or more. That single finding
produced the `proxy_url` secret input (1.0.3) and the Firecrawl fallback (1.0.4). The reverse happens too:
LinkedIn guest pages throttled from home and ran clean from AWS, while Glassdoor and Indeed reviews answer
403 to datacenter clients whatever the client. A source that works from your laptop is not verified, and a
job-scout board is listed for a country only after a request from the sandbox returned real rows.

**Save a trimmed real answer from each source the same day under `tests/fixtures/`**, named with the date it
was taken (`internshala_list.html`, `reed_list.html`, `seek_search.json`, `jobbank.xml`, ...). Every parser
test runs on those with no network, so a source that changes its shape fails a test instead of a run.

## 4. Decompose into modules, each with a source of truth

Write the brief's promises as a table before writing code. Each row must answer "where does the number come
from", "what does code compute" and "what is the model for". A row that cannot answer the first question is
not a module yet. The study-abroad table, eleven modules:

| Promise in the brief | Fact source | Code computes | The model does |
|---|---|---|---|
| Find universities in budget, am I eligible | the programme's own page, a second fees or admissions page when the first lacks the fee or deadline | requirement-by-requirement check (ETS TOEFL/IELTS table, GRE, work years, grades on the same scale), cost with ECB rates, fit score, tier, order | one structured extraction per page |
| Scholarships and my chances | DAAD, Chevening, Fulbright, Australia Awards, the shortlisted universities' pages | criterion-by-criterion match; "chances" = criteria met plus awards per year, never a percentage | extraction per page |
| What it costs | programme page, the country's official living figure, visa fee, insurance | first year and whole degree in the student's currency; money to show, separately | nothing |
| Where to live | the universities' accommodation pages, the operator's rent page | rent per month from weekly or per-semester figures | extraction per page |
| Timeline I can tick off | intake, deadlines read from pages, typical windows per country | backward-planned dated steps, statuses, ticks kept in memory | nothing |
| Documents | country configuration plus the programme page | the list | extraction |
| Visa, money, post-study work | official government pages, or pages quoting them when the official site is a shell (labelled) | nothing | extraction per country |
| Job market | cited search results | nothing | prose with citations only |
| Alumni to talk to | public search-result titles | namesake filter (the result must name the university, its city or its country) | nothing |
| Cover letter | the student's profile only | placeholders where the profile is silent; numbers not in the profile scrubbed | draft or critique |
| Education loans with yearly repayment | the lenders' own pages, their separate rates pages, a quoting page only when the lender prints nothing | EMI formula, lender and product merging, rate context rules | extraction per page |

Two patterns fall out of the table and are worth copying into any agent of this shape:

- **A "second read" per module.** The first page rarely prints everything. Programmes get `fill_gaps`
  (fee, deadline, English minimum, GRE rule), scholarships `fill_amounts`, housing `fill_rents`, loans
  `fill_rates`. Each is one more search and one more page per row, grounded like the first.
- **A fixed, dated estimate table** (`study-abroad-advisor/src/fallbacks.py`) for the figures a page may not
  print, each with its basis and a date, shown with "≈" and weighted lower in any score. The model never
  produces an estimate.

## 5. Decide what code does and what the model does

Write two lists before writing a node. For the pain-point agent:

**Code computes**: collection, cleaning, deduplication, every count, unique people, the thread cap, the
trend, buying intent, quote verification, the country split, the report. The constants sit at the top of
`src/analysis.py` where a reviewer can read the rules in ten lines.

**The model decides**: whether a post is a complaint and about this market, a one-line pain, severity, which
product, whether it is sarcasm, the churn fields; the names of up to 14 themes from a sample; which theme
each pain belongs to; the grouping of churn reasons into fixed categories; what a post-mortem page says;
which themes are opportunities; whether web results show a problem already solved.

The same split in the other two: job-scout's weights live in `scoring.WEIGHTS` (skills 40, experience 20,
location 15, seniority 10, education 5, recency 5, competition 5) and the same inputs give the same score;
the model reads the resume into a profile and a posting into its requirements with structured output, and
code scans skills from a curated list and grounds every name and URL the model returns. Study-abroad's
eligibility, FX, score, tier, timeline, EMI, matching and de-duplication are Python with tests, and the
model makes one structured-output call per page plus the prose at the end.

Every model call follows one shape (`ask` in `pain-point-discovery/src/agent.py`): a pydantic schema for
the answer, a short system prompt, a bounded payload (post text clipped to 900 characters, pages to 6,000),
batches of 25 or 40, at most 2 calls in flight, two retries, and a fallback when the call fails (the plan
call falls back to the fixed query terms without a context word). The model is never asked for a number
that code can compute.

Then lay the work out as nodes with one job each. The graph reads top to bottom; each node's inputs and
outputs are state keys; nothing clever.

```
pain-point:    plan -> collect -> clean -> classify -> themes -> measure -> churn -> failures -> opportunities -> report
job-scout:     prepare -> search -> analyse -> enrich -> write -> deliver

study-abroad:  inputs -> intake -> research -> assess -> extras -> people -> plan -> write -> deliver
                           |          |          |                   |        |
               profile   pages read   eligibility scholarships   timeline  prose last:
               (one      + one        affordability housing      + docs    verdicts,
               model     extraction   fit score   (time-boxed)   (code)    statement
               call +    call per     tier, order                          (model)
               code      page, then   (all code)
               parsing)  code grounding
                                                follow-up message -> answer (from memory, no search)
```

Model-free nodes (`collect`, `clean`, `measure`, `report`) are where the rules live. Keeping them model-free
is what makes them testable without a network or a key.

## 6. Write the spec first, reconcile it at the end

Location: `docs/<date>-<agent>-agent.md`. Write the first sections before code and the
results as they come in; the spec is where the next iteration starts. The sections that earned their place,
in order:

- **Problem** (two paragraphs: the user's tabs today; what exists and why it does not fit).
- **Outcome** (the numbered list from §1, in the user's words where possible).
- **Scope** (in, out with the reason for each, and what was added during the build).
- **Prior art used** (§2) and the **data access table** (§3).
- **Assumptions**, each verified, with how (the `curl_cffi` aarch64 wheel checked on PyPI; a `file` input
  arriving hosted as a signed link; the model path every reference agent uses).
- **Inputs** and the **pipeline table** (node, what it does, model or not).
- **Acceptance criteria**, a table `# | criterion | how it is checked` with one row per outcome plus one per
  failure mode. Each "how" is a unit test, a `gravity run` or a hosted run; "we'll see" is not a how.
  Study-abroad's A2 "every number shown occurs in the fetched page text; a planted hallucination is dropped"
  is a unit test; A1 "at least four programmes per country with university, page URL and the fee or deadline
  when the page states them" is a live run; A9 "any single source failing is listed and the rest is
  delivered" is an injected-failure test. Job-scout's A10 is model failure and A11 is validate, build and
  pytest with no network.
- **Rules enforced in code, edge cases, country handling** (the traceability table from §1).
- **Architecture and data flow**: the node pipeline as a diagram, a module table `file | role | model?`, the
  state keys, the routing and scoring tables, the failure boundaries, security and privacy (where the resume
  text goes, what is never scraped, drafts only).
- **File impact** table, so a reviewer sees the blast radius, and a "proposed, not built" section for any
  platform-side change the agent needed (study-abroad: a rendering fetch), so the decision is visible
  instead of silently worked around.
- **Alternatives considered**, with the reason each lost. Study-abroad: commercial counsellor APIs (none
  exist), per-country databases (keys the agent cannot hold, monthly ZIPs, no UK masters), an admit-chance
  model (no honest dataset outside the US), the `ddgs` search a sibling uses (throttled, no page text).
- **Verification plan** (the commands), then **verification results**: a dated section per version with
  run ids, times, calls, cost, counts, what the user saw, the cause, the rule and the proof. A result table
  is worth more than prose. It is the audit trail the review loop (§10) runs on.

The spec is a living log, amended in place every time the brief grows. Study-abroad's acceptance items 11
to 15 are dated additions; job-scout's spec has sixteen dated sections, one per version. This file is a
summary of those records.

## 7. The design rules that keep the output honest

Each rule is general and held up across all three builds. The indented lines are instances.

1. **Code does the facts, the model does the prose.** Counting, ranking, money, dates, dedupe, scores,
   comparison, time and order: Python with tests. The model reads unstructured text into structured fields
   and writes sentences around numbers code computed.
   > Weights, bands and ties by name in `job-scout/src/scoring.py`; eligibility, FX, fit, EMI in
   > study-abroad's `assess.py` and `loans.py`; every count, the trend and buying intent in
   > pain-point's `analysis.py`.
2. **Grounding is a gate, not a prompt instruction.** A number, date, URL or quote the model returns survives
   only if code finds it in the source it claims.
   > `study-abroad-advisor/src/grounding.py` turns the page into a set of number tokens (both thousands
   > conventions, decimals with either separator, lakh and crore forms) and nulls any extracted field whose
   > digits are not there; dates the same way; citations must be in the result set. "A missing number is
   > recoverable and a wrong one is not." Pain-point's `quote_in` and `verified_quote` drop any quote that
   > is not a substring of the post or page the run read, and count the drop.
3. **Never invent, and label every figure.** Three tiers, always: read from the page (plain figure);
   resolved by the agent (a second page, a named conversion method, a quoting page when the official one is
   a shell); estimated from the dated table (≈, basis shown, lower weight). The report never says "unknown"
   where a tier applies, and never tells the user to "confirm" or "check" something the agent could have
   read. A figure no tier reaches is a plain phrase, not a guess or a chip that pretends.
   > Pay is shown only when the posting states it ("pay not stated" otherwise); a rating line is left out
   > when there is none; no resume gives band `unknown` and a sentence saying why; a failure without
   > evidence says "no reason found".
4. **A link the agent constructs is shown only after it answered.** Links the user completes themselves (a
   board's search page, the LinkedIn alumni search) may stay.
   > Job-scout 1.0.14: the Levels.fyi chip led to a 404 for any company it does not list; now `page_exists`
   > checks the guessed URL and keeps it on a 2xx only. The rule: never show a link that lands on a 404.
5. **One file per concern, one pipeline.**
   > Job-scout: `boards.py` (which sources), `sources.py` (the fetchers), `profile.py`, `scoring.py`,
   > `reputation.py`, `people.py`, `writer.py` (every model call), `voice.py`, `resume_check.py`,
   > `resume_pdf.py`, `corpus.py`, `titles.py`; `agent.py` wires them.
6. **Failure boundaries at every edge; degrade, never pretend.** Every tool call under a timeout, page reads
   in batches with bounded concurrency, a time share per module that keeps the rows it has and says why it
   stopped, nothing raising past a node. Every source reports ok / partial / failed / skipped with counts and
   the reason; a failed source is one `{source, reason}` row under `unavailable`, de-duplicated at delivery;
   the run raises only when every source failed. A tool refusal (`NEEDS_RECONNECT`, `APPROVAL_REJECTED`)
   arrives as text and is a failure to record, never a success to pass on (`_payload`).
   > Job-scout: jobspy in a thread with 45 s, HTTP fetch 20 s, five at a time; all sources failing still
   > returns the direct search links; the first live run had every model call failing (402) and delivered
   > 125 scored internships with a note. Pain-point: collection stops at 300 of the run's 900 seconds and the
   > report says which sources were cut short; a 404 is never retried through a paid fallback; a 429 slows
   > the pacer for the rest of the run; under 50 complaints the report carries a thin-data note with broader
   > keywords. Study-abroad: each module keeps its partial rows when its time share runs out.
7. **Fallback chains, each step cheaper than the next, moving on only when the previous step returned nothing
   usable.** The caller says what usable means.
   > Pain-point: PullPush, then Reddit RSS (3 queries at most); DuckDuckGo, then `firecrawl.search`; a plain
   > httpx read, then `curl_cffi` with a browser fingerprint, then a `firecrawl.scrape` render; the country's
   > app store, then the US store, labelled as such. Job-scout's `make_search`: DuckDuckGo, then the
   > gateway's `web.search`, then `firecrawl.search` tailored to the country, each only when granted, with an
   > `accept` predicate (a profile with a headline, a page carrying the rating) deciding whether to keep
   > looking.
8. **Tools only through the gateway; paid tools on the user's own account, capped, degrading without the
   connection.** Gravity does not pay for tool accounts; the consumer connects their own
   (`gravity connect firecrawl`). Each call is counted in the report; without a connection the run behaves
   exactly as before.
   > Job-scout: at most twelve Firecrawl searches and two scrapes per company per run. Pain-point: Firecrawl
   > is declared in `permissions.tools` but used only after the free path failed. One measured lesson: do not
   > pass a `location` to a render; routing through India made a Capterra page take 36 s instead of 8 s and
   > timed out in 1.0.4; 1.0.5 removed it. Study-abroad: the first render goes alone and a refusal is
   > recorded once, after 1.0.12 printed the Firecrawl refusal eleven times.
9. **A secret input for something the platform does not provide yet.**
   > The Reddit archives refuse cloud addresses, so `proxy_url` is a `secret` input
   > (`http://user:pass@host:port`), with the platform's `HTTPS_PROXY` as the fallback. It is used only for
   > the calls that need it, validated by shape, masked in the stored inputs, and never written to the
   > result. Webshare's proxies were measured first: they fix PullPush and RSS from the sandbox, not the
   > review sites, so the review sites stay best-effort and say so.
10. **Bound the model.** `max_tokens` on every call, a semaphore on parallel calls (two in flight), only the
    fields it needs in the prompt, structured output, a retry policy that does not stall the run, and the
    page text focused rather than truncated.
    > Job-scout: `MODEL_MAX_TOKENS = 2500`; requirements for the first 24 postings by title match, the rest
    > scored on the title; a profile is one call. Study-abroad: the model receives the opening of the page
    > plus the passages around figures, the product's own passages first, menus split into small pieces
    > (`research.focus_text`), not the first N characters (§11 says why).
11. **Check the model's prose in code, retry once, report what still fails.** Quality rules are code, not
    hope.
    > `voice.py` checks every job-scout note and message; a failing draft goes back to the model once with
    > the exact failures; what still fails is delivered with its flags in `drafts_flagged`. The resume
    > rewrite keeps only bullets whose numbers exist in the original and is scored again by the same ATS
    > code. Study-abroad's cover letter draws on the profile only, with placeholders where it is silent and
    > numbers not in the profile scrubbed.
12. **Untrusted page text.** Pages reach the model as data under a system prompt that says so; code grounds
    every number, URL and citation that comes back. No write tools, no credentials, nothing read from a
    logged-in account; people are public search-result titles only.
13. **Delivery is a slot with adapters, not a tool.** Drafts before sends; the default keeps everything on the
    page.
    > `slots.deliver`: `gravity` (nothing leaves) or `gmail: [gmail.draft]`. Gmail therefore appears under
    > "Deliver the notes to" and not under "Tools it can call", which confused the user once; the spec
    > explains it.
14. **Memory for follow-ups is small and written after success.** A follow-up answers from it without a
    search; only a change of the core inputs starts a fresh run.
    > Job-scout: `state.max_kb: 256`; fifteen shortlist rows (id, title, company, url, score, band,
    > factors); "compare 1 and 2" answered in 59 s with no search. Study-abroad: the compact shortlist,
    > briefs, scholarship and housing rows, plans, ticks and the FX table; "compare 1 and 3", "cheaper",
    > "done: IELTS" and "loans" answer in seconds; only a country change starts a fresh run.
15. **Carry the user's context in code.** "Tailored to the user" means a profile in code, not an adjective
    in a prompt.
    > Pain-point: `countries.py` maps each country to its App Store and Play codes, its subreddits (r/india,
    > r/IndiaStartups, r/unitedkingdom, r/de, ...), its currency and locale tokens (₹, INR, GST, UPI; £,
    > HMRC; ...) and the city the user typed; the report's "In your country" section counts complaints from
    > the country's stores and communities, and says so when the pick is "Other / global". The market's
    > meaning: run 2 (smart thermostats) classified 343 of 450 posts as off-market because "Nest" alone
    > matches birds; the plan call now returns a context word ("thermostat") appended to every one-word
    > keyword in community searches, and the classifier's `on_market` field drops what slips through,
    > counted as "the keyword in a different meaning". Job-scout: a routing table of boards per country and
    > the review site locals read. Study-abroad: costs in the student's currency with ECB rates, documents
    > per country, visa pages per country.
16. **Every input type the user might need, with labels that read as a question plus a hint.** A file
    arrives as a signed link; the loader accepts a link, a path or text.
    > `resume_file` (pdf, docx, txt) or `resume_text`; `experience_years` overrides the resume;
    > `target_companies` adds their ATS boards; `count` is clamped 3 to 20; a missing `role` is a clear
    > error.
17. **Fix the mechanism, never the case.** A complaint about IBM is fixed for every short name; a complaint
    about ITOL Recruit is fixed for every company whose staff name a parent brand; a complaint about SBI's
    rate is fixed for every lender whose product page keeps the rate elsewhere. Per-case patches are
    forbidden, and each rule is tested with more than one site.

## 8. Build in this order, with the commands

1. **Scaffold with `gravity init`** (the template closest to the job) and follow the patterns of the worked examples
   here. `manifest.yaml` first (inputs, permissions, slots, outputs, state, resources), then `requirements.txt`,
   then the module files with their docstrings saying what they decide.
2. **Validate and lock early.** `gravity validate` and `gravity build` prove the manifest and compile the
   aarch64 lock; a dependency without an ARM64 wheel surfaces here, not in the hosted build.
3. **Pure logic and its tests** (`src/analysis.py`, `src/scoring.py`, `src/grounding.py` and their test
   files). Every rule from §1 as a small function with its constant, and one test per rule.
4. **Parsers over recorded fixtures** (`src/sources.py`, `tests/test_sources.py`), plus the three helpers
   every source shares: a `Pacer` that slows itself down after a 429, a `Deadline` that stops collection at
   its share of the run, and a per-source status entry (ok / partial / failed / skipped, with counts and the
   reason).
5. **The graph against a fake world** (`tests/test_agent.py`). Fake tools return Composio-shaped payloads
   built from real page excerpts with planted problems: a hallucinated number, a consultancy page that passes
   a substring "official" check, a scholarship with an award count the page never printed. A `FakeModel`
   answers every schema deterministically. One test runs the whole graph and asserts every rule at once
   (`test_full_run_keeps_every_rule`), beside the loud failures by name: every source down, a missing
   required input, the global country pick with no competitors, a blocked search, model failures, a failed
   FX lookup, bad inputs, a critiqued draft, every follow-up
   (`test_model_failure_still_delivers_the_scored_list`,
   `test_search_failure_leaves_reputation_and_people_empty_but_the_run_whole`,
   `test_no_jobs_at_all_gives_the_direct_links`, `test_gmail_delivery_drafts_and_a_refusal_keeps_the_report`,
   `test_manifest_declares_what_the_code_uses`).
6. **The report through every renderer** (`src/corpus.py`). One `report` dict becomes the corpus the
   platform renders as markdown, Word, PowerPoint and CSV. A stand-in run with a heuristic model pushed the
   pain-point corpus through every renderer before any real model call was paid for; it exposed GitHub
   keyword noise and issue-template quotes, both fixed before the first hosted run.
7. **Prompts last.** They are short, name the fixed output schema, and forbid inventing identifiers ("never
   invent a theme id").
8. **Keep a real hosted run as a fixture**, so the result-shape tests (study-abroad's `test_layout.py`:
   every field the layout names exists on its records, every block has a tab) run against what the agent
   really emits.
9. **Every review finding becomes a test before the version bump.** The commit messages from 1.0.6 on read
   as a changelog of findings; each has a test (`test_loans.py`, `test_research.py`, `test_second_reads.py`,
   `test_suite.py`; `test_shortlist_is_different_jobs_not_one_recruiters_repeats`).
10. **Run pytest as its own step.** Study-abroad 1.0.12 shipped with two failing tests because a push chain
    ignored the exit code. The chain now runs `pytest` separately, with `set -o pipefail`, before
    `gravity validate`, `gravity build` and `gravity push`.

Run the tests in your own virtual environment (`uv venv`, `uv pip install -r requirements.txt pytest`, then
`pytest tests -q`). The `gravity` package cannot be installed outside Gravity, so import it behind a guard
(`try: import gravity` / `except ImportError: gravity = None`) and fake `gravity.memory`, `gravity.ask` and
`gravity.tools` in tests; the real ones exist only on a hosted run. Count the tests after every version (the worked
examples have between 40 and about 200).

**Local real runs through the hosted gateway and model**, one per acceptance row that needs the network,
with the sample inputs kept under `samples/` (job-scout: a student resume, an analyst, a weak one, as txt,
docx and pdf). You need to be signed in (`gravity login`):

```bash
gravity run --input looking_for=internships --input role="software developer" --input country=India --input city=Bengaluru --input resume_text=@samples/resume_student.txt --input count=8
gravity run --input message="compare 1 and 2"
```

Record time, rows per source, model calls and cost in the spec's evidence table (job-scout's first hosted
run: 181 s, 30 model calls, $0.0087; pain-point's: 447 s, 20 calls, $0.026 model and $0.013 compute).

**Push.** Versions are immutable; every fix is a bump. From the agent folder:

```bash
gravity validate && gravity build && gravity push
```

A new version is private until the Gravity team approves it; you can run your own unapproved version from the web
app. A push can fail when Gravity's capacity is full: try again later or tell the team. `gravity agents` shows
`legacy` for retired versions.

**Write the README** (modules with their fact sources, the labelled tiers, inputs table, run commands, what a
run does, limits stated honestly, the test command).

## 9. Test as the user would, on every surface

Unit tests prove the rules. Only runs show whether the agent is useful, and only runs found the defects no
unit test could (402s, stale URLs, quota, sandbox 403s).

**Where to run as the user.** Push, then use the agent the way its audience will, from the consumer page (`/app`) or
the dashboard chat; you can run your own unapproved version. `gravity dev` serves the same form, timeline, approvals
and result locally. Answer every question, run the agent, open every tab of the result, look at it at a phone width,
upload a real file through the real question box, and open the run again from the history. If you have a
browser-automation tool, drive the page with it and keep the walk-through script next to the agent: a session's
scratch folder vanishes.

**Keep a run log in the spec** with time, model calls, cost, collected and classified counts, and one line
on what the run showed. Every change in a version log comes from a run, not from reading code. The
pain-point log:

| Run | What it showed | What changed |
|---|---|---|
| 1, local, note-taking apps, India | 125 of 200 classified posts off-market from unquoted keywords | quoted phrases, then the context word |
| 2, local, thermostats, UK, own product and a shut-down product | explicit zero lines for two competitors; the shut-down product reported "unknown" with the note that the pages found do not name it | kept: this is the honest answer |
| 3, local | a shared PullPush pacer for country subreddits starved the main Reddit search (6 of 22 queries) | sequential, smaller country search |
| 4, local | PullPush answered 429 while probe scripts ran from the same machine | the pacer slows itself after a 429 |
| 5, local, with Capterra and Product Hunt | 89 complaints, leavers for all three competitors from Capterra's switching fields; the run came within 106 s of the 900 s timeout | collection budget 300 s, depths 200 / 350 / 500 |
| hosted 1.0.2, API | 53 complaints, Pocket found as shut down; PullPush, Capterra and Product Hunt 403 from the sandbox | `proxy_url` input (1.0.3) |
| hosted 1.0.3, proxy | 835 Reddit posts, 81 complaints, 9 themes; the proxy adds latency (12 of 19 searches before the deadline) | kept; review sites still 403 |
| hosted 1.0.4, Firecrawl | Capterra and Product Hunt read through the consumer's account; two renders timed out when routed through India | no country routing (1.0.5) |
| hosted 1.0.5 | 59 complaints, 7 themes, 6 renders and 2 searches, 0 failed, about $0.04 | shipped |
| consumer chat on dev, 1.0.5 | 96 complaints from 90 people, 9 themes, 10 min 27 s; the chat's questions did not render the inputs as the form does | fixed on the platform side (the chat's question rendering) |

**The matrix.** Run the same inputs on every version so a fix can be seen against the previous run and a
regression shows up the next morning (study-abroad 1.0.9's merged loan products did). Job-scout's matrix:
four profiles started together, then a targeted case, then synthetic edge cases rendered through the page by
stubbing the run response:

| Case | Why it is in the matrix |
|---|---|
| student, India, internships, software developer, PDF resume | the main path: Internshala, Unstop, AmbitionBox, alumni |
| analyst, USA, New York, data analyst jobs | ATS boards, Glassdoor and Indeed ratings, pay stated on every row |
| weak resume, UK, London, software engineer | the ATS rewrite path (20 to 46), Reed, recruitment agencies with no reviews |
| no resume, Germany, Berlin, marketing internships | unscored rows, Kununu and Arbeitnow, the "unknown" band wording |
| target companies IBM and Infosys | short names, a company with 108,158 reviews, five alumni, Firecrawl spend |
| no jobs at all / 20 rows / a compare follow-up / a company with nothing / jobs without a resume / hostile text | the page must draw every shape with zero console errors |

**Walk every surface a user can reach, as that user, with the same inputs.** Each surface found a different
defect:

| Surface | How it was driven | What it found |
|---|---|---|
| `gravity run` locally against the real gateway | the CLI | the keyword and pacing defects above |
| `gravity dev` | the local dashboard | form defaults and question wording |
| a hosted run, from the consumer page, as the builder | the page's own form | the sandbox's 403s: sources that answer a laptop refuse a datacentre address |
| a hosted run as a user with no connected accounts | the same page | the connect gate asked for a tool before the first question although the tool was optional |
| every result tab, at desktop and phone width | a browser-automation walk | wrapped chips and a clipped programme name, before a reviewer saw them |
| run history, and the run opened again | the history page, `gravity runs`, `gravity logs` | the same run must read the same everywhere |

**Evidence recipe.** Run ids and timings from the page and `gravity runs <agent>`; the step timeline from
`gravity logs <run id>`; a paid tool's spend from its own usage page before and after; screenshots of the result as
the page shows it; the test count after each version.

**Platform limits you will meet**, so check them before promising a hosted run: the run's budget (`402
BUDGET_EXCEEDED`: keep model calls few and small), Gravity's capacity at push time (try again later), and the CLI
session, which expires within the hour (`gravity whoami` refreshes it).

## 10. A complaint becomes a rule: trace every wrong cell to its mechanism

The reviewer tests the way a student or a job seeker would and reports per-cell problems. None of them is
patched in the presentation. Each is traced to the page that was read, the extraction that ran, or the rule
that dropped the value, and the mechanism is fixed for every site, not the one named. Three habits make the
loop work:

- **Reproduce the complaint from the run's own data before changing code.** The IBM search results were in
  the gateway log; the loan pages were re-read by hand through the gateway. Ask "could any page have printed
  this?" before accepting a blank: the reviewer's "make sure really no info could be fetched" is the right
  standard, and if the figure is there the agent must find it.
- **Write the test for the rule, not the case.**
- **Re-run the whole matrix after each version**, since a rule for London can break Bengaluru, and a rule for
  SBI can hide ICICI.

The study-abroad record:

| Finding (reviewer's words) | What had actually happened | Fix (version) |
|---|---|---|
| "why does it not have rates?" | SBI's and IOB's product pages say "click here for rate of interest"; Bank of Baroda's table is script-filled; only ICICI prints a rate on the product page | `loans.fill_rates`: read the lender's own rates page first, accept a comparison site only when the lender prints nothing, labelled "quoted by host" (1.0.6) |
| "doesn't Germany have free education?" | every German programme without a printed fee got the midpoint of EUR 0 to 3,000 | a state rule: EUR 1,500 a semester at Baden-Württemberg public universities, elsewhere only the semester contribution; no estimate for a private university or an MBA; basis shown (1.0.6) |
| "why does it find private unis?" | every university in the run was public; the page had not said so | record public or private only when the page states it (1.0.6) |
| maximum "Rs 1.5 crore" missing | digit-only grounding did not know lakh and crore | grounding understands both forms (1.0.7) |
| a 6.85% rate nobody prints | Bank of Baroda's EMI-calculator default was read as the rate | a rate counts only when printed with %, per cent or p.a. (1.0.8) |
| affordability "unknown" for UNSW | "$61,000" came through with currency "$" | currency symbols resolve by the page's country; later "A$", "$A", "Australian dollars", "Australian Dollar (AUD)" (1.0.8, 1.0.13, 1.0.14) |
| SBI's second product vanished | rows merged per lender swallowed a different scheme | merge per lender and product family (1.0.9) |
| "KIT people are from the Indian KIT" | namesake institutions share abbreviations | an alumni result is kept only when it names the university, its city or its country (1.0.10) |
| "Level: page says MSc; you want a Masters" | level matched by string | level synonyms (MSc, Master's, postgraduate, graduate) (1.0.10) |
| one university twice | two pages, two names | de-duplicate across page names (1.0.10) |
| loans "0 tried" | the module's time box after a long search phase had skipped it | the chase runs inside its own deadline and keeps partial rows; later, lenders read during the research phase (1.0.10, 1.0.11, 1.0.18) |
| SBI showing 7.05% | a home-loan rate in the page's footer widgets | a rate must sit in education-loan context: its own sentence or table row, or a page dedicated to education-loan rates (1.0.12 to 1.0.14) |
| "make sure really no info could be fetched" (IDFC, Union Bank, Studentenwerk rents, scholarship values) | checked by hand through the gateway: IDFC's rates page prints "from 9.5% p.a."; the Studentenwerk pages print rents per room type; UQ's page says "25% reduction" in words | chase rents to the operator's page, scholarship values by link or by name, a plainer second lender search; a row says which hosts printed no rate; values in words shown as what they cover (1.0.15, 1.0.16) |
| many "not on the page" cells | root cause: page text handed to the model was cut at 7,000 characters; IDFC's rate sits at character 7,600 after the menu | detail pages read to 30,000 characters and focused on figure-bearing passages; plain text preferred over a render when both exist (1.0.17) |
| the Firecrawl refusal printed eleven times | fan-out of renders on an unconnected account | the first render goes alone; a refusal is recorded once (1.0.12, 1.0.19) |

The job-scout record:

| What the user saw | Root cause | The general rule (version) |
|---|---|---|
| Scalora Academy shown with Scaler Academy's rating | a search engine titled a namesake's page with the name asked for | a review page counts only when its URL slug and its text name the company (1.0.8) |
| IBM with no ratings and no people, although search returned both | the whole-name matcher needed four joined letters | names under four letters match as a whole word; the search chain keeps looking until the hits are usable, per the caller's `accept` (1.0.9, 1.0.10) |
| 34 Firecrawl credits spent on one run | people searches fanned out on the paid backend | twelve Firecrawl searches per run, then the free backend; count-only rating chips instead of hidden sites (1.0.11) |
| the downloaded resume had uneven spacing and misaligned headings | fpdf2's hand-placed layout | a Typst template with the content passed as JSON and its own fonts embedded (1.0.12) |
| three jobs shortlisted, people for one company | the top three were one agency's copies of one role | `diversify`: one posting per company and title first, a second per company only to fill (1.0.13) |
| a professor listed as a recruiter | the company's own words matched recruiter words | classification ignores the company's name words; a title glued to the next result is cut at "LinkedIn" (1.0.13) |
| "Pay on Levels.fyi" opened a 404 | the link was built from the name | a constructed link is kept only after it answered 2xx (1.0.14) |
| ITOL Recruit "has nobody to reach" when its recruiters were in the results | headlines named the parent brand, so the company check dropped them, while certificate holders passed | a hit records whether the engine honoured the quoted phrase; hiring-side people from an exact search count without the name; a company named only beside credential words is a certificate holder (1.0.15) |
| a headline running into the next result | the search engine's title had no separator | `titles.search_title` cuts at the engine's ellipsis and after a review site's name (1.0.16) |
| drafts read as machine writing | the prompt asked for a cover letter | the measured markers checked in code with one retry and flags (`voice.py`) |
| a run died at start-up with a task-group error | the gateway's MCP session was cut while listing tools | the SDK lists tools up to three times on a transient error (a platform fix) |

**A version bump needs a run that shows the change**, recorded in the spec with its numbers; the manifest's
version comment says why in one line. The pain-point version log:

| Version | Change | Evidence |
|---|---|---|
| 1.0.0 to 1.0.2 | the agent and its spec; hosted for the first time | 33 tests; hosted run 447 s, 20 calls, $0.026 model + $0.013 compute |
| 1.0.3 | `proxy_url` secret for the Reddit archives | 835 Reddit posts hosted against about 140 by RSS |
| 1.0.4 | Firecrawl as the fallback for refused pages and a throttled search | Capterra Notion and all Product Hunt pages read hosted; two renders timed out |
| 1.0.5 | renders no longer routed by country | 6 renders, 2 searches, 0 failed, 453 s |

## 11. Build a probe for the slow module

A full run takes five to eight minutes and shows only the output. When a module keeps printing blanks, build
a probe: a tiny agent (its own `manifest.yaml` and `gravity run`) that imports the real module, calls it on
seed rows against the real gateway and model, and logs what the model received and returned per page. The
study-abroad loans probe wraps `loans.fill_rates` on four lender rows and records each search's citations,
each page's length and head, and the extraction. It found the 7,000-character cap in minutes, something no
hosted run would have shown, and after the fix it printed IDFC 9.5% from its own page, SBI 8.9 to 9.4% from
its rates page and Union Bank's quote with the quoting host named.

Use a probe whenever a finding is about one module's inputs rather than the graph.

## 12. Shape the result for a reader; the platform draws it

The first study-abroad result read like a document, and the reviewer said so ("it says scholarships found
but I can't see them, it is just a table", "it should feel like a refined product rather than a doc
file"). The answer was not view code in the agent. An agent ships none; it ships a result the renderer can
read, the way `Gravity.agent.md` section 9 describes (the agent's `_layout` read as hints, then a planner, then
deterministic rules), and the platform composes the screen in its own design language. What the agent owes the
renderer:

- **Keys named for a reader, numbers as numbers.** `programmes`, `shortlist`, `companies`, `comparison`,
  `next_actions`, `why`, `deadline`; bookkeeping (`pages_read`, counts, caps, statuses) named so it folds
  away and never a consumer field. A display copy of a number ("≈ 1,272,109") cannot chart, so the raw value
  sits beside it; never a display copy of a list beside the raw one.
- **The one-sentence answer in `headline` or `verdict`; the written summary in `summary`.**
- **Records with `title` or `name`, `url`, short state words (`tier`, `band`, `status`), long text under
  `why` or `summary`; nested lists as records** (`people: [{name, headline, why, url}]`).
- **States as fixed enums with plain-word maps.** Trend, verdict, failure status and source state are short
  fixed values in the record; `corpus.py` maps each to the words a person reads ("Partly solved", "too few
  to tell", "shut down"). A reader never sees a raw label.
- **A sentence for every empty case.** No competitor named, nobody left, no shut-down product found, no
  theme strong enough, a global country pick, no resume: each section carries its own one-line explanation
  instead of vanishing, so a thin or failed run still reads as a finished answer.
- **Bounded lists, counts beside quotes.** At most 14 themes, 10 expanded, 4 quotes per theme, 5
  opportunities, 5 shut-down products; every count sits next to the quotes that back it, and every quote
  carries its link.
- **The method as data.** Sources with state and reason, drops by reason, and the window are fields of the
  record, so the limits of a run are presented like its findings.
- **One record, two readers.** The screen and the downloads (markdown, Word, PowerPoint, CSV through
  `corpus.py`) read the same `report` dict. There is never a second source of
  numbers. A file as bytes in the result (`pdf_b64`) only while the platform has no file output; the Word
  download carries the same content.
- **A layout hint, not a screen.** Study-abroad's `src/layout.py` emits `result._layout`: which fields
  matter, their captions, and a short tab name per block (Overview, Programmes, Scholarships, Money,
  Housing, Visa and country, Timeline, People). Captions through `_captions`, structure through a
  `_layout` hint read as hints (name every list you want shown: a list the hint omits is hidden). The platform decides tiles, rows, tables, charts and tabs, and
  adds its own controls. A presentation defect fixed in the platform (a clipped card body) is fixed for every
  agent at once.
- **Verify on the real page** (§9), and check the result everywhere the page shows it: the run in chat,
  the run history.
- **Trace design feedback like a data finding.** "Doc file" meant the facts had no kinds (everything was
  prose and one table), so the layout names a kind per block; "cut off" was the platform's clip, not the
  agent's output.
`Gravity.agent.md` section 9 lists the components the renderer has, what makes the rules pick each one, the
`_layout` hint fields, and the reserved `_offer`, `_stages` and `_focus` keys that steer "What next".

Gravity's house style applies to anything an agent emits that a page shows as text: no filler, no AI
vocabulary, a person row says the platform and the handle and how to send, a document download is typeset
(LaTeX quality; Typst in the sandbox), nothing links to a 404.

## 13. Ship, and leave the record straight

1. **Check what you ship.** Read the diff: only the agent's files, no debug output, no stale comments, and no keys,
   tokens or passwords anywhere (the hosted build scans the upload and refuses it on a hit). Do your own security
   pass over the final version: permissions, untrusted page content reaching a tool that writes, injection into
   prompts or URLs, secrets in logs, and duplicate or unintended effects.
2. **`pytest`, then `gravity validate`, `gravity build`, `gravity push`.** Pytest is its own step so a pipe cannot
   hide its exit code. A pushed version is frozen; any fix is a new `version`.
3. **Wait for the build.** `gravity push` waits; `gravity agents` shows queued, building, ready or failed, with
   the reason.
4. **Re-run the hosted version from the consumer page,** with the same inputs as the matrix (§9), and record it:
   run id, time, cost, counts.
5. **Tell the Gravity team** what the agent does, example inputs, the accounts it needs and what a good result
   looks like. A new version is private until they approve it, and an agent is listed only while its newest
   version is approved. `gravity agents` shows their notes.
6. **Reconcile the record.** The spec's results section for the version (run ids, counts, findings), the README's
   limits, and the open items with the reason each is open.

## 14. Checklist for the next problem statement

Copy this into the task and tick it as you go.

- [ ] Outcome rows written from the statement's nouns, rules from its adjectives, edge cases listed;
      refusals and reinterpretations stated with reasons; the unsaid pinned in code
- [ ] Commercial products, living open source and reachable sources checked with dates; designs borrowed
      and features rejected listed with reasons; fixtures saved
- [ ] Quality markers for the output researched and written as code checks, not prompt wording
- [ ] Every tool the agent will use probed against real targets, from the sandbox; what each returns and
      where it fails written down (shells, challenges, 404s, 429s, quotas, 402s)
- [ ] The module table: promise, fact source, code part, model part; no row without a fact source
- [ ] The spec with numbered acceptance criteria that name their check; amended in place when the brief grows
- [ ] Code decides, model writes; a grounding gate between extraction and report; every figure labelled
      read, resolved or estimated; estimates in a dated table in code; `max_tokens` set; structured output
- [ ] Every module gets a second read for the figures the first page tends to omit
- [ ] Every edge has a failure boundary; modules time-boxed with partial rows kept; a refusal is data; every
      failed source listed once; the run always delivers something
- [ ] Paid tools on the user's account, capped, degrading without the connection
- [ ] Constructed links checked before shown; pay, ratings and rates only when stated in context
- [ ] Fake tools, fake model, full-graph test with injected failures and one test per module from the first
      commit; a real run kept as a fixture; no network in tests
- [ ] pytest as its own step, then `gravity validate`, `gravity build`, local real runs recorded, push;
      README
- [ ] Run from the real page as the test account with an uploaded file; the matrix; synthetic shapes with
      zero page errors; run ids and counts recorded
- [ ] Each complaint traced to its page or mechanism, fixed as a general rule with a test and a version, the
      same inputs run again
- [ ] A probe built for any module that keeps printing blanks
- [ ] Result shaped for the renderer with a layout hint and tab names, no view code; checked in chat and history
- [ ] Diff read, security pass recorded, spec verification and README reconciled

For an agent that acts (§17):

- [ ] Every outward effect is a draft or an approval with a fallback, and none assumes the person saw the prompt
- [ ] A stage per person, a suppression list checked before every send across channels, one touch per person per
      channel, a pause switch
- [ ] Caps, working hours and spacing live in code; an effect never repeats on a resumed run
- [ ] A test mode redirects every recipient before the first live send; real sends stay manual until the checks pass
- [ ] A person's identity is confirmed by a link they or their company control, never by a name match
- [ ] Memory is read once per run, written after the effect succeeded, and every collection is declared

## 15. Anti-patterns met on the way, and the rule each produced

| Anti-pattern | Rule |
|---|---|
| Telling the user to "confirm whether GRE is required" | The agent resolves or estimates; the user is never handed a chore |
| "unknown" in a cell the agent could have filled from a second page | Every module gets a second read; blanks are the last resort and say why |
| A midpoint estimate applied to every university in a country | Estimates follow the real rule (by state, by level, by institution type) or are not shown |
| A number the model returned that the page never printed | Grounding gate in code; a dropped field reads "not on the page" |
| A quote the post never contained | Verified as a substring of the text it claims, otherwise dropped and counted |
| A rate that was really an EMI-calculator default, or a home-loan rate in a footer | A figure counts only in the context of the product it belongs to |
| A probability of being hired, an admit percentage | Show what the best products show; a band or criteria met, never a number nobody has data for |
| Trimming page text to the first N characters | Focus the text on figure-bearing passages; menus are not content |
| Preferring a browser render's "main content" over the plain read | Keep the plain text when both exist; renders fill gaps, they do not replace |
| Alumni from a namesake institution; a rating from a namesake company | A person or a page is kept only when it names the institution or company (its city or country for people; the URL slug and the text for a review page) |
| Merging rows by lender name alone | Merge by lender and product family |
| A module that silently skipped itself when the run ran long | A time share per module, partial rows kept, a line that says it stopped |
| A link built from a name | Shown only after it answered 2xx |
| A paid render routed through the user's country | No `location` on renders; measured 36 s against 8 s |
| People searches fanned out on the paid backend | A cap per run on the paid tool, then the free backend |
| A source verified only from a laptop | Probe again from the sandbox; what works at home may be walled there and the reverse |
| A prompt asked for a cover letter | Measured markers of machine writing checked in code, one retry, flags on what still fails |
| Pushing on a chain that ignored pytest's exit code | pytest is its own step with `set -o pipefail` |
| A version bump without a run | A bump needs a run that shows the change, recorded in the spec with its numbers |
| Adopting a scraping library because it is popular | Try it on the real failure list first; 12 of 15 failures were stale URLs and the rest needed a browser the agent image cannot hold |
| A result that is prose and one table | Records with kinds and reader-facing keys, plus a layout hint; the platform draws it |
| Fixing a cut-off list in the agent's output | Fix the platform's clip once for every agent |
| A per-case patch for IBM, ITOL Recruit or SBI | Fix the mechanism for every short name, every parent brand, every lender |
| A broad `except Exception` around a tool call | It swallows the platform's approval pause. Re-raise `GraphBubbleUp` first, and add a test that fails on any such try |
| One blocking memory read per item | Read a collection once; 418 one-by-one reads froze a run past its heartbeat |
| A person confirmed by a name or a one-word company match | Confirm only with a link they or their company control; otherwise "possible match", never written to |
| Trusting a months-old indexed copy of a profile | Re-check against the live page; a changed employer or country downgrades the match |
| A step that makes something (a document, an event, a form) running again on resume | Key it by a hash of its arguments, and look things up by title before making them |
| A tracker synced from the whole memory each run | Write only what this run touched |
| Testing sends on real accounts with no guard | One choke point redirects every outbound recipient to a test address |
| Reading the quoted text of a reply | Read only the new part; a quoted footer once turned "Yes" into a refusal |
| A button that promises what the tool cannot do ("Close the form") | Name a step for what it does, and test the promise |
| A channel assumed to exist | Check the vendor's API first; default to the zero-risk way, where the person sends it themselves |

## 16. Where to look

| What | Where |
|---|---|
| The platform reference: manifest, code rules, tools, memory, actions, approvals, how a result is drawn | `Gravity.agent.md` in this folder |
| A plain overview for the person you build for | `Gravity.getting-started.md` |
| Commands and options | `gravity help`, or `-h` on any command; `gravity guide` for the longer builder guide |
| The live tool list | `gravity tools [text]` |
| What changed in the CLI | `gravity changelog` |
| The worked examples | Gravity's own agents. Their source is not in your folder, so use the patterns described here: pacing, deadlines and per-source status; counts, quote verification and de-duplication in code; a grounding gate; labelled tiers and a dated estimate table; identity confirmation; paced sends behind approvals; a test inbox; a layout hint |

## 17. Agents that act: what lead-gen and hiring added

The first three agents end in a report. These two end in effects: messages sent, forms opened, interviews booked, a
tracker kept. They follow every rule above, and add what a system that acts on a person's behalf needs.

**lead-gen** finds companies that would buy a product, the buyer at each (identity proved from the person's own
profile), their email with how it was found, a real recent fact, and a first email. It then keeps working: it finds
which drafts were sent, sorts replies, drafts answers and follow-ups in the same Gmail thread, stops on a bounce,
an opt-out or a no, and sends only what the person approves, by email or from their own LinkedIn or X. Version 1.4.0
adds sending through the person's own X developer app, a research step on the leads' own sites and issues, and
discovery from company homepages.

**hiring** is a desk for one role per conversation. It turns the role into a scoring sheet the owner approves,
finds people from public evidence or opens an application form with a deadline, checks every fact before using it,
scores blind with quotes, finds a way to reach each person, drafts outreach in the owner's voice, sends it paced
from the owner's Gmail, reads replies, sends a take-home test and grades it, keeps the pipeline in Notion, books
interviews with Meet links, writes the interviewer's brief and drafts the offer. "Nothing goes out without you."

| | Research agents | Acting agents |
|---|---|---|
| Shape | one run, one report | several named `actions`, some with schedules the person can switch on |
| Memory | none | collections that work as a small CRM: contacts, suppression list, sends, candidates, audit |
| Tools | read-only | send, book and write tools, behind approvals |
| Over time | each run stands alone | a loop: send, wait, read the reply, follow up, book |
| Safety code | grounding gate | suppression, caps, working hours, spacing, a test mode, a pause switch |
| Success | findings that are true and cited | the right thing happened, once, with consent |

**The rules they taught us**

1. **Design consent first.** Every outward effect is a gated call or a draft. Drafts come before sends; a refusal
   keeps the draft; never assume the person saw the prompt (§10 of `Gravity.agent.md`: their approval setting
   decides). Hiring's offer email defaults to "keep it as a draft", and only an explicit "send it" sends.
2. **State per person.** A stage for each person that never moves backwards, a suppression list checked before every
   draft and send across channels (an opt-out also covers their profile and handles), one touch per person per
   channel, a bounded follow-up plan (lead-gen: three days, then seven more, never a third), and `pause` and
   `resume` actions as a kill switch.
3. **Code owns the send plan.** Caps per day, the recipient's working hours in their time zone, a ramp-up, random
   spacing, a per-company limit, and a stop on a bounce rate or spam signal are plain functions with tests. The model
   writes words and never decides how many go out.
4. **A test mode before the first live send.** Hiring routes every recipient through one function that redirects
   email and invites to a test address, strips cc and bcc, and marks the message "[Test]". It sits inside the call
   wrapper, so no send path can miss it.
5. **Survive a pause.** A resumed run starts the node again in a new process. Re-raise the platform's pause (never a
   broad `except`), read saved settings first in every step, store ids on completion only, look things up by title
   before making them, and run anything that makes something once per hash of its arguments. Keep the order of
   gated calls the same on every pass, or an approval can land on the wrong call.
6. **Identity before action.** A person is "confirmed" only with a hard proof (a link they or their company
   control) or two strong signals; one anchor is a "possible match", shown as such and never written to. Re-check
   people taken from an indexed copy against their live page. A name match confirms nothing.
7. **Label every fact.** Verified, self-reported, unconfirmed. Email tiers: seen on their site, built from a
   colleagues' pattern, guessed, company inbox, verified, found but not verified, not found; never "verified"
   without a verifier's answer. The model never sees an unconfirmed fact.
8. **A personal detail needs evidence in code.** A "moment" to mention needs a URL, a date inside a window, the
   page's exact words (the writer may quote only those), no sensitive subject, and relevance to the product. A
   message with a number, name, customer or experience nobody supplied is withheld with a reason.
9. **Read only the new part of a reply.** Quoted text carries your own footer and options.
10. **Score what could be checked, and say how much.** Rank by coverage, cap the label by it, judge twice and
    average, show a gate as a flag and let a person confirm every "no". Calibrate against real rounds: hiring's
    Good-or-Strong share moved from 13 to 40 of 110 only after calibration, and two runs of the same role kept
    their label for 13 of 15 people.
11. **Test the writing on real leads with blind judges from at least two model families.** Each judge preferred
    its own family by three to four ranks. On 15 real leads, a prompt with five varied examples plus
    draft, check and rewrite on a strong model ranked 2.29; the earlier prompt ranked last at 6.76. Giving the
    writer the company's own site text mattered more than the model.
12. **Fix by mechanism, for every market.** Lead-gen was measured on 21 sender profiles in 11 countries over five
    rounds; hiring on 22 roles. Each defect became a general rule: a rival check must know who the product is for,
    a country missing from a list must not become a wrong confirmation, an unread page is a finding to look at by
    hand.
13. **Ask the risky choice at the step that needs it, and default to the zero-risk way.** How to send on LinkedIn or
    X (through the person's account, or by handing them the text to send) is asked when the person picks that
    channel, and defaults to "I'll send it myself". Declare it as a slot with `ask_in: <that action>` (`Gravity.agent.md` section 4): the person is asked after the action's own questions, only when their answers need it, and the pick is kept for later runs. Check
    the vendor's API before assuming a channel exists.
14. **Name every step for the person.** Plain words, what a button does, what "off" means for a scheduled step,
    and a "What next" that follows the stage (`_offer`, `_waiting`, `_stages`, `_keep_running`; see
    `Gravity.agent.md` section 9).
15. **Money is part of the design.** Use Gravity's own accounts for finders and readers where available, cap calls
    per run, label the tier of each result, and mark runs made after a budget failure as not comparable.

**What is not proven yet.** Neither agent has a recorded send to a real third party on the hosted platform in a
shipped version: approvals were tested on cards and drafts, and booking with a test inbox. Most emails are found but
not verified, because many servers accept any address. LinkedIn and X actions through `browser.act` can get an
account restricted. Lead-gen 1.4.0's gains were measured in local runs against the real tools (a UK Series A SaaS brief went from 1
confirmed buyer and 1 draft to 3 and 3), not yet on the hosted platform. Per-run cost is recorded for lead-gen (about a cent or two of model cost) and not for hiring.
Say these limits in any new acting agent's own README rather than hiding them.
