"""Writes data/llm/bass2_outcome_proposals.csv (decision D12).

The proposals below were made by Claude (model claude-sonnet-5-5, Claude Code session, 2026-10-19) by reading each
original Appendix A observation (data/transcribed/sidecars/bass2_observations.csv) against the rubric in
data/llm/README.md. They are PROPOSALS: the pipeline uses a class only after a human approves it in
data/review/outcome_review.csv. Run from the repo root: python scripts/bass2_outcome_proposals.py
"""
import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SE, ET, NI, BC, UK = 'self_extinguished', 'externally_terminated', 'no_ignition', 'burned_to_completion', 'unknown'
H, M, L = 'high', 'medium', 'low'
P = {  # test: (proposed class, confidence, rationale)
    'B1': (ET, M, 'operator turned the flow off after spread halfway, then the flame went out'),
    'B2': (UK, H, 'only equipment notes (no stills, cable)'), 'B3': (UK, H, 'oxygen and flame colour only'),
    'B4': (UK, H, 'bubble layer note only'), 'B5': (UK, H, 'repeat-test note and O2 reading only'),
    'B6': (BC, H, '"complete burnout" before reaching the next flow'), 'B7': (UK, H, 'bubble layer note only'),
    'B8': (UK, M, 'spread at 10 cm/s and no blowoff; the end state is not stated'),
    'B9': (SE, M, 'extinguished at pot 0.35 while stepping flow down (quench limit)'),
    'B10': (SE, M, 'extinguished at pot 0.35 (quench limit)'), 'B11': (SE, M, 'extinguished at pot 0.35 (quench limit)'),
    'B13': (SE, M, 'extinguished at pot 0.35 (quench limit)'), 'B12': (UK, H, 'flame colour only'),
    'B14': (SE, M, 'only brief ignition, flame extinguished (could be read as no sustained ignition)'),
    'B15': (UK, M, 'spread at 10 cm/s, no blowoff; end state not stated'),
    'B16': (SE, H, 'flame quenched after prolonged burn at 0.4 pot'),
    'B17': (SE, M, 'extinguished just as pot 0.4 was reached'),
    'B18': (SE, H, 'flame blew out at fan pot 7.0 (blowoff)'), 'B19': (SE, H, 'flame blew out at pot 6.0 (blowoff)'),
    'B20': (BC, H, 'flame burned entire sample'),
    'B21': (SE, M, 'flame goes out at 0.355 pot while flow was being turned down'),
    'B22': (SE, M, 'flow decreased in steps, flame out at the last step'),
    'F1': (SE, M, 'flame appeared briefly and went out while the igniter was still on'),
    'F2': (NI, L, '"flame would not sustain"; unclear whether a flame ever appeared'),
    'F3': (SE, L, 'brief ignition flash then no sustained flame (flame existed)'),
    'F4': (SE, M, 'blue flame, flow reduced in steps until the flame extinguished at 0.305'),
    'M1': (ET, H, 'flame put out by turning off the flow when the camera card ran out'),
    'M2': (SE, H, '"it self-extinguished"'), 'M3': (SE, M, 'extinguished at 18 cm/s'),
    'M4': (SE, M, 'flow stepped down to pot 0.3 where the flame extinguished (flow not zero)'),
    'M5': (SE, H, 'extinguished at 5 cm/s after prolonged flashing'),
    'M6': (UK, M, 'flame reached the end of the sample and spread along the edges; end state not stated'),
    'M7': (BC, H, 'burned entire sample after an 18 min burn'),
    'M8': (SE, M, 'flow turned down to extinguish; went out at pot 0.4 (flow not zero)'),
    'M9': (SE, H, 'died after 15 min at 14 cm/s'), 'M10': (SE, H, 'flame self-extinguished at 8 cm/s after almost 10 min'),
    'M11': (SE, M, 'extinguished at 12 cm/s'), 'M12': (UK, H, 'plateaus at pot settings only; no end state'),
    'M13': (SE, M, 'flow stepped down to pot 0.3 where the flame extinguished (flow not zero)'),
    'M14': (SE, H, 'flame self-extinguished at an air reading of 9 cm/s'),
    'M15': (SE, M, 'spreading and slow extinction at 15 cm/s'),
    'M16': (UK, L, 'burned at decreasing flow to the end of the sample; end state unclear'),
    'M17': (ET, M, 'finally turned the fan pot to 0 to extinguish'),
    'M18': (SE, M, 'extinguished at 8 cm/s after a 26 min burn'),
    'M19': (SE, H, 'went out on its own at 5 cm/s'), 'M20': (SE, H, 'flame out after 3 more minutes at 8 cm/s'),
    'O1': (UK, M, 'bracket test notes; rod broken off the holder during readjustment, no end state'),
    'O2': (UK, M, 'dim sooty flame and vapor jetting; no end state'),
    'O3a': (SE, M, 'flame extinguished as soon as the flow was turned down (possible overshoot)'),
    'O3b': (UK, H, 'flame appearance only'), 'O4': (SE, M, 'extinguished at 0.36 while decreasing flow'),
    'O5a': (SE, H, 'burned 9 min then blew out'), 'O5b': (NI, M, 'would not sustain a flame without the igniter on'),
    'O6': (UK, H, 'no observation text (dashes)'),
    'O7': (SE, H, 'blowoff at fan 97'), 'O8a': (SE, H, 'quench at pot 0.31'), 'O8b': (SE, H, 'blowoff at fan 78'),
    'O9': (SE, H, 'blowoff at fan 68'),
    'O10': (SE, H, 'leading edge blew out, rest of the flame blew off at maximum flow'), 'O11': (SE, H, 'blowoff at pot 6.0'),
    'O12': (NI, M, 'no sustained flame at any flow; flame only with the igniter'),
    'O13a': (SE, H, 'flame self-extinguished after 3+ min at pot 0.31'),
    'O13b': (SE, M, 'stayed lit less than a minute then went out'),
    'O14': (SE, M, 'slow pot decreases to the quenching pot 0.28'),
    'O15a': (SE, M, 'flow decreased to extinction at 0.32 pot'), 'O15b': (SE, H, 'decreased flow to extinction at 0.27 pot'),
    'O16': (SE, L, 'brief flame at the end of the first ignition, none sustained'),
    'O17': (SE, H, 'blowoff then extinguished even after the flow was reduced'),
    'O18': (SE, H, 'extinguished after multiple oscillations'),
    'O19': (SE, M, 'slow pot decreases to the quenching pot 0.288'),
    'O20': (UK, H, 'not found in Appendix A (decision D12: stays unknown)'),
    'O21': (UK, H, 'not found in Appendix A (decision D12: stays unknown)'),
    'O22': (UK, H, 'not found in Appendix A (decision D12: stays unknown)'),
    'P1': (SE, H, 'extinction at pot 0.315'),
    'P2': (ET, M, 'no extinction on the stills, but it was just fan off, not a slow ramp'),
    'P3a': (SE, M, 'extinguished at 0.3 pot, very small flame'),
    'P3b': (UK, H, 'spread at low pots and a camera power problem; no end state'),
    'P4': (ET, H, 'long slow burn, steady until the flow was turned off'),
    'P5': (ET, H, 'flame persisted at all pots; finally turned the flow down to 0 to extinguish'),
    'P6': (ET, H, 'steady burning until the flow was turned off'),
    'P8': (SE, L, '"would not stay lit"; unclear whether it ignited'),
    'P9': (SE, H, 'flame out at 0.28'), 'P10': (SE, H, 'finite quench at pot 0.3'),
    'P12': (SE, M, 'out immediately at 0.34 after oscillating at 0.36'),
    'P13a': (ET, M, 'flame out when the pot was turned to 0 (flow off)'),
    'P13b': (SE, M, 'flame out when the pot was turned to 0.32 (flow not zero)'),
    'P14': (SE, M, 'extinguished at 0.31'), 'P15': (UK, H, 'stable burn description only'),
    'P16': (SE, M, 'extinguished at pot 0.32'), 'P17': (SE, H, 'oscillated and went out at 0.34'),
    'P18': (SE, M, 'extinction at fan pot 0.32'), 'P19': (SE, M, 'flame out at 0.32, sample mostly gone'),
    'P20': (SE, M, 'extinction at fan pot 0.335'), 'P21a': (SE, H, 'flame self-extinguished at 5 cm/s'),
    'P21b': (NI, L, 'igniter broke after the third attempt; ignition not achieved'),
    'P22a': (SE, M, 'extinguished at a higher flow'), 'P22b': (SE, M, 'extinguished at a lower flow than P22a'),
    'P23': (SE, M, 'extinction at fan pot 0.38'), 'P24': (SE, M, 'extinction at fan pot 0.30'),
    'P25': (SE, M, 'extinguished at the 0.31 pot'),
    'T1': (UK, H, 'instrument notes only'), 'T2': (UK, H, 'flow changes only'),
    'T3': (SE, L, 'multiple ignition attempts, brief flames went out'),
    'T4': (SE, M, 'extinguished after turning into a flamelet'),
    'T5': (BC, M, 'seemed to burn the full sample length as a flamelet'),
    'T6': (UK, L, '"still did not extinguish" at the end; end state of the test unclear'),
    'T7': (SE, M, 'extinction finally at pot 0.28'),
    'T9': (SE, H, 'brief ignition, flame extinguished before spreading'),
    'T10': (SE, H, 'brief ignition, flame extinguished before spreading'),
    'T11': (BC, H, 'burned completely'), 'T12': (SE, M, 'extinguished quickly'),
    'T13': (SE, M, 'flame extinguished quickly after a flow change'),
    'T14': (SE, M, 'extinguished as the flow was reduced below 3 cm/s'),
    'T15': (UK, M, 'no blowoff attained; end state not stated'),
    'T16': (BC, M, 'flame spread the whole sample at 3 cm/s'),
    'T17': (UK, M, 'tried to blow off but did not; end state not stated'),
    'T18': (SE, H, 'brief ignition, extinguished as it spread away from the igniter'),
    'T19': (UK, M, 'steady burn; end state not stated'),
    'T20': (SE, M, 'quick extinction when the air was turned down to 3 cm/s'), 'T21': (SE, H, 'successful blowoff'),
    'T22': (SE, M, 'turned down to 5 and extinguished'), 'T23': (NI, H, 'did not ignite with the moved igniter'),
    'T24': (UK, M, 'steady spread of a one-sided flame; end state not stated'),
    'T25': (UK, H, 'flow plan only'), 'T26': (UK, H, 'flow plan only'), 'T27': (BC, M, 'fuel is burned out'),
    'T28a': (SE, L, 'flame only briefly flashed then went out'), 'T28b': (SE, L, 'flame only briefly flashed then went out'),
    'T29': (SE, M, 'flame went out after a few seconds following the pot change'),
}
MODEL = 'claude-sonnet-5-5 (Claude Code session)'


def main():
    obs = {r['test_id'].split(':')[1]: r for r in csv.DictReader(open(ROOT / 'data/transcribed/sidecars/bass2_observations.csv', encoding='utf-8'))}
    assert set(P) == set(obs), (set(obs) - set(P), set(P) - set(obs))
    out = ROOT / 'data/llm/bass2_outcome_proposals.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, lineterminator='\n')
        w.writerow(['test_id', 'observation_text', 'proposed_class', 'confidence', 'rationale', 'model', 'proposed_on', 'rubric_version', 'review_status'])
        for t, o in obs.items():
            c, cf, why = P[t]
            w.writerow([o['test_id'], o['observation_text'], c, cf, why, MODEL, '2026-10-19', 'bass2-outcome-rubric-v1', 'proposed'])
    review = ROOT / 'data/review/outcome_review.csv'
    review.parent.mkdir(parents=True, exist_ok=True)
    if not review.exists():  # never overwrite human decisions
        with open(review, 'w', newline='', encoding='utf-8') as f:
            csv.writer(f, lineterminator='\n').writerow(['test_id', 'decision', 'approved_class', 'reviewer', 'reviewed_on', 'note'])
    print(len(P), 'proposals;', dict(collections.Counter(v[0] for v in P.values())), dict(collections.Counter(v[1] for v in P.values())))


if __name__ == '__main__':
    main()
