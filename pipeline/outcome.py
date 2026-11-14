"""Outcome-class rules (docs/OUTCOME_MAPPING.md; decisions D5, D10, D11, D12, D14).

outcome_class is one of: no_ignition, self_extinguished, burned_to_completion, externally_terminated, other, unknown.
externally_terminated is a censored outcome and must never be treated as extinction.
"""


def flex_outcome(test_end_label):
    """FLEX outcome from the 'Test end' label (decision D22, which reverses D11).

    Extinction -> self_extinguished, Completion -> burned_to_completion, Disruption -> other; anything else unknown.
    The visible flame extinction diameter is used only for flex_label_diameter_disagree (a consistency check).
    """
    c = {'extinction': 'self_extinguished', 'completion': 'burned_to_completion', 'disruption': 'other'}.get((test_end_label or '').strip().lower())
    return (c, []) if c else ('unknown', [])


def flex_label_diameter_disagree(test_end_label, extinction_diameter_text):
    """True when the label and the visible flame extinction diameter disagree.

    The FLEX report legend (NTRS 20150023456 PDF p.25) defines the diameter as the droplet diameter when the visible flame
    extinguished and a dash as 'no extinction'. Expected: Extinction -> a positive diameter; Completion or Disruption ->
    no positive diameter. Rows where this fails are listed in docs/REVIEW_QUEUE.md; the label still decides the class.
    """
    lab = (test_end_label or '').strip().lower()
    try:
        positive = float((extinction_diameter_text or '').strip()) > 0
    except ValueError:
        positive = False
    if lab == 'extinction':
        return not positive
    if lab in ('completion', 'disruption'):
        return positive
    return False


def cfig_outcome(hot, end, burn_time_text, comment):
    """CFI-G rules (decision D10). Returns (class, flags).

    FT (flow terminated) -> externally_terminated: confirmed by Kim 2022 (UMD thesis), Table 4.1 note c.
    SE (self-extinguished, PSI column 'Self-ext or flow term') -> self_extinguished: consistent with the thesis'
    'RE' (radiatively extinguished) flames; the abbreviation SE itself is not defined there.
    Hot ignition = 'flash' is undocumented -> unknown. Comment-based decisions carry the flag class_from_comment.
    """
    hot = (hot or '').strip().lower()
    end = (end or '').strip()
    cm = (comment or '').strip().lower()
    flags = []
    if hot == 'flash':
        return 'unknown', ['hot_ignition_value_flash_undocumented']
    if end == 'SE':
        if 'hit burner t limit' in cm or 'manually stopped' in cm:
            return 'externally_terminated', ['label_conflict_SE_vs_comment', 'class_from_comment']
        return 'self_extinguished', flags
    if end == 'FT':
        if hot == 'no':
            flags.append('label_conflict_hot_ignition_no_but_burn_time_positive')
        return 'externally_terminated', flags
    if 'direct cool' in cm:
        return 'other', ['cool_flame_only', 'class_from_comment']
    if 'abort' in cm and 'did not ignite' not in cm:
        return 'other', ['aborted_comment', 'class_from_comment']
    if hot == 'no' and (burn_time_text or '').strip() in ('0', '0.0'):
        return 'no_ignition', []
    return 'unknown', []
