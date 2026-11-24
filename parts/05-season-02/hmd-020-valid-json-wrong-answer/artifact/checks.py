"""
HMD-020 · the three lights of the Structured Output Testbench.

    STRUCTURE  parse_reply() + validate_schema()   does it read as JSON, and does it fit the form (schema.json)?
    RULE       check_rules()                       does it obey the shop's business rules (catalog, window, prices)?
    MEANING    grade()                             is it what the customer actually asked for? (needs the answer key,
                                                   so this light exists only in the lab)

route() is the product decision for arm 4: record automatically, repair once, or send to a person.
Standard library only. The rules were fixed before any model call (see protocol.md).
"""

import datetime as dt
import json
import re
from pathlib import Path

import world

HERE = Path(__file__).resolve().parent
SCHEMA = json.loads((HERE / 'schema.json').read_text(encoding='utf-8'))
FIELDS = ('product', 'quantity', 'paid_toman', 'delivery_date')    # graded fields (quantity is graded with its unit)
PRICE_TOLERANCE = 0.05            # paid amount must be within ±5% of the catalog total
REQUIRED_FOR_AUTO = ('quantity', 'unit', 'delivery_date')           # paid_toman = null means "pay on delivery"


# ── light 1a: does it parse? ─────────────────────────────────────────────────────────────────────
FENCE = re.compile(r'^```(?:json)?\s*\n?(.*?)\n?```$', re.S)


def parse_reply(text):
    """The reply must be one JSON object. A surrounding Markdown code fence is tolerated (most pipelines strip it);
    any other text around the object is not. Returns (object or None, reason)."""
    t = (text or '').strip()
    m = FENCE.match(t)
    if m:
        t = m.group(1).strip()
    try:
        obj = json.loads(t)
    except (json.JSONDecodeError, ValueError) as e:
        return None, f'not JSON: {e.msg}'
    if not isinstance(obj, dict):
        return None, 'JSON, but not an object'
    return obj, 'ok'


# ── light 1b: does it fit the form? (a small JSON Schema validator: the keywords schema.json uses) ──
def _type_ok(value, t):
    if t == 'null':
        return value is None
    if t == 'boolean':
        return isinstance(value, bool)
    if t == 'integer':
        return isinstance(value, int) and not isinstance(value, bool) or \
            isinstance(value, float) and value.is_integer()
    if t == 'number':
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == 'string':
        return isinstance(value, str)
    if t == 'object':
        return isinstance(value, dict)
    if t == 'array':
        return isinstance(value, list)
    raise ValueError(t)


def _date_ok(s):
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', s):
        return False
    try:
        dt.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def validate_schema(value, schema=SCHEMA, path='$'):
    """Errors as a list of strings; [] means the value fits. `format: date` is asserted here (JSON Schema treats
    format as an annotation by default, so many validators would not even check it)."""
    errs = []
    if 'anyOf' in schema:
        if not any(not validate_schema(value, sub, path) for sub in schema['anyOf']):
            errs.append(f'{path}: matches none of the allowed shapes')
        return errs
    t = schema.get('type')
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(value, x) for x in types):
            return [f'{path}: expected {"/".join(types)}, got {type(value).__name__}']
    if 'enum' in schema and value not in schema['enum']:
        errs.append(f'{path}: {value!r} is not one of the allowed values')
    if schema.get('format') == 'date' and isinstance(value, str) and not _date_ok(value):
        errs.append(f'{path}: {value!r} is not a YYYY-MM-DD date')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for k in schema.get('required', []):
            if k not in value:
                errs.append(f'{path}: missing field {k}')
        if schema.get('additionalProperties') is False:
            for k in value:
                if k not in props:
                    errs.append(f'{path}: unexpected field {k}')
        for k, sub in props.items():
            if k in value:
                errs += validate_schema(value[k], sub, f'{path}.{k}')
    return errs


# ── light 2: does it obey the business rules? ────────────────────────────────────────────────────
def missing_fields(rec):
    return [k for k in REQUIRED_FOR_AUTO if rec.get(k) is None]


MONEY_WORDS = ('تومان', 'تومن', 'ریال', 'میلیون', 'کارت به کارت', 'واریز', 'ریختم')   # a unit, or a payment verb
REPAIR_HINTS = {   # what the repair call is told: the rule, never the catalog total (that would hand over the answer)
    'unit': 'the unit is not one this product is sold in',
    'quantity': 'the quantity is outside what this shop accepts for this product (zero, above the household cap, or '
                'a fraction of a piece or pack)',
    'date': 'the delivery date is outside the delivery window (today to 14 days from today)',
    'price': 'paid_toman does not fit the catalog price of the ordered quantity; re-read the amount, its words '
             '(هزار، میلیون) and its currency (تومان or ریال)',
    'evidence': 'the message mentions a payment or an amount, but paid_toman is null',
}


def check_rules(rec, today=world.TODAY, message=None):
    """Business-rule violations for a schema-valid record, as (rule id, plain message). Null fields are not rule
    violations: they are reported by missing_fields() and go to a person to ask the customer.
    With the original message, one more rule (rule 5) compares the record with its source: if the message mentions
    an amount or a payment, paid_toman must not be null (null means "pay on delivery"). Added on 24 Nov 2026 after
    seeing the demo extractor's results on the TEST set, before any model output existed (protocol.md)."""
    out = []
    if message is not None and rec.get('paid_toman') is None and any(w in message for w in MONEY_WORDS):
        out.append(('evidence', 'the message mentions a payment or an amount but paid_toman is null'))
    product, qty, unit = rec['product'], rec.get('quantity'), rec.get('unit')
    name, _, allowed, base, price, cap = world.CATALOG[product]
    if unit is not None and unit not in allowed:
        out.append(('unit', f'unit "{unit}" is not sold for {product}; allowed: {", ".join(allowed)}'))
    q = world.to_base(product, qty, unit) if unit in allowed else None
    if qty is not None and unit in allowed:
        if q <= 0:
            out.append(('quantity', f'quantity must be more than zero, got {qty} {unit}'))
        elif q > cap:
            out.append(('quantity', f'{q:g} {base} is above the household cap of {cap} {base} for {product}'))
        elif base in ('piece', 'pack') and q != int(q):
            out.append(('quantity', f'{product} is sold in whole {base}s, got {q:g}'))
    d = rec.get('delivery_date')
    if d is not None:
        day = dt.date.fromisoformat(d)
        if not today <= day <= today + dt.timedelta(days=world.WINDOW_DAYS):
            out.append(('date', f'{d} is outside the delivery window {today} .. '
                                f'{today + dt.timedelta(days=world.WINDOW_DAYS)}'))
    paid = rec.get('paid_toman')
    if paid is not None and q is not None and q > 0:
        total = q * price
        ratio = paid / total
        if abs(ratio - 1) > PRICE_TOLERANCE:
            out.append(('price', f'paid {paid:,} toman but the catalog total is {round(total):,} toman '
                                 f'(ratio {ratio:.3g})'))
    elif paid is not None and paid <= 0:
        out.append(('price', f'paid amount must be more than zero, got {paid}'))
    return out


# ── light 3 (lab only): is it what the customer meant? ───────────────────────────────────────────
def _num_eq(a, b):
    return a is not None and b is not None and abs(a - b) <= 1e-9 * max(1, abs(b))


def grade(rec, truth):
    """Per-field correctness against the answer key. quantity counts only together with its unit (750 g of cheese
    and 0.75 kg are the same order; 750 kg is not). A null in the key must be null in the record."""
    if rec is None:
        return {f: False for f in FIELDS}
    out = {'product': rec.get('product') == truth['product']}
    tq = truth['quantity']
    if tq is None:
        out['quantity'] = rec.get('quantity') is None
    else:
        p = truth['product']
        out['quantity'] = rec.get('product') == p and _num_eq(world.to_base(p, rec.get('quantity'), rec.get('unit')),
                                                              world.to_base(p, tq, truth['unit']))
    tp = truth['paid_toman']
    out['paid_toman'] = rec.get('paid_toman') is None if tp is None else _num_eq(rec.get('paid_toman'), tp)
    out['delivery_date'] = rec.get('delivery_date') == truth['delivery_date']
    return out


def lights(text, truth, message=None):
    """All three lights for one reply. Returns a dict the report and the deck use."""
    rec, why = parse_reply(text)
    parse_ok = rec is not None
    schema_errs = validate_schema(rec) if parse_ok else ['not parsed']
    schema_ok = parse_ok and not schema_errs
    rules = check_rules(rec, message=message) if schema_ok else []
    missing = missing_fields(rec) if schema_ok else []
    fields = grade(rec if schema_ok else None, truth)     # the API rejects a record that misses the form: no field counts
    correct = all(fields.values())
    return {'parse_ok': parse_ok, 'parse_reason': why, 'schema_ok': schema_ok, 'schema_errors': schema_errs[:3],
            'rule_ok': schema_ok and not rules, 'rule_violations': [r[0] for r in rules],
            'repair_hints': [REPAIR_HINTS[r[0]] for r in rules],
            'rule_messages': [r[1] for r in rules], 'missing': missing, 'fields': fields, 'correct': correct,
            'silent_error': schema_ok and not correct, 'record': rec}


def route(first, repaired=None):
    """The product decision for one order (arm 4).
    auto          structure + rules pass, nothing missing: record it automatically
    auto_repaired rules failed, one repair call fixed it: record it automatically (flagged in the log)
    human_*       a person checks it: 'missing' (ask the customer), 'rule' (repair failed), 'schema'"""
    if not first['schema_ok']:
        return 'human_schema'
    if first['missing']:
        return 'human_missing'
    if first['rule_ok']:
        return 'auto'
    if repaired is None:
        return 'human_rule'
    if repaired['schema_ok'] and not repaired['missing'] and repaired['rule_ok']:
        return 'auto_repaired'
    return 'human_rule'
