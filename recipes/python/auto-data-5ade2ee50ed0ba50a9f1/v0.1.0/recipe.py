import sys
import json
import re


def reject_number(text):
    raise ValueError('unsupported number')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate key')
        result[key] = value
    return result


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError('arguments are not allowed')

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('input too large')
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff'):
            raise ValueError('leading BOM')

        records = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
        if (not (isinstance(records, list))) or len(records) > 40:
            raise ValueError('expected an array of at most 40 records')

        name_pattern = re.compile(r'[a-z][a-z0-9_-]{0,19}', re.ASCII)
        required_keys = {'group', 'value', 'weight', 'tag'}

        for record in records:
            if (not (isinstance(record, dict))) or set(record) != required_keys:
                raise ValueError('invalid record fields')
            for field in ('group', 'tag'):
                item = record[field]
                if (not (isinstance(item, str))) or name_pattern.fullmatch(item) is None:
                    raise ValueError('invalid name')
            value = record['value']
            weight = record['weight']
            if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
                raise ValueError('invalid value')
            if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
                raise ValueError('invalid weight')

        totals = {}
        for record in records:
            if record['value'] > 0:
                group = record['group']
                totals[group] = totals.get(group, 0) + record['value'] * record['weight']

        result = {
            'groups': [
                {'group': group, 'weighted_total': totals[group]}
                for group in sorted(totals)
            ]
        }
        output = json.dumps(result, ensure_ascii=True, allow_nan=False)
    except Exception:
        sys.stderr.write('error: invalid input, input read failure, or unsupported arguments\n')
        return 2

    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
