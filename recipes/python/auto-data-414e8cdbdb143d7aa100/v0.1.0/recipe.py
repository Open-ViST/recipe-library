import sys
import json
import re


def reject_number(text):
    raise ValueError('unsupported numeric value')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate object key')
        result[key] = value
    return result


def build_output():
    if len(sys.argv) != 1:
        raise ValueError('arguments are not allowed')

    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise ValueError('input is too large')
    text = raw.decode('utf-8', errors='strict')
    if text.startswith('\ufeff'):
        raise ValueError('leading BOM is not allowed')

    records = json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_float=reject_number,
        parse_constant=reject_number,
    )
    if (not (isinstance(records, list))) or len(records) > 40:
        raise ValueError('expected an array of at most 40 records')

    required = {'group', 'value', 'weight', 'tag'}
    for record in records:
        if (not (isinstance(record, dict))) or set(record) != required:
            raise ValueError('invalid record fields')
        for field in ('group', 'tag'):
            item = record[field]
            if (not (isinstance(item, str))) or re.fullmatch(r'[a-z][a-z0-9_-]{0,19}', item) is None:
                raise ValueError('invalid group or tag')
        value = record['value']
        weight = record['weight']
        if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
            raise ValueError('invalid value')
        if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
            raise ValueError('invalid weight')

    selected = {}
    for record in records:
        group = record['group']
        if group not in selected or record['value'] > selected[group]['value']:
            selected[group] = record

    result = {'groups': [selected[group] for group in sorted(selected)]}
    return json.dumps(result, ensure_ascii=True, allow_nan=False) + '\n'


def main():
    try:
        output = build_output()
    except Exception:
        sys.stderr.write('error: invalid input or input read failure\n')
        return 2
    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
