import sys
import json
import re


def reject_number(text):
    raise ValueError('Unsupported numeric value')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate object key')
        result[key] = value
    return result


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError('CLI arguments are not allowed')

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Input exceeds byte limit')
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff'):
            raise ValueError('Leading BOM is not allowed')

        records = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
        if (not (isinstance(records, list))) or len(records) > 40:
            raise ValueError('Expected an array of at most 40 records')

        required_keys = {'group', 'value', 'weight', 'tag'}
        pattern = re.compile(r'[a-z][a-z0-9_-]{0,19}')
        for record in records:
            if (not (isinstance(record, dict))) or set(record) != required_keys:
                raise ValueError('Invalid record fields')
            for field in ('group', 'tag'):
                value = record[field]
                if (not (isinstance(value, str))) or pattern.fullmatch(value) is None:
                    raise ValueError('Invalid group or tag')
            if (not ((isinstance(record['value'], int) and not isinstance(record['value'], bool)))):
                raise ValueError('Value must be an integer')
            if not -1000000 <= record['value'] <= 1000000:
                raise ValueError('Value out of range')
            if (not ((isinstance(record['weight'], int) and not isinstance(record['weight'], bool)))):
                raise ValueError('Weight must be an integer')
            if not -1000 <= record['weight'] <= 1000:
                raise ValueError('Weight out of range')

        totals = {}
        for record in records:
            group = record['group']
            if group not in totals:
                totals[group] = {'group': group, 'count': 0, 'total': 0}
            totals[group]['count'] += 1
            totals[group]['total'] += record['value']

        result = {'groups': [totals[group] for group in sorted(totals)]}
        output = json.dumps(result, separators=(',', ':'), allow_nan=False)
    except Exception:
        sys.stderr.write('error: invalid input or input-read failure\n')
        return 2

    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
