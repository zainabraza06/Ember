"""Unified test-table schema (docs/DATA_DICTIONARY.md section 2) and validators."""
import json

COLUMNS = [
    'test_id', 'record_type', 'family', 'psi_id', 'platform', 'gravity_level_g', 'gravity_source',
    'material_or_fuel', 'material_class', 'sample_geometry', 'sample_thickness_mm', 'sample_width_cm', 'sample_length_cm',
    'oxygen_fraction', 'oxygen_fraction_final', 'oxygen_orig', 'pressure_kpa', 'pressure_orig', 'diluent',
    'flow_velocity_cm_s', 'flow_direction', 'spread_orientation', 'ignition_method',
    'uloi_vol_pct', 'moc_vol_pct', 'o2_margin_vs_1g_pct', 'limit_criterion',
    'outcome_raw', 'outcome_class', 'outcome_class_proposed', 'outcome_proposal_confidence', 'outcome_review_status',
    'spread_rate', 'spread_rate_basis', 'burn_duration_s', 'pair_id', 'alt_value_report',
    'data_origin', 'source_ref', 'quality_flags', 'orig_values', 'ext', 'notes',
]

RECORD_TYPES = {'test', 'limit', 'series_summary'}
FAMILIES = {'FLEX', 'CFI-G', 'BASS-II', 'BASS', 'Saffire', 'partial_gravity_literature', 'screening_1g'}
GRAVITY_SOURCES = {'measured', 'nominal', 'assumed'}
MATERIAL_CLASSES = {'liquid_droplet', 'gas_fuel', 'solid_sheet', 'film', 'fabric', 'solid_rod', 'solid_sphere', 'foam',
                    'elastomer', 'laminate', 'other', 'unknown'}
FLOW_DIRECTIONS = {'opposed', 'concurrent', 'quiescent', 'unknown'}
ORIENTATIONS = {'upward', 'downward', 'horizontal', 'not_applicable', 'unknown', ''}
OUTCOME_CLASSES = {'no_ignition', 'self_extinguished', 'burned_to_completion', 'externally_terminated', 'other', 'unknown'}
SPREAD_BASES = {'flame_base', 'flame_tip', 'pyrolysis_front', 'regression', 'unknown', ''}
DATA_ORIGINS = {'psi_table', 'transcribed_from_table', 'read_from_figure', 'transcribed_from_text'}
CONFIDENCES = {'high', 'medium', 'low', ''}
REVIEW_STATUSES = {'', 'not_applicable', 'proposed', 'approved', 'rejected', 'changed'}
NUMERIC = ['gravity_level_g', 'sample_thickness_mm', 'sample_width_cm', 'sample_length_cm', 'oxygen_fraction',
           'oxygen_fraction_final', 'pressure_kpa', 'flow_velocity_cm_s', 'uloi_vol_pct', 'moc_vol_pct',
           'o2_margin_vs_1g_pct', 'spread_rate', 'burn_duration_s']


def validate_row(r):
    """Return a list of problems for one row (dict of strings/numbers)."""
    p = []
    def bad(msg): p.append(f"{r.get('test_id')}: {msg}")
    for c in COLUMNS:
        if c not in r:
            bad(f'missing column {c}')
    if not r.get('test_id'): bad('empty test_id')
    if r.get('record_type') not in RECORD_TYPES: bad(f"record_type {r.get('record_type')!r}")
    if r.get('family') not in FAMILIES: bad(f"family {r.get('family')!r}")
    if r.get('gravity_source') not in GRAVITY_SOURCES: bad('gravity_source')
    if r.get('material_class') not in MATERIAL_CLASSES: bad(f"material_class {r.get('material_class')!r}")
    if r.get('flow_direction') not in FLOW_DIRECTIONS: bad(f"flow_direction {r.get('flow_direction')!r}")
    if r.get('spread_orientation', '') not in ORIENTATIONS: bad(f"spread_orientation {r.get('spread_orientation')!r}")
    if r.get('outcome_class') not in OUTCOME_CLASSES: bad(f"outcome_class {r.get('outcome_class')!r}")
    if r.get('spread_rate_basis', '') not in SPREAD_BASES: bad('spread_rate_basis')
    if r.get('data_origin') not in DATA_ORIGINS: bad('data_origin')
    if r.get('outcome_class_proposed', '') not in OUTCOME_CLASSES | {''}: bad('outcome_class_proposed')
    if r.get('outcome_proposal_confidence', '') not in CONFIDENCES: bad('outcome_proposal_confidence')
    if r.get('outcome_review_status', '') not in REVIEW_STATUSES: bad('outcome_review_status')
    if not r.get('source_ref'): bad('empty source_ref')
    if 'quality_flags' not in r: bad('no quality_flags')
    for c in NUMERIC:
        v = r.get(c, '')
        if v == '' or v is None: continue
        try:
            float(v)
        except (TypeError, ValueError):
            bad(f'{c} not numeric: {v!r}')
    def num(c):
        v = r.get(c, '')
        return None if v in ('', None) else float(v)
    o = num('oxygen_fraction')
    if o is not None and not 0 <= o <= 1: bad(f'oxygen_fraction out of range {o}')
    o = num('oxygen_fraction_final')
    if o is not None and not 0 <= o <= 1: bad(f'oxygen_fraction_final out of range {o}')
    pk = num('pressure_kpa')
    if pk is not None and not 0 < pk < 1000: bad(f'pressure_kpa out of range {pk}')
    g = num('gravity_level_g')
    if g is not None and not 0 <= g <= 2: bad(f'gravity_level_g out of range {g}')
    bd = num('burn_duration_s')
    if bd is not None and bd < 0: bad('negative burn_duration_s')
    for c in ('orig_values', 'ext'):
        try:
            json.loads(r.get(c) or '{}')
        except ValueError:
            bad(f'{c} is not valid JSON')
    return p
