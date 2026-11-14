"""Rule-based normalization of free-text material descriptions (BASS-II and BASS tables).

Only what the text states is extracted. Dimensions whose meaning is unclear are left empty and flagged.
Fractional-inch rod sizes are converted with 1 in = 25.4 mm. Nothing is looked up from outside the text.
"""
import re

IN_MM = 25.4
ROD_FRACTIONS = {'1/4': 0.25, '3/8': 0.375, '1/2': 0.5, '0.5': 0.5}


def normalize_material(text):
    """Return dict(material_class, geometry, thickness_mm, width_cm, flags, ext)."""
    raw = text or ''
    t = ' '.join(raw.lower().replace('"', ' in ').replace('”', ' in ').split())
    out = {'material_class': 'unknown', 'geometry': '', 'thickness_mm': None, 'width_cm': None, 'flags': set(), 'ext': {}}
    fl = out['flags']
    sides = re.search(r'\b([12])\s*-?\s*sided\b', t)
    if sides:
        out['ext']['sides_burning'] = sides.group(1)
    if 'soot clean' in t:
        out.update(material_class='other', geometry='soot cleaning procedure')
        fl.add('non_burn_procedure')
        return out
    if re.search(r'candle|wax|paraffin|parrafin', t):
        out['material_class'] = 'other'
        out['geometry'] = 'candle' if 'candle' in t else 'wax slab'
        fl.add('wax_material')
        return out
    if 'sibal' in t or 'nomex' in t:
        out['material_class'] = 'fabric'
        m = re.search(r'(\d+(?:\.\d+)?)\s*cm', t)
        if m:
            out['geometry'] = f'fabric, size text "{m.group(1)} cm"'
            fl.add('dimension_meaning_unclear')
        else:
            out['geometry'] = 'fabric'
        return out
    if 'rod' in t:
        out['material_class'] = 'solid_rod'
        m = re.search(r'(1/4|3/8|1/2|0\.5)', t)
        if m:
            d = ROD_FRACTIONS[m.group(1)] * IN_MM
            out['geometry'] = f'rod {d:g} mm diameter'
            out['ext']['rod_diameter_mm'] = f'{d:g}'
        else:
            fl.add('dimension_missing')
        return out
    if 'sphere' in t or 'spherical' in t:
        out['material_class'] = 'solid_sphere'
        m = re.search(r'(\d+(?:\.\d+)?)\s*cm', t)
        out['geometry'] = f'sphere {m.group(1)} cm (diameter assumed from size text)' if m else 'sphere'
        if m:
            out['ext']['sphere_size_cm'] = m.group(1)
            fl.add('dimension_meaning_unclear')
        if not re.search(r'pmma|ultem|nomex|sibal', t):
            fl.add('material_not_stated')
        return out
    # flat samples: films, slabs, sheets
    th = re.search(r'(\d+(?:\.\d+)?)\s*(micron|mm)\b', t)
    if th:
        v = float(th.group(1))
        out['thickness_mm'] = v / 1000.0 if th.group(2) == 'micron' else v
    wm = re.search(r'(\d+(?:\.\d+)?)\s*cm(?:\s*wide)?', t)
    if wm and 'sphere' not in t:
        out['width_cm'] = float(wm.group(1))
        if 'wide' not in t:
            fl.add('width_assumed_from_position')
    if 'film' in t or 'micron' in t:
        out['material_class'] = 'film'
    elif 'slab' in t or 'sheet' in t or 'thick' in t:
        out['material_class'] = 'solid_sheet'
    elif th or wm:
        out['material_class'] = 'unknown'
    parts = []
    if out['thickness_mm'] is not None:
        parts.append(f"{out['thickness_mm']:g} mm thick")
    if out['width_cm'] is not None:
        parts.append(f"{out['width_cm']:g} cm wide")
    out['geometry'] = ', '.join(parts) if parts else ''
    if out['material_class'] == 'unknown':
        fl.add('shape_not_stated')
        if wm:
            out['geometry'] = f'size text "{wm.group(1)} cm" (shape not stated)'
            out['width_cm'] = None
            fl.discard('width_assumed_from_position')
    return out
