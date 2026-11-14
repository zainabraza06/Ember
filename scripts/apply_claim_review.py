"""Apply the AI-assisted claim triage and page checks, as accepted by the team reviewer, to data/review/claim_review.csv.

Inputs : data/CLAIM_TRIAGE_AI_SUGGESTIONS.csv, data/CLAIM_PAGE_CHECK_AI.csv (the page check wins over the triage), data/review/claim_review.csv,
         data/ledger/claims.jsonl + pages.jsonl (for the span / number / condition re-check of every corrected statement).
Output : data/review/claim_review.csv (decision, reviewer, reviewed_on, note, corrected statement, gravity label), and a printed list
         of claims that went back to needs_review. Then run `python -m ledger all --offline --skip-pilot` to rebuild the ledger.
Only claims listed in the triage file are touched. Spans are never changed.
"""
import csv
import json
import sys
from collections import Counter

sys.path.insert(0, '.')
from ledger.verify import check_conditions, check_numbers, check_span  # noqa: E402

REVIEWER = 'Zainab Raza (accepted AI-assisted review)'
DATE = '2026-11-14'
STAMP = 'AI-assisted check, accepted by reviewer'
SIM = 'simulated partial gravity (centrifuge, about 0.165 g)'

# corrected statements (rule 1: 'correct' -> approved with the corrected statement; the span is not changed)
CORRECT = {
    'C-02500f147f': 'For SIBAL fabric in the Earth-gravity run, the flame width decreases suddenly at about 24 seconds and goes to 0 within 4 seconds.',
    'C-8fcadabed7': 'For PMMA in the Earth-gravity run, the flame tip grows at approximately 3.95 mm/s at the beginning of the burn.',
    'C-6d3837e628': 'For PMMA in the Earth-gravity run, the oxygen concentration decreases approximately linearly from 21% to 14.5% after an initial rise.',
    'C-fa0a7b71dc': 'For PMMA in simulated partial gravity, the flame spread rate increases linearly from 0 to about 0.6 mm/s (before gravity starts dropping at t = 125 s).',
    'C-f89589a019': 'The information obtained so far indicates there is insignificant difference in the oxygen concentration flammability thresholds when comparing 1/8-in. diameter rods with ½-in. wide samples.',
    'C-0f4421dc5a': 'In combination with the fire-stop effect (the other factor discussed in the preceding text), a double-rolled hem increases MOC by one percent.',
    'C-6b7ea209e9': 'Initially the flame length fluctuated at about 1.4 Hz before becoming more stable at about 90 s.',
    'C-b0dcad8095': 'The average flame spread rate is 1.8 mm/s and the estimated average flame power is 1200 +/- 300 W.',
    'C-d46357f38e': 'The flame spread rate for the 5-cm-wide sample is marginally faster than for the 40.6-cm-wide sample at the same flow speed of 20 cm/s (2.1 compared to 1.8 mm/s).',
    'C-d4455b6a17': 'On Earth, this Nomex fabric will only burn if the oxygen concentration is increased to around 24 to 25%.',
    'C-3974b3d708': 'The 7-g fuel mass loss test had over 1,000 ppm of CO (above the range of the sensor).',
    'C-3a96923cb6': 'Steady spread over thin fuels in a perfectly quiescent environment has been established at higher O2 levels (Ref. 11), per the authors\' cited prior work.',
    'C-9db4b0d369': 'An average value of 0.044 mm/s is selected as the average spread rate for downward spread over PMMA in the thick limit.',
    'C-d63a1d6943': 'The transition thickness for downward flame spread in ambient air is calculated to be 5.19 mm.',
    'C-4739e34e6c': 'For the conditions tested, sustained flame spread was not observed for opposed-flow velocities below approximately 4 mm/s for the 0.00635- and 0.009525-m-diameter PMMA rods.',
    'C-f889b68102': 'In the tested conditions, flame spread rate increases with increasing O2 concentration, especially for the 6.35-mm-diameter rods.',
    'C-d886e8265f': 'The authors interpret this second blowoff as indicating that, at the low O2 levels tested (14.5 percent in this test), a flame stabilized farther than 2 mm downstream of the stagnation region is unable to repropagate upstream even though the fuel is already preheated.',
    'C-b29b263d04': 'The minimum in the flammability boundary occurs at approximately 13.5 percent O2, at stretch rates of 8 to 12 per second.',
    'C-dc08111531': 'In Saffire V-3, run at enhanced oxygen, the final flame length was greater than for the other samples.',
    'C-e1653ca2f6': 'In Saffire V-3, the one-sided PMMA sample flame in 25.4% oxygen grew to 11 cm after 450 seconds.',
    'C-aff4bc0482': 'Increasing the flow velocity is likely to decrease the ignitability of the fuel.',
    'C-3a58e8c51e': 'A typical alarm threshold for smoke detection was achieved only at 981 seconds.',
    'C-e8b3564fc1': 'At all tested thicknesses, the fuel can be considered thermally thin because the maximum spread rate was found to be inversely proportional to fuel thickness (Ref. 1), a hallmark of a thermally thin regime.',
    'C-cbca12ebcd': 'In limited tests on MQ (0.25 in. thick), material durometer did not significantly affect the oxygen flammability thresholds (Table 4, NTRS 20110008636 p5).',
    # decided by the page check (it wins over the triage):
    'C-f4d3c81aef': 'At a gravity level of 0.10 G, the model predicted extinction at 0.12 atm pressure, lower than the experiments indicated (model prediction).',
    'C-2eef8a9583': 'The fire experiments reported heat release rates up to 10 kW without the average vehicle conditions rising to unacceptable levels.',
    'C-b58d0b48b6': 'Most of the data show a CO to CO2 ratio well above 0.004, the reference value for efficiently burned flue gases in boilers and furnaces, indicating that microgravity flames are comparatively inefficient.',
}
GRAVITY_CLASS = {'C-424fca9292': 'not_stated'}   # method claim about tracking
MANUAL_OVERRIDE = {'C-cbca12ebcd': "AI page-image check: Table 4 is MQ, 0.25 in. thick, durometers 30 to 70. The material, thickness and citation numbers in the corrected statement come from Table 4 and the citation, not from the span.",
                   'C-f4d3c81aef': "Span OCR is garbled ('0. I0 G'). Page image checked by AI, text reads: at 0.10 G the model predicted extinction at 0.12 atm, lower than the experiments indicated. Label: model prediction."}
PAGE_NOTE = {'C-e8b3564fc1': 'Kept on PDF page 21 (the same sentence also appears on PDF page 31, so 21 is correct). Triage wording "at all tested thicknesses" used.'}
SIM_LABEL = ['C-6a444e61aa', 'C-c6eb6afcd0', 'C-2171da5d6d', 'C-9571d561f4', 'C-41d4bddb09', 'C-fa0a7b71dc']   # LUCI partial-gravity run slides
SIM_CLASS = 'partial_other'
KEEP_OPEN = {}
LUCI_SLIDE = ('Slide text read in the page text: slides are titled "LUCI: ..." and p24 refers to "partial-g burn", p40 "LUCI Partial-G Recap", '
              'p22/p43 say gravity drops at t = 125 s. Simulated lunar gravity by centrifuge (11 RPM, 1.22 m radius, about 0.165 g); label as simulated partial gravity, not "on the Moon".')


def main():
    tri = {r['claim_id']: r for r in csv.DictReader(open('data/CLAIM_TRIAGE_AI_SUGGESTIONS.csv', encoding='utf-8-sig'))}
    chk = {r['claim_id']: r for r in csv.DictReader(open('data/CLAIM_PAGE_CHECK_AI.csv', encoding='utf-8-sig')) if r['claim_id'].startswith('C-')}
    claims = {c['claim_id']: c for c in map(json.loads, open('data/ledger/claims.jsonl', encoding='utf-8'))}
    pages = {}
    for line in open('data/ledger/pages.jsonl', encoding='utf-8'):
        p = json.loads(line)
        pages.setdefault(p['doc_id'], {})[p['page']] = p['text']
    with open('data/review/claim_review.csv', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    fields = ['claim_id', 'doc_id', 'page', 'reasons', 'gravity_class', 'statement', 'span', 'decision', 'reviewer', 'reviewed_on', 'note', 'original_statement', 'gravity_label']
    went_back, tally, overrides = [], Counter(), []
    for r in rows:
        cid = r['claim_id']
        if cid not in tri:
            continue                                   # rule 5: untouched
        c, t, k = claims[cid], tri[cid], chk.get(cid)
        action = t['ai_suggested_action']
        triage_note = t['what_to_check_or_change']
        if k:
            note = f"{STAMP}. Page check ({k['source']}): {k['ai_page_check_result']}. {k['evidence_note']}"
        elif cid in SIM_LABEL or cid in ('C-02500f147f', 'C-9ba619935b', 'C-8fcadabed7', 'C-6d3837e628'):
            note = f"{STAMP}. Page check (NTRS 20250010653 p{c['page']}): {LUCI_SLIDE}"
        else:
            note = f"{STAMP}. No claim-specific page check on file; triage only: {triage_note or 'approve, no issue listed'}"
        if cid in PAGE_NOTE:
            note += ' ' + PAGE_NOTE[cid]
        r['original_statement'] = ''
        r['gravity_label'] = ''
        if cid in KEEP_OPEN:
            r.update(decision='', reviewer='', reviewed_on='', note=f"{STAMP}. {KEEP_OPEN[cid]}")
            went_back.append((cid, 'kept needs_review (your exception / page conflict)', KEEP_OPEN[cid]))
            tally['needs_review'] += 1
            continue
        decision, corrected = 'approved', False
        if action == 'reject':
            decision = 'rejected'
        elif cid in CORRECT:
            corrected = True
            new = CORRECT[cid]
            sp = check_span(c['span'], c['page'], pages[c['doc_id']])
            nm = check_numbers([new, c['magnitude_text']], c['span'])
            cd = check_conditions(c['conditions'], c['span'])
            bad = []
            if sp['result'] != 'exact' or sp['page'] != c['page']:
                bad.append(f"span {sp['result']}")
            if nm['result'] != 'pass':
                bad.append(f"numbers not in span: {nm['missing']}")
            if cd['result'] != 'pass':
                bad.append(f"condition values not in span: {cd['fields']}")
            if bad and cid in MANUAL_OVERRIDE:
                note = f"{STAMP}. MANUAL OVERRIDE of the code check ({'; '.join(bad)}); this is NOT a passed check. {MANUAL_OVERRIDE[cid]}"
                r['original_statement'] = c['statement']
                overrides.append((cid, bad))
            elif bad:
                decision = ''
                went_back.append((cid, 'back to needs_review: ' + '; '.join(bad), new))
            else:
                r['original_statement'] = c['statement']
            r['statement'] = new
        elif action == 'correct' and cid in GRAVITY_CLASS:
            corrected = True                           # correction is the gravity class only; statement unchanged
        elif action == 'correct':
            raise SystemExit(f'{cid}: triage says correct but no corrected statement defined')
        if cid in GRAVITY_CLASS and decision == 'approved':
            r['gravity_class'] = GRAVITY_CLASS[cid]
            note += ' Gravity class set to not_stated (method claim).'
        if cid in SIM_LABEL and decision == 'approved':
            r['gravity_class'] = SIM_CLASS
            r['gravity_label'] = SIM
        if decision == '':                              # failed re-check: keep original statement, mark open
            r['statement'] = c['statement']
            r['note'] = f"{STAMP}. Corrected statement failed the code re-check ({went_back[-1][1]}); kept as needs_review. Proposed wording: {CORRECT[cid]} | {note}"
            r.update(decision='', reviewer='', reviewed_on='')
            tally['needs_review'] += 1
            continue
        r.update(decision=decision, reviewer=REVIEWER, reviewed_on=DATE, note=note)
        tally['rejected' if decision == 'rejected' else ('approved_with_correction' if corrected else 'approved')] += 1
    with open('data/review/claim_review.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        w.writerows(rows)
    print(dict(tally), sum(tally.values()))
    for cid, bad in overrides:
        print(f'MANUAL OVERRIDE {cid}: {bad}')
    for cid, why, txt in went_back:
        print(f'\n{cid}: {why}\n   {txt}')


if __name__ == '__main__':
    main()
