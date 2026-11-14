"""Mapping of the approved PSI tables (decisions D1, D13) to the unified schema.

Each build_* function returns (rows, notes). A row is a dict with the columns of schema.COLUMNS.
Rules follow docs/DATA_DICTIONARY.md section 3 and docs/OUTCOME_MAPPING.md. PSI-10 is excluded (D6); PSI-26 (BASS)
is not part of the structured table (D13) and is used only by the evidence ledger.
"""
import collections
import csv
import re

from .common import (KPA_PER_BAR, KPA_PER_MMHG, MM_PER_CM, RAW_PSI, ROOT, Rec, RowBuilder, parse_float, parse_with_unit,
                     read_records, source_ref)
from .materials import normalize_material
from .outcome import cfig_outcome, flex_label_diameter_disagree, flex_outcome

SIDECARS = ROOT / 'data' / 'transcribed' / 'sidecars'
LLM = ROOT / 'data' / 'llm'
REVIEW = ROOT / 'data' / 'review'


def _one(pattern):
    hits = sorted(RAW_PSI.glob(pattern))
    if len(hits) != 1:
        raise FileNotFoundError(f'expected exactly one file for {pattern}, found {hits}')
    return hits[0]


def _sidecar(path, key='test_id'):
    with open(path, newline='', encoding='utf-8') as f:
        return {r[key]: r for r in csv.DictReader(f)}


def _o2_pct(b, field, text, column):
    """Percent-by-volume cell -> mole fraction (ideal gas: vol% / 100)."""
    v = parse_float(text)
    if v is None:
        b.flag(f'text_not_numeric:{field}' if text.strip() else f'missing_value:{field}')
        return
    b.set(field, v / 100.0, orig_text=text, column=column, unit='vol%')


# ----------------------------------------------------------------------------- FLEX (PSI-69)
def build_flex():
    path = _one('PSI-69/*FLEX.csv')
    header, recs = read_records(path)
    ids = collections.Counter(Rec(header, c).get('FLEX Identifier') for _, c in recs)
    rows, dropped = [], 0
    for n, cells in recs:
        r = Rec(header, cells)
        if r.empty():
            dropped += 1
            continue
        num = r.get('FLEX Test #')
        b = RowBuilder(test_id=f'PSI-69:{int(num):03d}', family='FLEX', psi_id='PSI-69', platform='ISS-CIR/MDCA',
                       gravity_level_g='0', gravity_source='nominal', material_or_fuel=r.get('Fuel'),
                       material_class='liquid_droplet', sample_geometry='droplet', source_ref=source_ref(path, n),
                       flow_direction='quiescent')
        b.flag('flow_direction_assumed_quiescent')
        pt = r.get('Ambient pressure; mmHg')
        p = parse_float(pt)
        if p is None or p <= 0:
            b.flag('missing_value:pressure_kpa')
            b.orig['pressure_kpa'] = {'value': pt, 'column': 'Ambient pressure; mmHg', 'unit': 'mmHg'}
        else:
            b.set('pressure_kpa', round(p * KPA_PER_MMHG, 4), orig_text=pt, column='Ambient pressure; mmHg', unit='mmHg')
        b.f['pressure_orig'] = f'{pt} mmHg' if pt else ''
        # columns O, N, CO, He are O2, N2, CO2, He (confirmed by NTRS 20150023456 Table IX)
        comp = {}
        for key, col in (('O2', 'O initial ambient composition; mole fraction'), ('N2', 'N initial ambient composition; mole fraction'),
                         ('CO2', 'CO initial ambient composition; mole fraction'), ('He', 'He initial ambient composition; mole fraction')):
            v = parse_float(r.get(col))
            if v is None:
                b.flag(f'missing_value:composition_{key}')
            else:
                comp[key] = v
        o2 = parse_float(r.get('O initial ambient composition; mole fraction'))
        if o2 is not None:
            b.set('oxygen_fraction', o2, orig_text=r.get('O initial ambient composition; mole fraction'),
                  column='O initial ambient composition; mole fraction', unit='mole fraction')
            b.f['oxygen_orig'] = r.get('O initial ambient composition; mole fraction')
        b.f['diluent'] = ';'.join(f'{k}={v:g}' for k, v in comp.items() if k != 'O2')
        if comp and not 0.97 <= sum(comp.values()) <= 1.01:  # the report also lists vapor species, so < 1 is normal
            b.flag('composition_sum_off')
        # outcome: the "Test end" label (D22); the extinction diameter is only a consistency check
        dx = r.get('Visible flame extinction diameter; mm')
        end = r.get('Test end')
        cls, fl = flex_outcome(end)
        b.f['outcome_raw'] = end
        b.f['outcome_class'] = cls
        b.flag(*fl)
        if flex_label_diameter_disagree(end, dx):
            b.flag('diameter_label_disagree')
        b.orig['outcome_class'] = {'value': end, 'column': 'Test end'}
        bt = r.get('Burn time; s')
        v = parse_float(bt)
        if v is None:
            b.flag('missing_value:burn_duration_s')
        else:
            b.set('burn_duration_s', v, orig_text=bt, column='Burn time; s', unit='s')
        b.x('cir_identifier', r.get('FLEX Identifier'))
        if ids[r.get('FLEX Identifier')] > 1:
            b.flag('duplicate_identifier')
        b.x('test_date', r.get('Test Date'))
        b.x('test_time_gmt', r.get('Test GMT'))
        b.x('droplet_initial_diameter_mm', r.get('Droplet initial diameter; mm'))
        b.x('extinction_diameter_mm', dx)
        b.x('burning_rate_mm2_s', r.get('Burning rate; mm'))  # header says mm; report Table IX says mm2/s
        if parse_float(r.get('Droplet initial diameter; mm')) is None:
            b.flag('missing_value:droplet_initial_diameter_mm')
        rows.append(b.row())
    return rows, {'file': str(path.name), 'records': len(recs), 'dropped_empty': dropped}


# ----------------------------------------------------------------------------- CFI-G (PSI-159)
def build_cfig():
    rows, info = [], {}
    for kind in ('Normal', 'Inverse'):
        path = _one(f'PSI-159/*{kind}*.csv')
        header, recs = read_records(path)
        k = kind.lower()
        dropped = 0
        for n, cells in recs:
            r = Rec(header, cells)
            if r.empty():
                dropped += 1
                continue
            test = r.get('Test').replace(' ', '')
            b = RowBuilder(test_id=f'PSI-159:{k}:{test}', family='CFI-G', psi_id='PSI-159', platform='ISS-CIR/ACME',
                           gravity_level_g='0', gravity_source='nominal', material_or_fuel=r.get('Fuel'),
                           material_class='gas_fuel', source_ref=source_ref(path, n))
            b.x('flame_type', r.get('Flame Type'))
            b.x('day_raw', r.get('Day'))  # metadata column, not an outcome (D10)
            b.x('test_label_original', r.get('Test'))
            pt = r.get('approx p (bar)')
            p = parse_float(pt)
            if p is None:
                b.flag('missing_value:pressure_kpa')
            else:
                b.set('pressure_kpa', round(p * KPA_PER_BAR, 4), orig_text=pt, column='approx p (bar)', unit='bar')
                b.flag('approximate_value')
            b.f['pressure_orig'] = f'{pt} bar' if pt else ''
            if kind == 'Normal':
                o_b, o_a = r.get('XO2 before test'), r.get('XO2 after test')
                for fld, txt, col in (('oxygen_fraction', o_b, 'XO2 before test'), ('oxygen_fraction_final', o_a, 'XO2 after test')):
                    v = parse_float(txt)
                    if v is not None:
                        b.set(fld, v, orig_text=txt, column=col, unit='mole fraction')
                    else:
                        b.flag(f'missing_value:{fld}')
                b.f['oxygen_orig'] = o_b
                b.x('cool_flame_raw', r.get('Cool flame?'))  # PCI-A..G codes: metadata, not outcomes (D10)
                b.x('fuel_mole_fraction', r.get('Xf'))
                b.x('hc_flow_mg_s', r.get('mHC (mg/s)'))
                b.x('peak_burner_temp_c', r.get('Peak burner T (C )'))
            else:
                txt = r.get('XO2')
                v = parse_float(txt)
                if v is not None:
                    b.set('oxygen_fraction', v, orig_text=txt, column='XO2', unit='mole fraction')
                else:
                    b.flag('missing_value:oxygen_fraction')
                b.f['oxygen_orig'] = txt
                b.x('fuel_mole_fraction_before', r.get('Xf before test'))
                b.x('fuel_mole_fraction_after', r.get('Xf after test'))
                b.x('hc_flow_mg_s', r.get('HC burnrate (mg/s)'))
                b.x('o2_flow_mg_s', r.get('O2 flow rate (mg/s)'))
                b.x('peak_burner_temp_c', r.get('Peak burner Temp (C)'))
                b.x('peak_burner_temp_k', r.get('Peak burner temp (K)'))
                b.x('color', r.get('Color'))
            b.x('tfp_raw', r.get('TFP'))  # TFP = thin filament pyrometry (NTRS 20210021781); not an outcome (D10)
            b.x('tad_k', r.get('Tad (K)'))
            b.x('zst', r.get('Zst'))
            hot = r.get('Hot ignition')
            end = r.get('Self -ext or flow term') if r.has('Self -ext or flow term') else r.get('Self-ext or flow term')
            bt = r.get('burn time (sec)')
            comment = r.get('Comments')
            b.x('hot_ignition_raw', hot)
            b.x('comments', comment)
            v = parse_float(bt)
            if v is None:
                b.flag('missing_value:burn_duration_s')
            else:
                b.set('burn_duration_s', v, orig_text=bt, column='burn time (sec)', unit='s')
            b.f['outcome_raw'] = f'end={end or "(blank)"}; hot_ignition={hot or "(blank)"}'
            cls, fl = cfig_outcome(hot, end, bt, comment)
            b.f['outcome_class'] = cls
            b.flag(*fl)
            rows.append(b.row())
        info[kind] = {'file': path.name, 'records': len(recs), 'dropped_empty': dropped}
    return rows, info


# ----------------------------------------------------------------------------- BASS-II (PSI-25)
def _apply_material(b, text):
    m = normalize_material(text)
    b.f['material_class'] = m['material_class']
    b.f['sample_geometry'] = m['geometry']
    if m['thickness_mm'] is not None:
        b.set('sample_thickness_mm', round(m['thickness_mm'], 4), orig_text=text, column='Fuel Sample Material', unit='parsed from text')
    if m['width_cm'] is not None:
        b.set('sample_width_cm', m['width_cm'], orig_text=text, column='Fuel Sample Material', unit='parsed from text')
    b.flag(*[f'material_{x}' if not x.startswith('material_') else x for x in sorted(m['flags'])])
    for k, v in m['ext'].items():
        b.x(k, v)


def _load_review():
    path = REVIEW / 'outcome_review.csv'
    if not path.exists():
        return {}
    with open(path, newline='', encoding='utf-8') as f:
        return {r['test_id']: r for r in csv.DictReader(f) if r.get('decision')}


def build_bass2():
    path = _one('PSI-25/*.csv')
    header, recs = read_records(path)
    obs = _sidecar(SIDECARS / 'bass2_observations.csv')
    props = _sidecar(LLM / 'bass2_outcome_proposals.csv')
    t51 = _sidecar(SIDECARS / 'bass2_table5_1.csv')
    press = _sidecar(SIDECARS / 'bass2_pressure_statements.csv')
    review = _load_review()
    rows, dropped = [], 0
    stats = collections.Counter()
    for n, cells in recs:
        r = Rec(header, cells)
        if r.empty():
            dropped += 1
            continue
        tid = f'PSI-25:{r.get("Test #")}'
        b = RowBuilder(test_id=tid, family='BASS-II', psi_id='PSI-25', platform='ISS-MSG', gravity_level_g='0',
                       gravity_source='nominal', material_or_fuel=r.get('Fuel Sample Material'), source_ref=source_ref(path, n))
        _apply_material(b, r.get('Fuel Sample Material'))
        _o2_pct(b, 'oxygen_fraction', r.get('Calibrated initial O2 % by vol'), 'Calibrated initial O2 % by vol')
        _o2_pct(b, 'oxygen_fraction_final', r.get('Calibrated final O2 % by vol'), 'Calibrated final O2 % by vol')
        b.f['oxygen_orig'] = r.get('Calibrated initial O2 % by vol')
        for k, col in (('pi', 'PI'), ('test_date', 'Date'), ('gmt_day', 'GMT'), ('sample_number', 'Sample #'),
                       ('flow_restrictor_code', 'Flow restrictor'), ('fan_display', 'Fan display'), ('air_display_raw', 'Air display'),
                       ('radiometer_gain', 'Radiometer gain (1000 250 50 10)'), ('frames_shot', 'Total Frames Shot'),
                       ('co2_initial_vol_pct', 'Initial CO2 % by vol'), ('co2_final_vol_pct', 'Final CO2 % by vol'),
                       ('co_initial_ppm', 'Initial CO (ppm)'), ('co_final_ppm', 'Final CO (ppm)')):
            b.x(k, r.get(col))
        # --- pressure: only where the report text states it (D12)
        if tid in press:
            s = press[tid]
            b.set('pressure_kpa', float(s['pressure_kpa']), orig_text=s['pressure_orig'], unit='atm')
            b.orig['pressure_kpa'].update(origin='transcribed_from_text', source=s['source_ref'], converted='atm to kPa')
            b.f['pressure_orig'] = s['pressure_orig']
            b.flag('nominal')
            b.x('pressure_statement_scope', s['statement_scope'])
            stats['pressure_filled'] += 1
        else:
            b.flag('missing_value:pressure_kpa')
        # --- numeric flow only for the 20 Table 5.1 tests (D12); codes stay raw elsewhere
        flow_filled = False
        if tid in t51:
            t = t51[tid]
            vels = [v for v in t['velocity_cm_s_list'].split(';') if v]
            b.x('table_5_1', {k: t[k] for k in ('thickness_mm', 'width_cm', 'sides_burning', 'velocity_cm_s_list', 'spread_rate_mm_s_text',
                                                 'burn_time_min', 'initial_o2_vol_pct', 'final_o2_vol_pct')})
            b.x('table_5_1_source', t['source_ref'])
            if len(vels) == 1:
                b.set('flow_velocity_cm_s', float(vels[0]), orig_text=vels[0], column='Velocity, cm/s (Table 5.1)', unit='cm/s')
                b.orig['flow_velocity_cm_s'].update(origin='transcribed_from_table', source=t['source_ref'])
                flow_filled = True
            else:
                b.x('flow_velocity_steps_cm_s', ';'.join(vels))
                b.flag('multiple_flow_steps')
            o2i = parse_float(r.get('Calibrated initial O2 % by vol'))
            if o2i is not None and abs(o2i - float(t['initial_o2_vol_pct'])) > 0.05:
                b.flag('table_5_1_o2_differs_from_psi')
            stats['table_5_1'] += 1
        if not flow_filled:
            b.flag('flow_codes_undecoded')
        # --- outcome: original observation text; LLM proposal; human review (D12)
        o = obs.get(tid)
        text = o['observation_text'] if o else ''
        b.f['outcome_raw'] = text
        if o and o['source_ref'].startswith('NTRS'):
            b.x('observation_source', o['source_ref'])
        if not text:
            b.flag('outcome_not_in_appendix_a')
        pr = props[tid]
        b.f['outcome_class_proposed'] = pr['proposed_class']
        b.f['outcome_proposal_confidence'] = pr['confidence']
        b.f['outcome_review_status'] = 'not_applicable' if not text else 'proposed'
        b.x('outcome_proposal_rationale', pr['rationale'])
        b.x('outcome_proposal_model', pr['model'])
        rv = review.get(tid)
        if rv and text:
            dec = rv['decision'].strip().lower()
            if dec == 'approved':
                b.f['outcome_class'] = pr['proposed_class']
            elif dec == 'changed':
                b.f['outcome_class'] = rv['approved_class']
            b.f['outcome_review_status'] = dec if dec in ('approved', 'rejected', 'changed') else 'proposed'
            stats['reviewed'] += 1
        rows.append(b.row())
    return rows, {'file': path.name, 'records': len(recs), 'dropped_empty': dropped, **dict(stats)}


# ----------------------------------------------------------------------------- Saffire I-III (PSI-98, 99, 100)
def _len_cm(b, field, text, column, default_unit='cm'):
    v, u = parse_with_unit(text, ('cm', 'mm'))
    if v is None:
        if text.strip():
            b.flag(f'text_not_numeric:{field}')
        return
    u = u or default_unit
    if u == 'mm':
        b.set(field, v / 10.0, orig_text=text, column=column, unit='mm')
    else:
        b.set(field, v, orig_text=text, column=column, unit='cm')


def _thick_mm(b, text, column, default_unit, corrected_mm=None):
    t = text.strip()
    if re.fullmatch(r'0\d{2,}\s*mm', t, flags=re.I):  # "037 mm": the decimal point is missing
        if corrected_mm is None:
            b.flag('value_typo_suspected')
            b.orig['sample_thickness_mm'] = {'value': text, 'column': column, 'unit': 'mm'}
            return
        b.set('sample_thickness_mm', corrected_mm, orig_text=text, column=column, unit='mm')
        b.orig['sample_thickness_mm'].update(corrected_value=f'{corrected_mm:g}', origin='transcribed_from_table', source=REPORT_REF)
        b.flag('corrected_from_report')
        return
    v, u = parse_with_unit(t, ('cm', 'mm'))
    if v is None:
        if t:
            b.flag('text_not_numeric:sample_thickness_mm')
            b.orig['sample_thickness_mm'] = {'value': text, 'column': column}
        return
    u = u or default_unit
    b.set('sample_thickness_mm', v * (MM_PER_CM if u == 'cm' else 1.0), orig_text=text, column=column, unit=u)


def _o2_text(b, text, column):
    t = text.strip()
    b.f['oxygen_orig'] = t
    m = re.fullmatch(r'(~\s*)?(\d+(?:\.\d+)?)', t)
    if m:
        b.set('oxygen_fraction', float(m.group(2)) / 100.0, orig_text=text, column=column, unit='vol%')
        if m.group(1):
            b.flag('oxygen_approximate')
    elif t:
        b.flag('text_range_not_parsed:oxygen_fraction')
    else:
        b.flag('missing_value:oxygen_fraction')


def _flow(b, text, column):
    v, u = parse_with_unit(text, ('cm/s',))
    if v is None:
        b.flag('missing_value:flow_velocity_cm_s')
        return
    b.set('flow_velocity_cm_s', v, orig_text=text, column=column, unit='cm/s')


def _burn(b, text, column):
    v, u = parse_with_unit(text, ('s',))
    if v is None:
        b.flag('missing_value:burn_duration_s' if not text.strip() else 'text_not_numeric:burn_duration_s')
        if text.strip():
            b.orig['burn_duration_s'] = {'value': text, 'column': column}
        return
    b.set('burn_duration_s', v, orig_text=text, column=column, unit='s')


def _saffire_rows(glob):
    path = _one(glob)
    header, recs = read_records(path)
    out, dropped, nontest = [], 0, 0
    for n, cells in recs:
        r = Rec(header, cells)
        if r.empty():
            dropped += 1
            continue
        sid = r.get('Sample Number')
        if re.match(r'^(F\d|Note)', sid):
            nontest += 1
            continue
        out.append((n, r, sid))
    return path, out, dropped, nontest


# NTRS 20170008805 slide 29, Table I (Saffire results presentation) reproduces the Saffire-I and II tables.
# Decision D24: clear errors are corrected and flagged corrected_from_report; genuine conflicts keep the PSI value, put the
# report value in alt_value_report and flag source_conflict (listed in docs/CONFLICTS.md).
REPORT_REF = 'NTRS 20170008805, slide 29, Table I (Saffire results presentation)'
SAFFIRE2_THICKNESS_FIX = {'2-4': 0.37, '2-5': 0.37, '2-6': 0.37}   # PSI cell reads "037 mm"; report: 0.37 mm
SAFFIRE2_MATERIAL_FILL = {'2-6': ('Cotton-Fiberglass', 'fabric'), '2-9': ('PMMA', 'unknown')}  # blank in PSI-99
SAFFIRE2_FLOW_CONFLICT = {'2-6': ('flow_velocity_cm_s', '25 cm/s')}   # PSI 20 cm/s, report 25 cm/s


def build_saffire():
    rows, info = [], {}
    # ---- Saffire-I (PSI-98)
    path, recs, dropped, nontest = _saffire_rows('PSI-98/*.csv')
    for n, r, sid in recs:
        b = RowBuilder(test_id=f'PSI-98:{sid}', family='Saffire', psi_id='PSI-98', platform='Cygnus (Saffire-1 enclosure)',
                       gravity_level_g='0', gravity_source='nominal', material_or_fuel=r.get('Material'), material_class='fabric',
                       source_ref=source_ref(path, n))
        b.flag('missing_value:pressure_kpa')
        _thick_mm(b, r.get('Sample Thickness (cm)'), 'Sample Thickness (cm)', 'cm')
        # PSI-98 lists length 40.6 and width 94; the report (and PSI-100) give width 40.6 cm and length 94 cm: swapped back (D24)
        _len_cm(b, 'sample_length_cm', r.get('Sample Width (cm)'), 'Sample Width (cm)')
        _len_cm(b, 'sample_width_cm', r.get('Sample Length (cm)'), 'Sample Length (cm)')
        for fld in ('sample_length_cm', 'sample_width_cm'):
            b.orig[fld].update(corrected_value=b.f[fld], origin='transcribed_from_table', source=REPORT_REF)
        b.flag('corrected_from_report')
        b.x('correction_note', f'{REPORT_REF}: width 40.6 cm and length 94 cm; the PSI-98 length and width cells are swapped')
        _flow(b, r.get('Air Flow (cm/s)'), 'Air Flow (cm/s)')
        _o2_text(b, r.get('Percent O2'), 'Percent O2')
        b.f['flow_direction'] = r.get('Flow Direction').strip().lower() or 'unknown'
        _burn(b, r.get('Burn Time (s)'), 'Burn Time (s)')
        b.f['outcome_raw'] = f"burn_time={r.get('Burn Time (s)')}"
        b.flag('end_state_not_in_table')
        for k, col in (('ignition_power_w', 'Ignition Power (W)'), ('ignition_time_s', 'Ignition Time (s)'),
                       ('camera_1', 'Camera 1'), ('camera_2', 'Camera 2')):
            b.x(k, r.get(col))
        rows.append(b.row())
    info['PSI-98'] = {'file': path.name, 'test_rows': len(recs), 'non_test_rows_dropped': nontest, 'dropped_empty': dropped}
    # ---- Saffire-II (PSI-99): microgravity rows plus separate 1 g comparison rows linked by pair_id (D14)
    path, recs, dropped, nontest = _saffire_rows('PSI-99/*.csv')
    split = one_g = 0
    for n, r, sid in recs:
        mat = r.get('Material')
        variants = [(sid, mat, r.get('Samle Thickness'), r.get('Sample Length'), None)]
        if mat == 'PMMA & Nomex':  # one card, two samples (table note 2): split into two tests
            variants = [(f'{sid}-PMMA', 'PMMA', '0.85 mm', '5 cm', 'burned_to_completion'),
                        (f'{sid}-Nomex', 'Nomex', '0.37 mm', '24 cm', 'no_ignition')]
            split += 1
        for vid, vmat, vthick, vlen, vout in variants:
            cls = {'silicone': 'elastomer', 'nomex': 'fabric'}.get(vmat.lower())
            if cls is None and 'sibal' in vmat.lower():
                cls = 'fabric'
            b = RowBuilder(test_id=f'PSI-99:{vid}', family='Saffire', psi_id='PSI-99', platform='Cygnus',
                           gravity_level_g='0', gravity_source='nominal', material_or_fuel=vmat,
                           material_class=cls or 'unknown', source_ref=source_ref(path, n))
            b.flag('missing_value:pressure_kpa')
            if sid in SAFFIRE2_MATERIAL_FILL and not vmat:
                fill, fcls = SAFFIRE2_MATERIAL_FILL[sid]
                b.f['material_or_fuel'] = fill
                b.f['material_class'] = fcls
                b.orig['material_or_fuel'] = {'value': '', 'column': 'Material', 'corrected_value': fill, 'origin': 'transcribed_from_table', 'source': REPORT_REF}
                b.flag('corrected_from_report')
                vmat = fill
            if 'pmma' in vmat.lower():
                b.flag('material_shape_not_stated')
            if not vmat:
                b.flag('missing_value:material_or_fuel')
            if len(variants) > 1:
                b.flag('derived_from_two_material_card')
                b.orig['sample_card'] = {'value': mat, 'column': 'Material'}
            if vout is None:
                _thick_mm(b, vthick, 'Samle Thickness', 'mm', corrected_mm=SAFFIRE2_THICKNESS_FIX.get(sid))
                _len_cm(b, 'sample_length_cm', vlen, 'Sample Length')
            else:  # cells read "0.85 and 0.37 mm" and "5 and 24 cm": one value per material, in the order PMMA, Nomex
                b.set('sample_thickness_mm', float(vthick.split()[0]), orig_text=r.get('Samle Thickness'), column='Samle Thickness', unit='mm')
                b.set('sample_length_cm', float(vlen.split()[0]), orig_text=r.get('Sample Length'), column='Sample Length', unit='cm')
                b.flag('size_split_by_position_in_cell')
            _len_cm(b, 'sample_width_cm', r.get('Sample Width (cm)'), 'Sample Width (cm)')
            _flow(b, r.get('Air Flow (cm/s)'), 'Air Flow (cm/s)')
            _o2_text(b, r.get('Percent O2 (Note 1)'), 'Percent O2 (Note 1)')
            b.f['flow_direction'] = r.get('Flow Direction').strip().lower() or 'unknown'
            if sid in SAFFIRE2_FLOW_CONFLICT:
                fld, alt = SAFFIRE2_FLOW_CONFLICT[sid]
                b.f['alt_value_report'] = f'{fld}={alt} ({REPORT_REF})'
                b.flag('source_conflict')
            bt = r.get('Burn Time (s)')
            b.f['outcome_raw'] = f'burn_time={bt}'  # "Insignificant" stays here; burn_duration_s stays empty (D14)
            if vout is None:
                _burn(b, bt, 'Burn Time (s)')
                ug_len = r.get('?-g Burn Length')
                sample_len = parse_with_unit(vlen, ('cm',))[0]
                v, u = parse_with_unit(ug_len, ('cm',))
                if v is not None and sample_len is not None and v == sample_len:
                    b.f['outcome_class'] = 'burned_to_completion'
                    b.flag('outcome_class_provisional', 'rule_burn_length_equals_sample_length')
                elif bt.strip().lower() == 'insignificant':
                    b.flag('insignificant_burn_meaning_undocumented')
            else:
                b.f['outcome_class'] = vout
                b.f['outcome_raw'] += '; table note 2: "The PMMA portion was completely consumed but the Nomex was not ignited."'
                b.flag('outcome_from_table_note_2')
                if vout == 'burned_to_completion':
                    _burn(b, bt, 'Burn Time (s)')
            b.f['outcome_raw'] += f"; ug_burn_length={r.get('?-g Burn Length')}"
            # the PSI header says '?-g Spread Length' but the values are rates in mm/s; the report calls the column
            # '?-g Spread Rate' (NTRS 20170008805 slide 29), so the header is corrected (D14)
            sp = r.get('?-g Spread Length')
            v, u = parse_with_unit(sp, ('mm/s',))
            if v is not None and vout != 'no_ignition':
                b.set('spread_rate', v, orig_text=sp, column='?-g Spread Length', unit='mm/s')
                b.f['spread_rate_basis'] = 'unknown'
                b.flag('header_corrected')
                b.x('spread_rate_header_correction', f'{REPORT_REF}: column is "?-g Spread Rate"')
            for k, col in (('ignition_power', 'Ignition Power (W)'), ('ignition_time', 'Ignition Time (s)'),
                           ('ug_burn_length', '?-g Burn Length'), ('ug_spread_length_raw', '?-g Spread Length'),
                           ('one_g_burn_length', '1-g Burn Length'), ('one_g_spread_rate', '1-g Spread Rate'),
                           ('camera_1', 'Camera 1'), ('camera_2', 'Camera 2')):
                b.x(k, r.get(col))
            if len(variants) > 1:
                b.x('card_cells_shared_by_two_rows', 'yes: ext values are the whole card as printed, not split per material')
            # --- 1 g comparison row (D14); on card 2-7 the 1 g value ("~ 0 (Nomex)") belongs to the Nomex sample only
            g1_len, g1_rate = r.get('1-g Burn Length').strip(), r.get('1-g Spread Rate').strip()
            has_1g = bool(g1_len or g1_rate) and not (len(variants) > 1 and vout == 'burned_to_completion')
            if has_1g:
                pair = f'PSI-99:{vid}'
                b.f['pair_id'] = pair
                c = RowBuilder(test_id=f'PSI-99:{vid}:1g', family='Saffire', psi_id='PSI-99',
                               platform='1 g comparison test (apparatus not stated in the table)', gravity_level_g='1',
                               gravity_source='nominal', material_or_fuel=b.f['material_or_fuel'], material_class=b.f['material_class'],
                               source_ref=source_ref(path, n), pair_id=pair)
                for fld in ('sample_thickness_mm', 'sample_length_cm', 'sample_width_cm', 'oxygen_fraction', 'oxygen_orig'):
                    c.f[fld] = b.f[fld]
                c.orig = {k: dict(v) for k, v in b.orig.items() if k in ('sample_thickness_mm', 'sample_length_cm', 'sample_width_cm', 'oxygen_fraction')}
                c.flag('missing_value:pressure_kpa', 'flow_not_stated_for_1g_test', 'pair_row_of_microgravity_test')
                c.flag(*[f for f in b.flags if f.startswith('material_') or f.startswith('value_typo') or f in ('oxygen_approximate', 'corrected_from_report')])
                c.f['outcome_raw'] = f'1g_burn_length={g1_len}; 1g_spread_rate={g1_rate}'
                if g1_len.lstrip('~ ').lower() == 'complete':
                    c.f['outcome_class'] = 'burned_to_completion'
                    c.flag('outcome_class_from_1g_burn_length_complete')
                v1, _ = parse_with_unit(g1_rate, ('mm/s',))
                if v1 is not None:
                    c.set('spread_rate', v1, orig_text=g1_rate, column='1-g Spread Rate', unit='mm/s')
                    c.f['spread_rate_basis'] = 'unknown'
                c.orig['outcome_class'] = {'value': g1_len, 'column': '1-g Burn Length'}
                c.x('one_g_burn_length', g1_len)
                c.x('one_g_spread_rate', g1_rate)
                rows.append(c.row())
                one_g += 1
            rows.append(b.row())
    info['PSI-99'] = {'file': path.name, 'test_rows_in_source': len(recs), 'split_two_material_cards': split,
                      'one_g_comparison_rows': one_g, 'non_test_rows_dropped': nontest, 'dropped_empty': dropped}
    # ---- Saffire-III (PSI-100)
    path, recs, dropped, nontest = _saffire_rows('PSI-100/*.csv')
    for n, r, sid in recs:
        b = RowBuilder(test_id=f'PSI-100:{sid}', family='Saffire', psi_id='PSI-100', platform='Cygnus (Saffire III enclosure)',
                       gravity_level_g='0', gravity_source='nominal', material_or_fuel=r.get('Material'), material_class='fabric',
                       source_ref=source_ref(path, n))
        b.flag('missing_value:pressure_kpa', 'missing_value:oxygen_fraction', 'outcome_not_in_table')
        _thick_mm(b, r.get('Sample Thickness'), 'Sample Thickness', 'cm')
        _len_cm(b, 'sample_length_cm', r.get('Sample Length'), 'Sample Length')
        _len_cm(b, 'sample_width_cm', r.get('Sample Width'), 'Sample Width')
        _flow(b, r.get('Air Flow'), 'Air Flow')
        b.f['flow_direction'] = r.get('Direction').strip().lower() or 'unknown'
        b.x('camera_1', r.get('Camera 1'))
        b.x('camera_2', r.get('Camera 2'))
        rows.append(b.row())
    info['PSI-100'] = {'file': path.name, 'test_rows': len(recs), 'non_test_rows_dropped': nontest, 'dropped_empty': dropped}
    return rows, info
