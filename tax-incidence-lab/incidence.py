"""Weighted fiscal-incidence summaries; Python 3.10+, standard library only.

Input is already harmonized microdata, NOT raw POF files. Values must share
the same unit, time period and population concept. No tax law is encoded.
"""
import argparse
import csv
import json
import math
from itertools import groupby
from pathlib import Path


def validate(rows):
    if not rows:
        raise ValueError('Empty input')
    for r in rows:
        for k in ('income', 'tax_before', 'cashback', 'weight'):
            if k not in r or not math.isfinite(r[k]):
                raise ValueError(f'Missing or non-finite {k}')
        if r['income'] <= 0 or r['weight'] <= 0:
            raise ValueError('Income and weight must be strictly positive; document exclusions upstream')
        if r['tax_before'] < 0 or not 0 <= r['cashback'] <= r['tax_before']:
            raise ValueError('Require 0 <= cashback <= tax_before; negative net taxes unsupported')


def concentration(rows, field):
    """C = 2 sum(w*x*R)/sum(w*x)-1; weighted midrank, ties pooled by income."""
    total_w = sum(r['weight'] for r in rows)
    total_x = sum(r['weight'] * r[field] for r in rows)
    if total_x == 0:
        return None
    previous = numerator = 0.0
    for _, group in groupby(sorted(rows, key=lambda r: r['income']), lambda r: r['income']):
        group = list(group)
        group_w = sum(r['weight'] for r in group)
        rank = (previous + group_w / 2) / total_w
        numerator += rank * sum(r['weight'] * r[field] for r in group)
        previous += group_w
    return 2 * numerator / total_x - 1


def summarize(rows):
    validate(rows)
    rows = [dict(r, tax_after=r['tax_before'] - r['cashback']) for r in rows]
    gini = concentration(rows, 'income')
    c_before = concentration(rows, 'tax_before')
    c_after = concentration(rows, 'tax_after')
    # Split weight at exact decile boundaries. For income ties, pool each
    # tie group first so arbitrary row ordering cannot change decile results.
    bins = [dict(decile=d + 1, weight=0., income=0., tax_before=0., tax_after=0.) for d in range(10)]
    total_w = sum(r['weight'] for r in rows)
    previous = 0.
    for _, group in groupby(sorted(rows, key=lambda r: r['income']), lambda r: r['income']):
        group = list(group)
        gw = sum(r['weight'] for r in group)
        means = {k: sum(r['weight'] * r[k] for r in group) / gw for k in ('income', 'tax_before', 'tax_after')}
        end = previous + gw
        for d, bucket in enumerate(bins):
            overlap = max(0., min(end, total_w * (d + 1) / 10) - max(previous, total_w * d / 10))
            bucket['weight'] += overlap
            for k, value in means.items():
                bucket[k] += overlap * value
        previous = end
    for b in bins:
        b['burden_before_pct'] = 100 * b['tax_before'] / b['income']
        b['burden_after_pct'] = 100 * b['tax_after'] / b['income']
        b['reduction_pp'] = b['burden_before_pct'] - b['burden_after_pct']
    return dict(n=len(rows), gini=gini,
                kakwani_before=None if c_before is None else c_before - gini,
                kakwani_after=None if c_after is None else c_after - gini,
                deciles=bins)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source', required=True, help='Source/version/table or processing provenance')
    p.add_argument('--scenario', required=True)
    p.add_argument('--unit', required=True, help='e.g. person, monthly per-capita BRL, person expansion weights')
    args = p.parse_args()
    with args.input.open(encoding='utf-8-sig', newline='') as f:
        rows = [{k: float(r[k]) for k in ('income', 'tax_before', 'cashback', 'weight')} for r in csv.DictReader(f)]
    output = summarize(rows)
    output.update(source=args.source, scenario=args.scenario, unit=args.unit)
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2, allow_nan=False), encoding='utf-8')


if __name__ == '__main__':
    main()
