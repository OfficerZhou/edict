<h1 align="center">⚔️ Sansheng Liubu (Three Departments & Six Ministries) · Edict</h1>

<p align="center">
  <strong>I redesigned AI multi-agent collaboration around an imperial system from 1,300 years ago.<br>Turns out, the ancients understood checks and balances better than modern AI frameworks.</strong>
</p>

<p align="center">
  <sub>Sansheng Liubu = 8 universal skills (role prompts embedded, usable on ANY agent platform): the Crown Prince triages, the Chancellery plans, the Gate-Check reviews and can veto, the Secretariat dispatches, the Six Ministries execute in parallel, and the report returns to you.<br>One more layer of <b>institutional review</b> than CrewAI, one <b>live board</b> more than AutoGen.</sub>
</p>

<p align="center">
  <a href="#-demo">🎬 Demo</a> ·
  <a href="#-30-second-quick-start">🚀 30-Second Start</a> ·
  <a href="#-architecture">🏛️ Architecture</a> ·
  <a href="docs/task-dispatch-architecture.md">📚 Architecture Doc</a> ·
  <a href="CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Harness-Agnostic-8B5CF6?style=flat-square" alt="Any Harness">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Skills-8-8B5CF6?style=flat-square" alt="Skills">
  <img src="https://img.shields.io/badge/License-MIT-22C55E?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Backend-stdlib_only-EC4899?style=flat-square" alt="Zero Backend Dependencies">
</p>

---

## 🎬 Demo

<p align="center">
  <video src="docs/Agent_video_Pippit_20260225121727.mp4" width="100%" autoplay muted loop playsinline controls>
    Your browser does not support video. See the GIF below or <a href="docs/Agent_video_Pippit_20260225121727.mp4">download the video</a>.
  </video>
  <br>
  <sub>🎥 Full end-to-end walkthrough of the Sansheng Liubu AI multi-agent workflow</sub>
</p>

<details>
<summary>📸 GIF preview (faster)</summary>
<p align="center">
  <img src="docs/demo.gif" alt="Sansheng Liubu Demo" width="100%">
  <br>
  <sub>One sentence → Crown Prince triage → Chancellery planning → Gate-Check review → Six Ministries in parallel → memorial report (30 s)</sub>
</p>
</details>

---

## 🤔 Why Sansheng Liubu?

Most multi-agent frameworks work like this:

> *"OK, you AIs go talk among yourselves and hand me the result."*

Then you get a blob of output you can't reproduce, audit, or intervene in.

**Sansheng Liubu takes a completely different approach** — an institutional architecture that has existed in China for 1,400 years:

```
You (Emperor) → Crown Prince (triage) → Chancellery (plan) → Gate-Check (review) → Secretariat (dispatch) → Six Ministries (execute) → report back
```

This is not a fancy metaphor — it is **real checks and balances**:

| | CrewAI | MetaGPT | AutoGen | **Sansheng Liubu** |
|---|:---:|:---:|:---:|:---:|
| **Review mechanism** | ❌ none | ⚠️ optional | ⚠️ Human-in-loop | **✅ Dedicated Gate-Check reviewer · can veto** |
| **Live board** | ❌ | ❌ | ❌ | **✅ Junjichu Kanban + timeline** |
| **Flow audit** | ⚠️ | ⚠️ | ❌ | **✅ Full memorial archive** |
| **Setup cost** | mid | high | mid | **Low · skills-dir convention / one-click installer** |

> **Core difference: institutional review + full observability + live intervention**

<details>
<summary><b>🔍 Why the Gate-Check review is the killer feature</b></summary>

<br>

CrewAI and AutoGen agents collaborate in "ship it and move on" mode — nobody checks the quality of the output. Like a company with no QA department, engineers ship straight to production.

The **Gate-Check (门下省)** exists for exactly this:

- 📋 **Reviews plan quality** — is the Chancellery's plan complete? Are the subtasks sensible?
- 🚫 **Vetoes substandard output** — not a warning; it sends it straight back for rework
- 🔄 **Forces a rework loop** — nothing passes until it meets the bar

This is not an optional plugin — **it is part of the architecture.** Every edict passes the Gate-Check, no exceptions.

That is why Sansheng Liubu handles complex tasks reliably: a mandatory quality gate sits between planning and execution. 1,300 years ago, Emperor Taizong already understood — **unchecked power inevitably errs.**

</details>

---

## ✨ Capabilities

### 🏛️ Institutional flow (checks and balances — a process, not a suggestion)

- **Crown Prince triage** — chit-chat answered directly; only real edicts become tasks (≥10 chars + action verb + goal; 「传旨/下旨」 prefix forces the flow)
- **Chancellery planning** — draft the plan (≤500 chars): who / what / how / deliverable
- **Gate-Check review** — four-dimensional adversarial review (feasibility / completeness / risk / resources), **❌ veto sends it back** (≤3 rounds; round 3 is forced approval with notes); the reviewer runs in a fresh-context subagent with zero context shared with the drafter
- **Secretariat dispatch** — parallel dispatch across the ministries by responsibility matrix (any code task must include Works Ministry implementation + Justice Ministry testing)
- **Six Ministries execute** — specialized execution; verify before reporting done
- **Memorial report** — a report built on the board's fact chain (flow / progress / audit); done before presenting

### 🛡️ Institutional review + full observability

- State-machine validation: `kanban_update.py` enforces `_VALID_TRANSITIONS`; illegal jumps (Doing→Taizi) are rejected and logged
- Permission matrix: per-role board-command allowlist (AGENT_POLICY); out-of-scope calls are refused
- Audit log: every create/flow/confirm lands in `data/audit_log.json` (atomic writes, 5000-entry cap)
- Edict sanitization: titles/notes stripped of file paths, URLs, system metadata, and prefix words

### 🧩 Universal skill pack (any harness)

- Skill bodies describe **actions, never tool names** (tool mappings live in `skills/using-edict/references/<harness>-tools.md`)
- Copy the `skills/` directory and the full flow runs on any platform; when subagents/shell are unavailable, the embedded fallback wording takes over
- Root `install-skills.sh` / `install-skills.ps1` installs to the current platform in one command

### 📋 Junjichu Board (local · zero dependencies)

- State columns (Awaiting Triage → In Progress → Done) + auto-refresh every 5 seconds
- Click a card for the full flow timeline (including vetos) + audit trail
- Light/dark adaptive; click blank space to close the detail drawer
- Read-only: agents write cards via CLI; the board is only "eyes" (`python board/server.py` → http://127.0.0.1:7891)

### 📦 Task artifact convention

- Every edict's artifacts (code / docs / reports) land in `output/<task-ID>/` (e.g. `output/JJC-20260830-001/`); run outputs carry timestamps
- `output/` is fully gitignored — local artifacts never enter the repo

---

## 🚀 30-Second Quick Start

### Three steps (local, zero dependencies)

```powershell
cd F:\edict
.\install-skills.ps1   # 1. install the 8 skills into your current agent (auto-detects Claude Code/Codex/dsh)
.\start.ps1            # 2. start the Junjichu board → http://127.0.0.1:7891
```
Then say to the agent: 「朕要一个 React 待办应用，六部协同办理」— Crown Prince triage creates the card → Chancellery plans → Gate-Check reviews (a vague request may trigger a veto) → Secretariat dispatches → Six Ministries execute → memorial report, all visible live on the board.

> The historical demo image `docker run cft0808/sansheng-demo` still runs (old board, for nostalgia only; Docker sources were removed with the generalization).

### 🧩 Universal skill pack (harness-agnostic)

Sansheng Liubu is nobody's proprietary plugin: **`skills/` is a self-contained universal skill pack** (Agent Skills standard — `SKILL.md` + action language, no platform tool names), with every role's full prompt and persona enhancements embedded; copying one directory gives any agent that honors skills-dir conventions the complete flow (triage → plan → review → dispatch → execute → report), with zero mandatory platform/repo dependencies.

#### 🧰 One-click install into your agent (recommended)

Any agent that clones this repo can run the root installer, which puts the 8 skills into its platform's skills directory (auto-detects Claude Code / Codex CLI / DeepSeek Harness; `--target` to override):

```bash
git clone git@github.com:OfficerZhou/edict.git && cd edict
./install-skills.sh              # copy install (active in a new session)
./install-skills.sh --link      # symlink install, follows repo updates
./install-skills.sh --dry-run   # show plan only
```

Windows PowerShell:

```powershell
.\install-skills.ps1            # copy install
.\install-skills.ps1 -Link      # directory junction (no admin), follows repo updates
```

Open a new session and say 「朕要一个 React 待办应用，六部协同办理」 to verify the trigger. Manual per-platform skill locations are in `docs/porting-edict-to-a-harness.md` Part 1.

The universal layer consists of three things (details in `docs/porting-edict-to-a-harness.md`):

1. **Skill content**: `skills/*/SKILL.md` shared by all platforms; bodies only describe actions ("dispatch a fresh-context subagent", "update the task card"); fallback wording for degradable capabilities (no subagents / no shell) is embedded
2. **Tool mapping**: `skills/using-edict/references/<harness>-tools.md` translates each action into the platform's real tool
3. **Bootstrap**: at session start the `skills/using-edict/SKILL.md` is injected into context (via the platform's own mechanism: hooks / context file / plugin) — without it the skills sit inert, which is why each platform packaging adds this thin layer

> This repo ships **no platform integration files** (the former `.claude-plugin/`, `hooks/`, `.codex-plugin/`, `dsh-plugin/`, `AGENTS.md` and OpenClaw deployment files were removed; restore from the session backup `edict-deleted-20260830.tar.gz` or re-package per the porting guide).
>
> Acceptance test (any platform): in a clean session, the message 「朕要一个 React 待办应用，六部协同办理」 must trigger `edict-triaging` (create the task card, hand to the Chancellery) before any code is written.

#### Junjichu Board (optional companion)

`board/` (single-file page + stdlib API) + `scripts/kanban_update.py` form the board service: agents write cards via CLI, the board renders `data/` live — no database, no refresh loop:

```bash
python board/server.py   # board UI → http://127.0.0.1:7891
```

---

## 🏛️ Architecture

```
👑 The Emperor (you — one sentence in any agent conversation)
        │
   ┌────▼────────────────────────────────────────────┐
   │  Skill chain (skills/ · role prompts embedded)   │
   │  Crown Prince triage → Chancellery plan          │
   │   → Gate-Check review (can veto)                 │
   │   → Secretariat dispatch → Six Ministries → report│
   │  Each role = one skill; executed by fresh-context │
   │  subagents when available (review isolation),    │
   │  otherwise in-context role play                  │
   └────┬────────────────────────────────────────────┘
        │ board CLI (scripts/kanban_update.py)
   ┌────▼────────────────────────────────────────────┐
   │  Junjichu blackboard (data/tasks_source.json + audit) │
   │  Junjichu board board/ (read-only render)        │
   │  Task artifacts output/<task-ID>/ (local only)   │
   └─────────────────────────────────────────────────┘
```

### Role × skill mapping

| Role | Skill | Duty | Board command permissions (AGENT_POLICY) |
|------|------|------|------|
| Crown Prince | `edict-triaging` | Triage, create card, handoff, report | create/state/flow/progress/todo |
| Chancellery | `edict-planning` | Plan (≤500 chars), drive review & execution | state/flow/progress/todo/delegate |
| Gate-Check | `edict-review` | 4D adversarial review, veto | state/flow/progress/todo/confirm |
| Secretariat | `edict-dispatch` | Dispatch matrix, parallel scheduling, summary | state/flow/progress/todo/confirm/delegate |
| Six Ministries | `edict-ministries` | Specialized execution (works/infrastructure/data/docs/testing/HR) | progress/todo/done/block |
| Memorial | `edict-report` | Fact-chain-based memorial | — (last link) |
| Board | `edict-kanban` | Authoritative manual: state machine / permissions / commands | — (read-only) |

> The full permission matrix and state machine are defined in `skills/edict-kanban/SKILL.md` — the skill is the documentation.

### Task state flow

```
Emperor → Crown Prince triage → Chancellery plan → Gate-Check review → Dispatched → In Progress → Under Review → ✅ Done
                      ↑          │                              │
                      └──── veto ┘                    Blocked
```

> ⚡ **Protected transitions**: `kanban_update.py` enforces `_VALID_TRANSITIONS`; illegal jumps (e.g. Doing→Taizi) are rejected and logged — the flow cannot be bypassed.

---

## 📁 Project layout

```
edict/
├── skills/                     # universal skill pack (harness-agnostic core)
│   ├── using-edict/            # master skill: catalog/rules/degradation + tool mappings
│   ├── edict-triaging/         # Crown Prince · triage
│   ├── edict-planning/         # Chancellery · planning
│   ├── edict-review/           # Gate-Check · review & veto
│   ├── edict-dispatch/         # Secretariat · dispatch
│   ├── edict-ministries/       # Six Ministries · execution (+ references/depts personae)
│   ├── edict-report/           # memorial report
│   └── edict-kanban/           # board manual (state machine / permission matrix)
├── board/
│   ├── board.html              # Junjichu board (single file · zero dependencies)
│   └── server.py               # board API (Python stdlib · zero dependencies)
├── scripts/
│   ├── kanban_update.py        # board CLI (state machine/permissions/audit — agents' only write path)
│   ├── file_lock.py            # file lock (concurrency-safe writes)
│   └── utils.py                # shared utilities
├── edict/backend/              # event-driven backend (SQLAlchemy + Redis)
├── tests/                      # kanban CLI / state machine / skills lint tests
├── data/                       # runtime data (gitignored)
├── docs/
│   ├── porting-edict-to-a-harness.md    # 📚 porting guide: connect any agent platform
│   └── task-dispatch-architecture.md    # architecture doc: dispatch, flow, scheduling
├── install-skills.sh / .ps1    # one-click installer (skills/ → current platform)
├── start.ps1                   # one-click Junjichu board start (Windows)
├── CONTRIBUTING.md             # contributing guide
└── LICENSE                     # MIT License
```

---

## 🎯 Usage

### Issue an edict

In any agent conversation with the skills installed, issue the edict directly, in the tone of the emperor:

```
Design a user registration system:
1. RESTful API (FastAPI)
2. PostgreSQL
3. JWT auth
4. Complete test suite
5. Deployment doc
```

**Then sit back:**

1. 📜 The Chancellery receives the edict and plans the assignment
2. 🔍 The Gate-Check reviews — approve, or veto it back for replanning
3. 📮 The Secretariat dispatches the approved plan to the ministries
4. ⚔️ Ministries execute in parallel; progress is visible live
5. 📮 The Secretariat summarizes and reports back to you

Watch everything in real time on the **Junjichu Board**; intervene anytime (state change / block / cancel via CLI).

### Find the artifacts

Every edict's artifacts live in `output/<task-ID>/` (code/docs/reports; local only, not committed):
```
output/JJC-20260830-001/    # tool + usage guide + timestamped run reports
```

### Intervene

The board is read-only; intervention goes through the CLI (state-machine validated, high-risk transitions need confirmation):
```bash
python scripts/kanban_update.py state JJC-xxx Blocked "dependency missing"   # park
python scripts/kanban_update.py state JJC-xxx Cancelled "cancel"             # cancel (high-risk confirm)
python scripts/kanban_update.py confirm JJC-xxx approve "approved"           # confirm high-risk transitions
```

### Where are the personas?

Each role's full prompt is embedded in its skill body; tone/case enhancements live under `skills/edict-*/references/` (shipped with the skills).

---

## 🔧 Tech highlights

| Feature | Description |
|------|------|
| **Universal skill pack** | `skills/` works in any agent's skills directory (no platform/repo hard dependencies) |
| **Institutional review** | Adversarial 4D Gate-Check with veto loop, fresh-context reviewer isolation |
| **State machine audit** | Strict lifecycle transitions + full audit log |
| **Board** | `.\start.ps1` (Windows one-click) / `python board/server.py` |
| **Live refresh** | Board pulls task cards every 5 s (toggle in-page) |
| **Artifact convention** | All outputs under `output/<task-ID>/`, gitignored |

---

## 📚 Deep dive

- **[🧩 Porting guide](docs/porting-edict-to-a-harness.md)** — connect this skill pack to any agent platform
- **[🗺️ Architecture doc](docs/task-dispatch-architecture.md)** — full design of dispatch, flow, and scheduling
- **[🤝 Contributing](CONTRIBUTING.md)** — want to help? Start here

---

## 🔧 Troubleshooting

<details>
<summary><b>❌ Board doesn't update / service didn't start</b></summary>

**Check**:
```bash
python board/server.py            # start the board directly (127.0.0.1:7891)
python scripts/kanban_update.py flow JJC-xxx "test" "test" "ping"   # verify the CLI can write
```

**Common causes**:
- Board process not running (`.\start.ps1` or `python board/server.py`); port occupied (`-Port 8080` to switch)
- Corrupted task file: reset `data/tasks_source.json` to `[]` and re-run (test env only)
- Unquoted Chinese in command strings → add quotes

</details>

<details>
<summary><b>❌ The agent didn't start the Sansheng Liubu flow</b></summary>

**Check**:
1. Confirm skills are installed: `ls ~/.claude/skills/` shows 8 directories including `edict-triaging`
2. Open a new session (skill index loads at session start); try after `/clear`
3. The trigger needs an action verb + goal (≥10 chars): 「朕要一个 React 待办应用，六部协同办理」; prefix 「传旨：」 to force the flow
4. If a model occasionally misses the trigger, add one line to the project instructions file (AGENTS.md/CLAUDE.md): "task messages start with edict-triaging"

</details>

---

## 🗺️ Roadmap

> Full roadmap & how to participate: [ROADMAP.md](ROADMAP.md)

### Phase 1 — Core architecture ✅
- [x] Universal skill pack (harness-agnostic): 8 SKILL.md skills, role prompts embedded, degradable
- [x] Institutional review (gate-check 4D adversarial + veto loop ≤3 rounds + fresh-context isolation)
- [x] Junjichu board v2 (zero deps: state columns / flow timeline / audit trail / 5 s refresh)
- [x] Task state machine + permission matrix + audit log (enforced by kanban_update.py CLI)
- [x] Task artifact convention (output/<task-ID>/, local only)
- [x] One-click installer (install-skills.sh/.ps1: auto-detects Claude Code/Codex/dsh)
- [x] Porting guide (docs/porting-edict-to-a-harness.md: thin-layer integration for any platform)
- [x] Edict sanitization + duplicate-task protection + end-to-end test coverage

### Phase 2 — Institutional deepening 🚧
- [ ] Imperial approval mode (manual approval + one-click approve/veto)
- [ ] Express courier (live inter-agent message stream visualization)
- [ ] National history bureau (knowledge-base retrieval + citation tracing)

### Phase 3 — Ecosystem
- [ ] Notion / Linear adapters
- [ ] Annual exam (agent annual performance report)
- [ ] Mobile adaptation + PWA
- [ ] Plugin marketplace distribution

---

## 🤝 Contributing

All contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

Especially:
- 🎨 **UI enhancements**: dark/light themes, responsive design, animations
- 🤖 **New skills**: dedicated roles for specific scenarios
- 🔗 **Integrations**: Notion · Jira · Linear · GitHub Issues
- 🌐 **i18n**: Korean · Spanish · more

---

## 📂 Examples

`examples/` contains real end-to-end cases:

| Case | Edict | Departments involved |
|------|------|----------|
| [Competitive analysis](examples/competitive-analysis.md) | "Analyze CrewAI vs AutoGen vs LangGraph" | Chancellery→Gate-Check→Data+Engineering+Docs |
| [Code review](examples/code-review.md) | "Review this FastAPI code for security" | Chancellery→Gate-Check→Engineering+Justice |
| [Weekly report](examples/weekly-report.md) | "Generate this week's engineering team report" | Chancellery→Gate-Check→Data+Docs |

Each case contains: the full edict → Chancellery plan → Gate-Check verdict → ministry results → final memorial.

---

## ⭐ Star History

If this project makes you smile, please give a Star ⚔️

[![Star History Chart](https://api.star-history.com/svg?repos=cft0808/edict&type=Date)](https://star-history.com/#cft0808/edict&Date)

---

## 📄 License

[MIT](LICENSE) · originated from the OpenClaw community

---

<p align="center">
  <strong>⚔️ Governing AI with the wisdom of ancient empires</strong><br>
  <sub>以古制御新技，以智慧驾驭 AI</sub>
</p>
