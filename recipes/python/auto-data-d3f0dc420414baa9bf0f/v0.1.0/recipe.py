import sys
import json
import re


def reject_constant(token):
    raise ValueError('Non-finite number')


def reject_float(token):
    raise ValueError('Floating-point number')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate key')
        result[key] = value
    return result


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError('CLI arguments are not allowed')

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Input too large')
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff'):
            raise ValueError('Leading BOM')

        records = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
            parse_float=reject_float,
        )
        if (not (isinstance(records, list))) or len(records) > 40:
            raise ValueError('Expected an array of at most 40 records')

        name_pattern = re.compile(r'[a-z][a-z0-9_-]{0,19}')
        required_keys = {'group', 'value', 'weight', 'tag'}

        # Validate every record before performing any transformations.
        for record in records:
            if (not (isinstance(record, dict))) or set(record) != required_keys:
                raise ValueError('Invalid record fields')
            for key in ('group', 'tag'):
                item = record[key]
                if (not (isinstance(item, str))) or name_pattern.fullmatch(item) is None:
                    raise ValueError('Invalid group or tag')
            value = record['value']
            weight = record['weight']
            if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
                raise ValueError('Invalid value')
            if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
                raise ValueError('Invalid weight')

        totals = {}
        for record in records:
            group = record['group']
            totals[group] = totals.get(group, 0) + record['value'] * record['weight']

        result = {
            'groups': [
                {'group': group, 'weighted_total': totals[group]}
                for group in sorted(totals)
            ]
        }
        output = json.dumps(result, ensure_ascii=True, separators=(',', ':')) + '\n'
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
