"""Rebuild src/data.json from the Google Sheets text export (LIVE Google Sheets Master).

Usage: python3 src/parse_sheet.py path/to/export.txt
The export is plain text: '## Sheet name: X' lines followed by CSV.
Numbers in the export use '.' as thousands separator, so '2.200' = 2200 and '242.000' = 242000.
"""
import csv, io, json, re, sys
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding='utf-8')
sections = {}
for part in re.split(r'^## Sheet name: ', src, flags=re.M)[1:]:
    name, _, body = part.partition('\n')
    sections[name.strip()] = list(csv.reader(io.StringIO(body)))

def num(s):
    s = (s or '').strip().replace('¥','').replace('Rp','').replace('RM','').replace(' ','')
    if not s: return 0
    s = s.replace('.', '').replace(',', '.') if re.search(r'\.\d{3}(\D|$)', s) or ',' in s else s
    try: v = float(s)
    except ValueError: return 0
    return int(v) if v == int(v) else v

MON = {'Nov':11,'Dec':12}
def iso(title):
    m = re.search(r'(\d{1,2})\s+(Nov|Dec)', title)
    return f"2026-{MON[m.group(2)]:02d}-{int(m.group(1)):02d}"

# ---- itinerary
days = []
for r in sections['Detailed Itinerary']:
    r = r + [''] * (14 - len(r))
    if r[0].strip() and re.search(r'\d+ (Nov|Dec) •', r[0]):
        days.append({'title': r[0].strip(), 'route': r[3].strip(), 'stay': r[4].strip(), 'theme': r[5].strip(), 'items': [], 'subtotalNote': '', 'date': iso(r[0])})
    elif days and r[2].strip():
        days[-1]['items'].append({'time': r[2].strip(), 'area': r[3].strip(), 'act': r[5].strip(), 'jpy': num(r[6]), 'idr': num(r[7]),
            'mode': r[8].strip(), 'dur': r[9].strip(), 'ticket': r[10].strip(), 'status': r[11].strip(), 'note': r[12].strip(), 'src': r[13].strip()})
    elif days and r[5].startswith('DAY SUBTOTAL'):
        days[-1]['subtotalNote'] = r[5].strip()

def table(rows, header_first):
    out, hdr = [], None
    for r in rows:
        if r and r[0] == header_first: hdr = r; continue
        if hdr is None: continue
        if r and r[0].isupper() and len(r) < 3 and r[0] != header_first and out: break
        if not any(c.strip() for c in r): break
        if len(r) < 3 and not r[0].strip(): break
        if r[0].strip() == '' and not any(r[1:3]): break
        out.append({h: (r[i].strip() if i < len(r) else '') for i, h in enumerate(hdr) if h})
    return out

hotels = table(sections['Hotels & Stays'], 'Stay')
for h in hotels:
    try: h['Nights'] = int(h['Nights'])
    except ValueError: pass
tips = table(sections['Tips & Notes'], 'Category')

# ---- bookings + notes block
rows = sections['Bookings & Adjustments']
bookings = [b for b in table(rows, 'Priority') if b.get('Priority') in ('HIGH','MED','LOW')]
def after(marker):
    for i, r in enumerate(rows):
        if r and r[0].startswith(marker): return i + 1
    return None
def grab(marker, stop):
    i = after(marker); out = []
    while i is not None and i < len(rows) and not (rows[i] and rows[i][0].startswith(stop)):
        if any(c.strip() for c in rows[i]): out.append([c.strip() for c in rows[i]])
        i += 1
    return out
revisions = grab('REVISION POINTS', 'OPTIONAL SWAPS')
swaps = grab('OPTIONAL SWAPS', 'RETURN-FLIGHT')
tripflex = ' '.join(r[0] for r in grab('RETURN-FLIGHT', 'LATEST BOOKING'))
recon = grab('LATEST BOOKING', 'zzzz')

# ---- transportation: arrival table + major transfers
trows = sections['Transportation']
trans, major, mode = [], [], None
for r in trows:
    r = r + [''] * (12 - len(r))
    if r[1] == 'Date' and r[2] == 'From - To': mode = 'arr'; continue
    if r[1].startswith('MAJOR TRANSFERS'): mode = 'maj_h'; continue
    if mode == 'maj_h' and r[1] == 'Date': mode = 'maj'; continue
    if mode == 'arr' and any(r): 
        d = r[1].strip()
        trans.append(['2026-11-22' if d else '', r[2].strip(), r[3].strip(), r[4].strip(), num(r[5]), num(r[6]), r[7].strip(), r[8].strip(), r[9].strip(), r[10].strip(), r[11].strip()])
    elif mode == 'arr': mode = None
    if mode == 'maj' and r[1].strip():
        major.append({'date': r[1].strip(), 'route': r[2].strip(), 'mode': r[3].strip(), 'resv': r[4].strip(), 'paid': r[5].strip(), 'dep': r[7].strip(), 'arr': r[8].strip(), 'seats': r[9].strip(), 'status': r[10].strip(), 'note': r[11].strip()})

# ---- budget, shopping, change log
brow = sections['Budget & Payments']
payments, pending, i = [], [], 0
hdr = None
for r in brow:
    if r and r[0] == 'Travel date': hdr = 'paid'; continue
    if r and r[0] == 'Item' and 'Expected total' in r: hdr = 'pend'; continue
    if hdr == 'paid' and len(r) > 9 and r[0].strip():
        payments.append({'date': r[0].strip(), 'type': r[1].strip(), 'item': r[2].strip(), 'detail': r[3].strip(), 'pax': num(r[4]), 'cur': r[5].strip(), 'amt': num(r[6].replace('.', '').replace(',', '.') if False else r[6].replace('.', '').replace(',00', '')), 'note': r[10].strip()})
    elif hdr == 'paid' and r and r[0].startswith('PENDING'): hdr = None
    if hdr == 'pend' and r and r[0].strip() and len(r) > 6 and r[0] != 'Item':
        pending.append({'item': r[0].strip(), 'date': r[1].strip(), 'cur': r[2].strip(), 'amt': num(r[3]), 'status': r[5].strip(), 'note': r[6].strip()})
rates = {}
for r in brow:
    if r and r[0] in ('JPY', 'MYR') and len(r) > 1 and ',' in r[1] and r[0] not in rates and len(rates) < 2:
        rates[r[0]] = num(r[1].split(',')[0])
shopping = table(sections['Shopping & Gear'], 'Date')
changelog = table(sections['Change Log'], 'Date')
dbud = table(sections['Daily Budget'], 'Date')

out = {'days': days, 'hotels': hotels, 'bookings': bookings, 'tips': tips, 'trans': trans, 'revisions': revisions, 'swaps': swaps, 'tripflex': tripflex,
       'recon': recon, 'major': major, 'payments': payments, 'pending': pending, 'sheetRates': rates, 'shopping': shopping, 'changelog': changelog}
Path(__file__).with_name('data.json').write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding='utf-8')
print({k: (len(v) if hasattr(v, '__len__') else v) for k, v in out.items()})
