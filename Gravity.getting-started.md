<!-- gravity-cli 0.10.0 · sha256:8e3ce6db71f8380cd1a09e4d056a0683e7b475ebf013c2977548ac35a3982052 · kept up to date by the Gravity CLI; edit a copy, or delete this line to keep your edits -->
# Getting started with Gravity

Gravity CLI 0.10.0 wrote this file and rewrites it on every update, so it always matches the version you
have. Do not edit it: an edited copy is left alone and stops getting updates (`gravity docs --force` replaces it).
Keep your own notes in a separate file.

This page is for anyone new to Gravity, technical or not. It explains what Gravity is, how agents work, what you can
build, and what we expect from an agent before it goes on the shelf. You can read it top to bottom in ten minutes.
Your coding assistant reads a longer, more technical file in this folder called `Gravity.agent.md`.

## 1. Gravity in one minute

Gravity is a place where **agents** live. An agent is a small piece of software that does a whole job for a person,
not just answers a question. A person types what they need, Gravity asks them the few things it still has to know,
and the agent goes and does the work: it reads websites, looks people up, writes drafts, books times, keeps track of
what it did and shows the result as a clear screen the person can act on.

If you build an agent, you decide what it does. Gravity runs it, keeps it safe, pays for the tools it uses, shows its
result nicely and lets people find it.

| Who | What they do |
|---|---|
| **A person using agents** | Opens Gravity, picks or describes what they need, answers a few questions, gets a result they can act on |
| **A builder** (you) | Designs an agent, builds it with the help of a coding assistant, tests it and publishes it |
| **Your coding assistant** | An AI helper such as Claude Code or Codex that writes the agent's code from your description. It reads the guides in this folder |
| **The Gravity CLI** | A small program called `gravity` that you run in a terminal. It sets up, checks, tests and publishes your agent |
| **The Gravity platform** | Runs the agent, gives it tools, asks the person before risky steps, keeps its memory and shows the result |

## 2. What an agent is, and what it is not

Ask a general chat assistant for "a two-bedroom flat in Delhi under 25,000 near my office" and you get a list of
names from memory. You then check prices, listings, commute and the neighbourhood yourself, one website at a time.

An agent does that checking for you. It asks for the facts the request left out, looks at the problem from every
side you would have checked, uses real sources, and shows a comparison you can act on.

**An agent for Gravity is its own small piece of software.** We do not want an agent that anyone could rebuild by
pasting a prompt into ChatGPT or Claude in one to three tries. We want:

- **A real job, done from end to end.** Several steps, several kinds of information, one clear outcome.
- **Real data.** Every name, number, price, link and quote comes from a source the agent actually read, and the
  source is shown. If something could not be found, the agent says so. It never makes it up.
- **Fact-checked.** The agent checks its own claims in code before it shows them. A made-up number is worse than a
  missing one.
- **Personal to the request.** Country, budget, role, industry, writing style: what the person typed changes what
  comes back. A generic answer is a failure.
- **Honest about limits.** What it could not read, what is an estimate, and how it estimated.
- **Safe to leave alone.** Anything that cannot be undone (sending an email, posting, booking) waits for the
  person's OK.

A good test: if the agent's whole value is a clever prompt, it is not an agent for Gravity yet.

### Two generations of agents

| | Research agents | Acting agents |
|---|---|---|
| Examples | job-scout, study-abroad-advisor, pain-point-discovery | lead-gen, hiring |
| What they do | Gather and compare information, then report | Do the work too: write messages, send them with approval, read replies, follow up, book interviews |
| Memory | Mostly none | Remember every person they contacted, so they never write twice and stop when someone says no |
| Runs | One run, one report | Several steps over days, some on a schedule |

The newer **lead-gen** agent finds companies that would buy a product, finds the right person at each, proves who
they are, finds their email and writes a first message. It then watches for replies and writes the follow-ups. The
**hiring** agent turns a role into a scoring sheet, finds candidates from public evidence, writes outreach, reads
replies, sends a take-home test, books interviews on the user's calendar and drafts the offer. Both ask before
anything goes out. This is the direction we want new agents to go in.

## 3. What an agent is made of

An agent is a folder with a few files. You will mostly let your coding assistant write them, but it helps to know
what they are.

| Piece | What it is, in plain words |
|---|---|
| `manifest.yaml` | The agent's **permission slip and order form**. It lists the questions to ask the person, the tools the agent may use, what needs approval, when it may run on its own, what it remembers and what files it can produce |
| `src/agent.py` | The agent's **steps**, written in Python. Each step does one job and hands its work to the next |
| `requirements.txt` | The libraries the code needs |
| `tests/` | Checks that prove the logic works before anyone relies on it |

The manifest is what keeps people safe. Gravity only lets the agent use what the manifest declares, on every single
call. If the agent tries anything else, Gravity refuses it.

**Code decides the facts, the model writes the words.** Counting, ranking, money, dates and de-duplication are
done by ordinary code that can be tested. The AI model is used for reading messy text and for writing sentences
around numbers the code worked out. The model never owns a number.

## 4. What your agent can use

You do not wire up accounts, keys or servers. You name the tool in the manifest and Gravity does the rest. At the
moment there are 54 hand-reviewed tools and 1,374 more imported ones across twelve apps, 1,428 in all. Run
`gravity tools` for the live list, or `gravity tools slack` to search it.

| What you want | Examples |
|---|---|
| Search and read the web | Search, read a page, read a page that needs a real browser, read pages that block normal visits through Gravity's proxies |
| Look up people and companies | Company search, work emails and email checks, public LinkedIn and X profiles, Reddit, YouTube transcripts |
| Email | Read, draft, send and reply in the person's Gmail |
| Calendar, documents and data | Free and busy times, create events, Drive files, Sheets, Notion |
| Teams | Slack, Linear, GitHub, Jira, Confluence and more |
| Forms | Google Forms, and Byteforms for public forms with a close date |
| Signed-in browsing | Read pages and send messages as the person on LinkedIn or X, after they sign in once on Gravity. The agent never sees the password |
| Post | A post on the person's LinkedIn |
| Direct messages on X | Look up an account and message it through the person's own X developer app, which they connect once and X bills |

Some of these tools run on **Gravity's own accounts**. The person connects nothing and the cost is counted against
the run's budget. The others run on the person's own connected account, and Gravity asks them to connect it.

### What Gravity gives every agent

| Feature | What it means |
|---|---|
| **Questions** | The form is built from the manifest. A question can appear only when an earlier answer needs it, or be an either/or choice. Typed answers (numbers, emails, web addresses) are checked before the agent sees them |
| **Models** | The agent uses AI models through Gravity. No keys to manage. Every call is counted against the run's spending cap |
| **Memory** | Between runs an agent can remember: a small notebook, plus lists of records with limits and expiry (for example "people already contacted"). Each person's memory is their own, and they can see and delete it |
| **Actions** | One agent can do several things. The person picks what to do next from buttons under a result, for example "find more", "write the emails", "send them" |
| **Approvals** | Before the agent does something that reaches other people or cannot be undone, the person sees exactly what will happen and says yes or no. Every approval step must have a fallback, such as keeping a draft |
| **Asking mid-run** | An agent can pause to ask the person a question and carry on with the answer |
| **Schedules** | An agent can run by itself on a schedule (India time, no more often than every five minutes). The person switches it on and can change the time |
| **Files** | The person can ask for the result as a web page, Word document, slide deck or spreadsheet. The agent writes one structured document and Gravity makes each format |
| **Spending cap** | Each run has a budget, one dollar by default. Past it, calls are refused and the agent should wrap up and say what it could not do |

## 5. How a result is shown (GenUI)

An agent does not build screens. It returns its result as plain, well-named data, and **GenUI**, Gravity's result
screen, turns it into something a person enjoys reading: a headline, key numbers, ranked cards that open for detail,
tables, charts, timelines, side-by-side comparisons, sources with their logos, drafts with a Copy button and a
"What next?" bar with the next steps.

You help GenUI by naming things for a reader (`shortlist`, `why`, `deadline`, not `x1`), returning numbers as numbers,
writing one sentence of answer first and giving every empty case a sentence. Your coding assistant knows the
details. An agent can also add a small hint about which parts to feature and what to call them. It never ships
screen code.

## 6. Using the CLI

The CLI is a program you type commands into. You need Python 3.12 or newer. `uv` installs it without fuss.

```bash
uv tool install gravity-cli
```

The first ten minutes:

| Step | Command | What happens |
|---|---|---|
| Sign in | `gravity login` | Opens your browser to sign in with Google. Nothing else to remember |
| Make an agent | `gravity init my-agent` | Creates a working starter agent in a new folder, with these guides inside |
| Build it | Ask your coding assistant | Open the folder in your assistant and describe the agent you want. Tell it to read `Gravity.agent.md` first |
| Check it | `gravity validate` | Runs the same checks Gravity runs when you publish, and lists every problem at once |
| Try it | `gravity run --input name=value` | Runs your agent on the real tools, so you see what a person would see |
| Try it with buttons | `gravity dev` | Opens a local page with the form, a live timeline and the result |
| Publish | `gravity build` then `gravity push` | Packages the agent, uploads it and builds it. It waits until it is ready or says what went wrong |
| See your agents | `gravity agents` | Lists your agents, their versions, review status and the team's notes |

Other commands you will use: `gravity tools` (what is available), `gravity connect gmail` (connect your own
account so local runs can use it), `gravity runs` and `gravity logs` (what happened on Gravity), `gravity docs`
(refresh these guides), `gravity update` and `gravity changelog` (stay current and see what changed). Add `-h` to any
command to see its options.

The CLI keeps itself current. When a new release comes out it updates itself, rewrites the guides in your folder and
shows what is new.

## 7. From idea to a published agent

1. **Start from a person's request**, written as a sentence a real user would type.
2. **Write down what the agent must produce**, what it must refuse, and what could go wrong. `problem-to-agent.md`
   in this folder is the method your coding assistant follows.
3. **Check the real sources first.** Find out what each tool and website really returns before designing around it.
4. **Build it in small steps with tests**, then `gravity validate` and `gravity run`.
5. **Test it as a user would**: publish, then use it from the real Gravity page. Every complaint you find becomes a
   general rule, a test and a new version.
6. **Publish** with `gravity push`. A published version never changes; fixes go out as a new version number.
7. **Review**: a new version stays private until the Gravity team approves it. Tell them what the agent does, example
   inputs, which accounts it needs and what a good result looks like.

## 8. Words you will meet

| Word | Plain meaning |
|---|---|
| Agent | A program that does a whole job for a person |
| Run | One go of an agent from question to result |
| Tool | One thing an agent can do in an app, such as "read Gmail" or "search the web" |
| Manifest | The agent's permission slip and order form |
| Gateway | Gravity's gatekeeper. Every tool and model call goes through it and is checked against the manifest |
| Approval | A moment where the person says yes or no before something goes out |
| Action | One of the things an agent can do, shown as a button |
| Memory | What an agent keeps between runs |
| Corpus | The structured document an agent returns when it wants downloads in several formats |
| GenUI | The part of Gravity that turns a result into a screen |
| Slot | A choice that decides which tools an agent gets, such as "deliver by Gmail or keep in Gravity" |

## 9. Where to go next

| You want to | Read |
|---|---|
| Build an agent with a coding assistant | `Gravity.agent.md` (the full reference) and `problem-to-agent.md` (the method) |
| See every command | `gravity -h` |
| Know what changed lately | `gravity changelog` |
| Learn from a good agent | The lead-gen and hiring agents show how to act safely on a person's behalf |
