# LLM-proposed outcome classes (decision D12)

`bass2_outcome_proposals.csv` holds, for each BASS-II test, the original Appendix A observation (NTRS 20210011385) and a **proposed** `outcome_class` with a confidence and a one-line rationale. The proposals were made by Claude (model `claude-sonnet-5-5`, Claude Code session, 2026-10-19) reading each observation against the rubric below; the file is written by `scripts/bass2_outcome_proposals.py`.

They are **proposals only**. The pipeline uses a class downstream only after a human approves it in `data/review/outcome_review.csv` (columns: `test_id`, `decision` = approved | rejected | changed, `approved_class`, `reviewer`, `reviewed_on`, `note`). Until then every BASS-II row has `outcome_class = unknown`; the proposal and its confidence are stored in `outcome_class_proposed`, `outcome_proposal_confidence` and `outcome_review_status = proposed`. `docs/REVIEW_QUEUE.md` lists every proposal for review.

Rubric (version `bass2-outcome-rubric-v1`):
- `no_ignition`: the text says the sample did not ignite, or no flame could be sustained and no flame is described.
- `self_extinguished`: a flame existed and went out while the flow was still on, including blowoff, quench limits found by stepping the flow down (flow not zero), and brief flames that died. Extinction at a non-zero reduced flow counts as a measured limit.
- `burned_to_completion`: the text says the sample burned entirely or completely.
- `externally_terminated`: the operator ended the burn while the flame was still burning or by switching the flow off or to zero (also running out of camera card, loss of signal). Censored: not an extinction.
- `other`: procedure or equipment issue that makes none of the above clear.
- `unknown`: the text has no outcome (appearance, instrument or oxygen notes only, no end state, or no text).

Confidence: `high` = the text states the end state plainly; `medium` = the end state is stated but needs an interpretation (for example extinction while the flow was being reduced); `low` = the text is ambiguous.
