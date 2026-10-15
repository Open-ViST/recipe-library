# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
import argparse
import csv
import json
import pathlib
import sys


def read_snapshot(path, key_name):
    try:
        with path.open('r', encoding='utf-8', newline='') as source:
            reader = csv.DictReader(source, strict=True)
            headers = reader.fieldnames
            if not headers:
                raise ValueError(f'{path}: missing CSV header')
            if len(headers) != len(set(headers)):
                raise ValueError(f'{path}: duplicate header names')
            if key_name not in headers:
                raise ValueError(f'{path}: key column {key_name!r} not found')

            records = {}
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(f'{path}: extra fields on line {line_number}')
                if any(value is None for value in row.values()):
                    raise ValueError(f'{path}: missing fields on line {line_number}')
                key = row[key_name]
                if key == '':
                    raise ValueError(f'{path}: blank key on line {line_number}')
                if key in records:
                    raise ValueError(f'{path}: duplicate key {key!r} on line {line_number}')
                records[key] = row
            return records, headers
    except OSError as exc:
        raise ValueError(f'{path}: cannot read file: {exc}') from exc
    except UnicodeError as exc:
        raise ValueError(f'{path}: input is not valid UTF-8: {exc}') from exc
    except csv.Error as exc:
        raise ValueError(f'{path}: invalid CSV: {exc}') from exc


def main():
    parser = argparse.ArgumentParser(
        description='Compare two local CSV snapshots by a unique key column.'
    )
    parser.add_argument('before', help='earlier CSV file')
    parser.add_argument('after', help='later CSV file')
    parser.add_argument('--key', required=True, help='exact key-column header')
    args = parser.parse_args()

    try:
        before, before_headers = read_snapshot(pathlib.Path(args.before), args.key)
        after, after_headers = read_snapshot(pathlib.Path(args.after), args.key)
        if set(before_headers) != set(after_headers):
            raise ValueError('CSV snapshots must have the same column names')
    except ValueError as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2

    before_keys = set(before)
    after_keys = set(after)
    added = sorted(after_keys - before_keys)
    removed = sorted(before_keys - after_keys)
    changed = []
    for key in sorted(before_keys & after_keys):
        fields = sorted(
            name for name in before[key]
            if name != args.key and before[key][name] != after[key][name]
        )
        if fields:
            changed.append({'key': key, 'fields': fields})

    result = {'added': added, 'removed': removed, 'changed': changed}
    json.dump(result, sys.stdout, ensure_ascii=False, sort_keys=True)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())