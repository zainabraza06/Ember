# Evidence ledger schema (M3)

The ledger turns NASA documents into **atomic, verified claims**. It is the only source of truth for Q&A (M4), ranking (M5), contradictions (M7) and briefs (M8): anything not in `data/ledger/claims.jsonl` with status `verified_auto` or `approved` must not reach the UI.

## Files
| file | content | in git |
|---|---|---|
| `data/ledger/sources.csv` | one row per document: NTRS id, title, authors, year, NASA rights determination, `us_government_work`, `display_verbatim`, `study_family`, URL, PDF URL, local path, bytes, SHA-256, scope pages | yes |
| `data/ledger/pages.jsonl` | text layer: `{doc_id, page, text}` per PDF page (pypdf), page = PDF page index starting at 1 | no (derived; `python -m ledger pages`) |
| `data/ledger/cache/*.json` | one file per LLM call: provider, response, **exact model version returned**, token usage, prompt version | yes |
| `data/ledger/providers.json` | models chosen by `python -m ledger smoke` | yes |
| `data/ledger/usage.jsonl`, `run_log.jsonl` | one line per real API call (tokens), retries and stops | yes |
| `data/ledger/claims.jsonl` | claims with status verified_auto, approved or needs_review | yes |
| `data/ledger/rejected.jsonl` | rejected claims with the reason (kept for audit, never shown) | yes |
| `data/ledger/pilot.json` | pilot results per prompt version | yes |
| `data/review/claim_review.csv` | needs_review queue and human decisions | yes |
| `docs/CLAIM_AUDIT.md` | 30 seeded random verified claims for the human audit | yes |
| `docs/LEDGER_REPORT.md` | generated report | yes |

## Claim record (one JSON object per line)
| field | type | meaning |
|---|---|---|
| `claim_id` | string | `C-<10 hex>` = SHA-1 of document id, PDF page and the normalised span (letters, digits and dots only). It does not depend on the model's wording, so it is stable across runs. Several claims sharing one span get suffixes `-b`, `-c` in the order of their normalised statements |
| `doc_id`, `page`, `locator` | string, int, string | document (`NTRS-<id>`), PDF page where the span was **found** (a wrong page named by the model is corrected from the text and flagged `page_corrected`), table/figure/section if the page names one |
| `statement` | string | plain-language sentence; every number in it must appear in the span |
| `variables` | list | from: oxygen_concentration, pressure, flow_velocity, flow_direction, gravity_level, material, sample_thickness, sample_geometry, ignition, flame_spread_rate, burn_time, extinction, flame_temperature, blowoff, radiation, fuel_type, diluent, other |
| `conditions` | object | `gravity_class` (microgravity, lunar, mars, partial_other, earth_1g, not_stated), `gravity_g`, `oxygen_fraction_min/max` (0-1), `pressure_kpa_min/max`, `flow_cm_s_min/max`, `material`, `geometry`. null = not stated. Only fixed conversions are allowed (percent to fraction, psia, atm, mmHg to kPa, mm/s and m/s to cm/s) |
| `effect_direction` | enum | increases, decreases, no_effect, threshold, not_applicable |
| `magnitude_text` | string | magnitude as printed, if any |
| `evidence_type` | enum | measurement, observation, model, review |
| `span` | string | **verbatim supporting text** (at most 600 characters) |
| `extraction_confidence` | enum | high, medium, low (given by the model) |
| `verification` | object | `span` {result exact/fuzzy/fail, score, page, page_corrected}, `numbers` {pass/fail, missing}, `conditions` {pass/fail, fields}, `gravity` {pass/context/fail}, `support` {supported/partial/unsupported/error/pending, reason, model_version} |
| `status` | enum | `verified_auto`, `needs_review`, `approved`, `rejected` |
| `reasons` | list | why a claim is not verified_auto (see below) |
| `group_id`, `group_size`, `independent_sources` | | set for public claims, see Grouping |
| `chunk_id`, `prompt_version`, `verify_prompt_version`, `model_version`, `flags` | | provenance |

## Verification and status
1. **Span check** (code): the normalised span must be a substring of the normalised page text. Exact = pass. Not on the named page but exactly on another page of the document: page corrected. No exact match but a window with similarity >= 0.95: `fuzzy_span` (needs_review). Otherwise **rejected** (`span_not_found`).
2. **Number check** (code): every number in `statement` and `magnitude_text` must appear in the span with the same value (a percentage may be written as a fraction). Failing: `number_not_in_span` (needs_review).
3. **Condition check** (code): each numeric condition must follow from a printed number by one of the fixed conversion factors. Failing: `condition_value_not_in_span` (needs_review).
4. **Gravity check** (code): a lunar, mars, microgravity or earth_1g class needs a matching word in the span (or, as `context`, on the same page). Failing: `gravity_class_not_in_text` (needs_review).
5. **Support check** (LLM, `prompts/verify_v1.md`; a separate call to a **different model family** (Groq/Llama) from the extractor (Gemini)): `unsupported` -> **rejected** (`support_unsupported`); `partial` -> needs_review (`support_partial`); error -> needs_review.
6. Low extraction confidence -> needs_review (`low_extraction_confidence`).
`verified_auto` = every check passed. A person can set `approved` or `rejected` in `claim_review.csv` (column `decision`); decisions are re-applied on every build and survive reruns. Rejected claims are never deleted: they go to `rejected.jsonl`.

## Grouping
Public claims (verified_auto, approved) with the same gravity class, effect direction and first three variables are clustered by statement overlap (Jaccard of content words >= 0.5, single link). `group_id` = `G-` + hash of the key and the smallest member id. `independent_sources` = number of distinct `study_family` values among the members; the family is the document itself unless two documents report the same campaign (currently only the two BASS-II documents, NTRS 20210011385 and 20160000593). This count measures agreement across documents, not truth: a group with one source is a single report.

## Copyright display rule
`display_verbatim = yes` only for documents whose NTRS rights determination is `GOV_PUBLIC_USE_PERMITTED` (US Government work, public use permitted). For all other documents the UI shows the plain-language statement and a citation (title, year, NTRS id, PDF page, locator) and **never the verbatim span**; the span stays in the ledger for verification and the audit. `ledger/display.py` implements this (`public_view`) and is covered by tests. The assignment comes from NTRS metadata and still needs a person to confirm (open question on the status page).

## Limits of the checks
The checks prove that the quoted text exists, that the claim's numbers are in it and that a second model call judged it supported. They do not prove the paper is right, and the support check is an LLM judgement (hence the human audit of 30 claims).
