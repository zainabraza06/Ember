# Flame in Freefall — Project Plan

**Event:** NASA Space Apps Challenge 2026, Islamabad local event (hackathon weekend: 14–15 November 2026)
**Challenge:** Flame in Freefall: AI-Powered Fire Safety Insights from Microgravity Combustion Data
**Working name:** *Ember* (rename freely)
**Document purpose:** The single source of truth for the build. Claude Code should read this file before starting any module and follow the module boundaries, acceptance criteria and scope rules below.

---

## 1. The challenge, decomposed into requirements

Challenge statement (official summary): NASA has studied flames in microgravity for decades and holds a large body of experimental results. As humans return to the Moon and go on to Mars, that knowledge matters more, but the volume of results makes them hard to find, compare and understand. Build an **interactive, AI-powered dashboard** that **summarizes, ranks and interprets** these findings to deliver **fire safety insights for human space exploration**.

> **Status of the official page (checked 18 October 2026):** only the challenge *summary* is published so far ("Challenge Summaries are now live"). The full details (Objectives, Potential Considerations, NASA Resources, Space Agency Partner Resources) are not yet on the page. The summary text is saved in `docs/CHALLENGE.md`.
>
> **Wording note:** the page title says "AI-Powered", while the summary body says "super intelligence (SI) powered dashboard". Treat both as the same requirement (an AI-driven dashboard); the AI must be visibly central, not decorative.
>
> **Action:** re-check the challenge page weekly and on release of the full details, copy them into `docs/CHALLENGE.md`, then update sections 1 and 4 of this plan. Every resource listed there must be used or explicitly considered, because "Relevance" is judged on how well NASA resources are integrated. Until then, section 4 is our own best estimate of the data sources.

### 1.1 Explicit requirements (stated by the challenge)

| ID | Requirement | How we meet it |
|---|---|---|
| R1 | Interactive dashboard | Web app with filters, comparisons, charts, scenario controls (M9) |
| R2 | AI-powered | LLM extraction, grounded Q&A, learned flammability model, generated briefs (M3, M4, M6, M8) |
| R3 | **Summarize** findings | Per-experiment, per-material and per-scenario summaries, every sentence cited (M3, M8) |
| R4 | **Rank** findings | Transparent multi-criteria ranking with mission profiles and adjustable weights (M5) |
| R5 | **Interpret** findings | Effect directions, consensus/contradiction detection, flammability envelope with uncertainty (M6) |
| R6 | Use NASA microgravity combustion data | PSI datasets, NTRS reports, NASA Glenn experiment pages (M1) |
| R7 | Fire safety insights | Actionable outputs: material screening, atmosphere risk, detection and suppression notes (M8) |
| R8 | For human space exploration (Moon, Mars) | Mission profiles incl. partial gravity and exploration atmospheres (M5, M6, M8) |
| R9 | Address "hard to find, compare, understand" | Unified schema (find/compare) + plain-language layer (understand) (M2, M9) |

### 1.2 Implicit requirements (what judges will check without saying so)

| ID | Requirement | Why it matters |
|---|---|---|
| I1 | Scientific validity | "Validity" is a judging criterion. NASA subject-matter experts judge globally. No invented numbers, no overclaiming. |
| I2 | Traceability | Every number and claim links to a specific source page or data file. |
| I3 | Honest uncertainty | Show where evidence is thin, conflicting, or outside tested conditions. Refuse when appropriate. |
| I4 | Partial gravity gap | Most data is ~0 g or 1 g; Moon (0.16 g) and Mars (0.38 g) are under-tested. Saying so explicitly is a strength. |
| I5 | Multiple audiences | Engineers, mission planners, crew, educators/public. |
| I6 | Works live | A stable deployed demo plus a recorded fallback. |
| I7 | Reusable / continuable | Public repo, clear README, open data, documented pipeline. |

### 1.3 Submission and judging requirements

- **Judging criteria (five, equal weight):** Impact, Creativity, Validity, Relevance, Presentation.
- **Demo:** a video of **up to 30 seconds** (English subtitles required) **or** a slide deck of **up to 7 slides** (English). Links only; files are not uploaded to the Space Apps site.
- **Global nomination:** project page must link to a **public code repository**, and clearly show which NASA / partner agency data was used.
- **Local judging:** run by the Islamabad hosts; confirm format (live pitch length, Q&A).
- **Build window (team decision, 19 October 2026):** the full product is built between 19 October and 13 November. The hackathon weekend (14–15 November) is used for final testing, the demo video, slides, pitch rehearsal and submission inside the official submission window. Keep the full git history and disclose the build period honestly if asked.
- Team size: maximum 6.

### 1.4 Judging criteria → design decisions

| Criterion | What wins it | Where |
|---|---|---|
| Impact | A named user with a real decision (habitat/vehicle designer choosing materials and cabin atmosphere); exportable mission fire-safety brief | M8 |
| Creativity | Evidence ledger with contradiction detection; partial-gravity risk view; "what NASA should test next" recommender | M3, M6, M7 |
| Validity | Measured evaluation, held-out checks, physics sanity checks, applicability-domain guard | M6, M10 |
| Relevance | Breadth of NASA resources actually integrated; direct mapping to summarize/rank/interpret | M1, M5 |
| Presentation | 30-second video and 7-slide deck built around one story; clean UI | M13 |

---

## 2. Competitive landscape and our angle

Many teams worldwide have already published public repositories for this challenge. Common patterns observed:

- Cited Q&A chatbots over NASA reports
- Single-dataset ML predictors (e.g., FLEX droplet extinction, BASS-II spread)
- Flammability "envelope" sliders with range guards
- Weighted ranking of findings with export
- 3D flame visualizations and gamified quizzes
- Data-cleaning catalogues of the PSI combustion investigations

**Conclusion:** a chatbot, a slider, or a 3D flame alone will not stand out. We win on **depth of evidence handling, validity, and a decision-grade output**.

**Our angle (one sentence):**
*Ember turns NASA's scattered microgravity fire research into a verified evidence ledger, then answers one real question for any mission — "What will burn here, how sure are we, and what should NASA test next?" — and exports it as a cited fire-safety brief.*

**Differentiators (must all appear in the demo):**

1. **Evidence Ledger.** Findings stored as atomic, verified claims (condition → effect → magnitude → source page), not chunks of text.
2. **Consensus and contradiction map.** Where multiple experiments agree, disagree, or are silent.
3. **Partial-gravity lens.** Moon and Mars views that show how much evidence exists at each gravity level and where conclusions are extrapolated.
4. **Next-experiment recommender.** The gaps in the oxygen × pressure × flow × gravity space where a new test would reduce uncertainty most.
5. **Mission Fire-Safety Brief.** One-click, fully cited PDF/HTML brief for a chosen mission profile.
6. **Published validation numbers** shown inside the app (not only in the README).

Rule: **do not copy or adapt any other team's repository.**

---

## 3. Primary user story and demo narrative

**Primary user:** a habitat or vehicle fire-safety engineer preparing a design review for a lunar surface habitat.

**Decision:** which cabin atmosphere and which interior materials are acceptable, and where the evidence is too weak to rely on.

**Demo narrative (drives every build decision):**
1. Select mission profile "Lunar surface habitat" (partial gravity, exploration atmosphere).
2. Ember shows the top-ranked risks and findings, each with evidence strength and citations.
3. User picks two candidate materials; side-by-side comparison against tested conditions.
4. Envelope view shows where these materials are tested, where they are extrapolated, and where Ember refuses to predict.
5. Contradiction panel highlights one place where experiments disagree.
6. Gap panel recommends the most informative next test.
7. Export the Mission Fire-Safety Brief.

Secondary personas (light-touch modes, same data): **Crew** (short procedure-style safety card), **Educator/Public** (plain-language explainer).

---

## 4. Data sources (to verify and catalog in M1)

| Source | Content | Use |
|---|---|---|
| NASA Physical Sciences Informatics (PSI), Combustion Science | ~24–25 investigations; experiment matrices (test conditions), measurements, metadata, media | Primary structured data |
| NASA Technical Reports Server (NTRS) + its API | Technical memoranda, papers, final reports for each experiment | Claim extraction, tables in reports |
| NASA Glenn ISS research pages | Experiment descriptions (BASS/BASS-II, ACME, FLEX, Saffire, SoFIE etc.) | Context, summaries |
| NASA Task Book | Project descriptions for investigations without PSI data | Coverage of gaps |
| NASA materials flammability standard (Test 1, upward flame propagation) | 1 g screening test basis | "Passes on Earth, burns in space" interpretation |
| NASA exploration atmosphere report (NASA/TP-2010-216134) | Proposed reduced-pressure, elevated-oxygen cabin atmospheres | Mission profiles |
| Space agency partner resources listed on the challenge page (e.g., JAXA, ESA, CSA, if listed) | Partner microgravity combustion results | Relevance + coverage |

Candidate experiment families (confirm which have usable tables): BASS, BASS-II, ACME (incl. CFI-G and other ACME flames), FLEX, FLEX-2, Saffire series, SLICE, SoFIE, smoke/aerosol measurement experiments (fire detection), drop-tower and parabolic-flight studies.

Data rules:
- Record license and citation for every file (PSI public data is reported as CC0; verify).
- Some PSI legacy files are reported broken (404); log, do not block on them.
- PSI media is very large (terabytes, mostly video). **Never bulk-download media.** Download experiment tables and metadata; fetch media only for a chosen stretch module.
- **Scope:** commit to **3–5 experiment families** with good tables for the structured layer; reports for others can still feed the evidence ledger.

---

## 5. Architecture overview

```
Sources (PSI, NTRS, Glenn, Task Book, partners)
        │  M1 acquisition + provenance manifest
        ▼
Raw store ──► M2 harmonized test table  ──► M6 envelope model + domain guard
        │                                   │
        └──► M3 evidence ledger (claims) ───┼──► M5 ranking engine
                    │                       │
                    ├──► M4 retrieval + grounded Q&A
                    ├──► M6 consensus/contradiction
                    └──► M7 gap + next-experiment
                                            │
                              M8 mission brief generator
                                            │
                              M9 dashboard (API + UI)
        M10 evaluation runs across M3–M8 · M12 deploy · M13 pitch
```

**Recommended stack (team already strong here):**
- Backend: Python, FastAPI; analytical store DuckDB or SQLite (single file, easy deploy); vector index in-process (e.g., Chroma or FAISS).
- AI: one frontier LLM via API for extraction and generation; local sentence-embedding model for retrieval; scikit-learn / gradient boosting for the envelope model with calibrated probabilities.
- Frontend: React/Next.js + TypeScript, a charting library, Tailwind.
- Deploy: frontend on Vercel, backend on Render or similar; all precomputed artifacts committed or built in CI so the demo never depends on live scraping.
- API keys only server-side. Cache all LLM outputs used in the demo.

---

## 6. Modules

Each module lists: **Goal · Inputs · Outputs · Acceptance criteria · Depends on · Priority** (P0 = must ship, P1 = should, P2 = stretch).

### M0 — Challenge lock and rules
- **Goal:** fix scope and constraints before building.
- **Inputs:** official challenge page, Space Apps submission guide, Islamabad event rules.
- **Outputs:** `docs/CHALLENGE.md` (full text), `docs/RULES.md` (submission format, deadlines, what pre-work is allowed), requirement checklist mapped to modules (section 1 of this plan, kept current).
- **Acceptance:** every listed NASA/partner resource appears in the M1 catalog with status "used" or "considered, reason".
- **Priority:** P0.

### M1 — Data acquisition and provenance catalog
- **Goal:** collect the raw material with full provenance.
- **Inputs:** sources in section 4.
- **Outputs:** `data/raw/` organized by source and investigation; `data/catalog.csv` with one row per file: source, investigation ID, title, URL, license, retrieval date, file type, size, status (ok / broken / skipped), notes; per-investigation `info.md` (objective, approach, conditions varied, outcome measured).
- **Acceptance:** catalog covers all chosen experiment families; no media bulk downloads; reruns are idempotent.
- **Depends on:** M0. **Priority:** P0.

### M2 — Unified schema and harmonized test table
- **Goal:** one comparable table of individual tests across experiments.
- **Outputs:** `data/processed/tests` with, at minimum: test ID, experiment family, platform (ISS, Cygnus, drop tower, aircraft), gravity level, fuel/material (normalized name + class: solid sheet, fabric, droplet, gas jet, wire insulation), sample geometry, oxygen fraction, total pressure, diluent, flow velocity and direction (opposed / concurrent / quiescent), ignition method, outcome class (no ignition / self-extinguished / sustained / spread), spread rate, burn duration, extinction condition, source reference (file + row or report + page + table).
- Units normalized (SI), original value kept alongside. Data-quality flags (estimated, transcribed from figure, missing).
- **Data dictionary** document explaining every column.
- **Acceptance:** spot check of 20 random rows against sources has zero unexplained mismatches; every row has a source reference.
- **Depends on:** M1. **Priority:** P0.

### M3 — Evidence Ledger (claim extraction and verification)
- **Goal:** turn reports into atomic, verified findings.
- **Claim record:** claim ID, statement (plain language), variable(s), condition range (O₂, pressure, flow, gravity, material), effect direction (increases / decreases / no effect / threshold), magnitude if reported, evidence type (measurement, observation, model, review), source (document, page, table/figure), **verbatim supporting span**, extraction confidence, verification status.
- **Pipeline:** LLM extraction per document section → automatic verification that the supporting span exists in the source text and that numbers in the claim appear in the span → human review queue for low-confidence claims.
- **Outputs:** `data/ledger/claims` plus review log.
- **Acceptance:** 100% of published claims have a verified span; human audit of 30 random claims ≥ 90% judged correct; claims failing verification never reach the UI.
- **Depends on:** M1 (M2 for linking claims to tests). **Priority:** P0.

### M4 — Retrieval and grounded Q&A
- **Goal:** answer free-text questions using only the ledger, tests and source passages.
- **Behavior:** hybrid retrieval (keyword + embeddings) over claims and passages; answers cite claim IDs and source pages; explicit **refusal** when evidence is missing or outside tested conditions; shows evidence strength for each answer.
- **Acceptance:** on the M10 question set, citation precision ≥ 90%, unsupported-answer rate ≤ 5%, correct refusal on all out-of-scope questions in the set.
- **Depends on:** M3. **Priority:** P0.

### M5 — Ranking engine
- **Goal:** rank findings, materials and experiments for a selected mission profile.
- **Mission profiles:** ISS / LEO, Orion-class transit vehicle, lunar surface habitat, Mars transit, Mars surface habitat. Each defines gravity, cabin atmosphere range, ventilation regime, crew response constraints.
- **Ranking criteria (each shown and adjustable):** safety severity, relevance to profile conditions (distance between tested and profile conditions), evidence strength (number of independent tests, consistency, platform quality), actionability (does it change a design choice), recency.
- **Outputs:** ranked list with per-criterion score breakdown; sensitivity view (which items move when weights change); export CSV/JSON.
- **Acceptance:** every score is reproducible from documented formulas; changing profile visibly changes the ranking in a way the team can explain in the pitch.
- **Depends on:** M2, M3. **Priority:** P0.

### M6 — Interpretation engine
Three parts:
- **6a Effect synthesis:** for each variable (O₂, pressure, flow, gravity, material class), aggregate claims into consensus statements with direction, strength and number of supporting sources. P0.
- **6b Consensus / contradiction detection:** flag claim pairs with overlapping conditions and opposite directions or incompatible magnitudes; show both sides with sources; never resolve silently. P0.
- **6c Flammability envelope model:** predict outcome class (and, where data allows, spread rate) from test conditions using the M2 table; calibrated probabilities; **applicability-domain guard** that refuses or warns outside the tested region; nearest real tests shown with every prediction; interpretable effects (e.g., monotonic constraints or partial-dependence views). P1.
- **Physics sanity checks (shown in UI):** e.g., more oxygen should not lower predicted flammability at fixed other conditions; checks run on load and display pass/fail.
- **Acceptance:** envelope model evaluated with leave-one-experiment-out validation; metrics reported against a simple baseline; domain guard triggers on held-out extreme conditions.
- **Depends on:** M2, M3.

### M7 — Evidence gap map and next-experiment recommender
- **Goal:** show where NASA knowledge is thin and what to test next.
- **Outputs:** coverage heatmaps over O₂ × pressure, flow × gravity, material class × gravity; highlighted mission-relevant gaps (especially lunar and Martian gravity); ranked list of recommended next test conditions with the reason (high model uncertainty, mission relevance, contradiction to resolve).
- **Acceptance:** each recommendation states the condition, the reason and the profiles it serves; recommendations change sensibly with profile.
- **Depends on:** M2, M6. **Priority:** P1 (the heatmap alone is P0).

### M8 — Mission Fire-Safety Brief generator
- **Goal:** the decision-grade deliverable.
- **Contents:** profile summary; top ranked risks; material screening for user-selected materials; atmosphere considerations; detection and suppression notes where evidence exists; contradictions and gaps; confidence statement; full reference list.
- **Persona modes:** Engineer (full brief), Crew (one-page card), Public (plain-language explainer).
- **Rules:** every sentence traceable to claim IDs; generation constrained to ledger content; template-first, LLM fills only cited slots.
- **Outputs:** HTML view + PDF export.
- **Acceptance:** zero uncited factual sentences in a review of three generated briefs.
- **Depends on:** M5, M6, M7. **Priority:** P0 (Engineer mode), P1 (other modes).

### M9 — Dashboard (API + UI)
- **Pages:**
  1. **Mission** — profile selector, top risks, evidence strength, "export brief".
  2. **Explore** — experiment and test browser with filters, timeline, side-by-side comparison.
  3. **Ledger** — searchable claims with verified source spans.
  4. **Envelope** — condition sliders, prediction, nearest tests, domain guard state.
  5. **Consensus & Gaps** — contradiction list, coverage heatmaps, next-experiment list.
  6. **Ask** — grounded Q&A with citations and refusals.
  7. **Validation** — live evaluation numbers and sanity-check status.
  8. **About / Data** — sources, licenses, methodology, limitations.
- **Requirements:** fast first load (precomputed artifacts), mobile-usable, accessible contrast, every number clickable to its source, visible "not for flight decisions" note.
- **Acceptance:** the full section-3 demo narrative runs end-to-end in under 3 minutes without errors on a fresh device.
- **Depends on:** M2–M8. **Priority:** P0.

### M10 — Evaluation and validation
- **Goal:** prove validity with numbers.
- **Assets:** gold question set (≥ 40 questions: factual, comparative, ranking, out-of-scope), gold claim audit sample, held-out experiment family for the envelope model.
- **Metrics:** retrieval recall@k, citation precision, unsupported-answer rate, refusal accuracy, claim extraction precision, envelope model accuracy / balanced accuracy / calibration vs baseline, domain-guard trigger rate.
- **Outputs:** `docs/EVALUATION.md` and the in-app Validation page.
- **Acceptance:** metrics regenerate from one command; results versioned.
- **Depends on:** M3–M6. **Priority:** P0. (Question set can be written before the weekend.)

### M11 — Stretch: video-based flame measurement
- **Goal:** extract flame-front position over time from a small number of PSI flight videos, compute spread rate, compare with reported values.
- **Why:** strong creativity and validity signal; few teams will attempt it.
- **Constraint:** only if M0–M10 P0 items are done; use 2–3 short clips only.
- **Priority:** P2.

### M12 — Deployment and repository quality
- Public repo, README (problem, solution, data used, how to run, evaluation results, limitations), license, data attribution, architecture diagram, reproducible build of processed data, deployed URLs, recorded fallback demo.
- **Acceptance:** a stranger can reproduce processed data and run the app from the README.
- **Priority:** P0.

### M13 — Pitch and submission
- **30-second video** (English subtitles): problem (5 s) → the engineer's question (5 s) → Ember answering with evidence, contradiction and gap (15 s) → impact line (5 s).
- **7-slide deck:** title; problem; user and decision; solution and differentiators; validation numbers; NASA data integrated; impact and next steps.
- **Live pitch** (length per local rules) with rehearsed Q&A on: data scope, validity limits, partial-gravity extrapolation, why ranking weights are what they are.
- **Submission page:** project description, NASA resources used, repo link, demo link, all required boxes checked well before the deadline.
- **Priority:** P0.

---

## 7. Scope control

**Minimum winning product (must exist by 9 November, leaving the last week for testing and polish):** M1, M2 (3 families), M3, M4, M5, M6a, M6b, M7 heatmap, M8 Engineer brief, M9 pages 1–3, 5, 6, 7, M10 core metrics, M12, M13.

**Add if on track:** M6c envelope model and Envelope page, M7 recommender, persona modes.

**Only if everything else is done:** M11.

**Cut rules:** never cut validation (M10), citations, or the export brief. Cut visual polish, extra experiment families and persona modes first.

---

## 8. Team allocation (adapt to final team, max 6)

| Role | Modules |
|---|---|
| Data lead | M1, M2 |
| AI/NLP lead | M3, M4, M8 generation |
| Modeling & evaluation lead | M5 formulas, M6, M7, M10 |
| Full-stack lead | M9, M12 |
| Pitch, design & science-communication lead | M13, UI design, persona content, data-dictionary review |
| Floater / domain reader | Reads key NASA reports, validates claims (M3 review queue), helps M2 transcription |

---

## 9. Timeline

The full build happens before the event. Each week ends with a working, deployed version.

**Week 1 (19–25 Oct): data foundation**
- M0, M1 done. M2 complete: data dictionary, outcome mapping, transcribed report tables, harmonized test table built by pipeline, 20-row spot check passed.
- M10 started: first 20 gold questions written.
- Repo skeleton for backend and frontend; deployment accounts ready.

**Week 2 (26 Oct – 1 Nov): evidence and AI core**
- M3 Evidence Ledger: extraction, span verification, review queue, 30-claim audit.
- M4 grounded Q&A with refusals.
- M10: question set at 40+, first metrics run.
- First end-to-end slice deployed: Ask page answering with citations.

**Week 3 (2–8 Nov): ranking, interpretation, brief, dashboard**
- M5 ranking with mission profiles; M6a/6b synthesis and contradictions; M7 coverage heatmaps; M8 Engineer brief with PDF export.
- M9 pages: Mission, Explore, Ledger, Consensus & Gaps, Ask, Validation, About.
- Minimum winning product (section 7) complete by 9 November.

**Week 4 (9–13 Nov): depth, hardening, presentation**
- M6c envelope model and Envelope page; M7 recommender; persona modes if on track.
- M11 video measurement only if everything above is done.
- Full evaluation run, bug fixing, performance, mobile check, README and repo cleanup (M12).
- Feature freeze on 12 November. Draft 30-second video, 7 slides and pitch script (M13); first rehearsal.

**Hackathon weekend (14–15 Nov): finish and submit**
- Saturday: recheck official guides and the challenge page for any new requirements or resources; adjust only if required. Final testing on fresh devices. Record and subtitle the final video; finalize slides.
- Sunday morning: final deploy, fill the submission page, submit by midday (well before the deadline).
- Remaining time: rehearse the live pitch and Q&A twice.

---

## 10. Instructions for Claude Code

1. Read this file and `docs/CHALLENGE.md` before any task.
2. Work one module at a time; state which module and which acceptance criteria a change addresses.
3. Never invent data, numbers, citations or sources. If a value is unknown, mark it missing and flag it.
4. Every claim, number and summary shown in the UI must carry a source reference (document + page/table, or dataset file + row).
5. Never bulk-download PSI media. Respect the catalog and record provenance for anything fetched.
6. Keep secrets server-side; cache LLM outputs used in the demo.
7. Prefer precomputed artifacts over runtime scraping so the demo is stable offline.
8. Do not copy code or content from other teams' repositories for this challenge.
9. After each module, update `docs/STATUS.md` (done, open issues, next step) and the requirement checklist.
10. Ask the team before changing scope, schema, ranking formulas or mission profiles.

---

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Data harder to extract than expected (PDF tables, inconsistent formats) | Limit to 3–5 families; transcribe key tables manually with source references |
| LLM hallucination in claims or briefs | Span verification, template-constrained generation, refusal behaviour, audit |
| Overclaiming partial-gravity conclusions | Explicit extrapolation labels; gravity-level evidence counts on every finding |
| Demo failure on stage | Precomputed data, deployed backup, recorded video fallback |
| Too many features, weak polish | Section 7 cut rules; feature freeze on Day 2 midday |
| Official 2026 guides (published 13 Nov) add rules on pre-event work | Keep full git history, disclose the build period, and be ready to adjust the submission on 14 November |