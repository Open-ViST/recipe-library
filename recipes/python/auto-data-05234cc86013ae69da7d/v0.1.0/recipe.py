import sys
import json
import re


def reject_number(token):
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
            raise ValueError('invalid record array')

        pattern = re.compile(r'[a-z][a-z0-9_-]{0,19}', re.ASCII)
        fields = {'group', 'value', 'weight', 'tag'}
        for record in records:
            if (not (isinstance(record, dict))) or set(record) != fields:
                raise ValueError('invalid record fields')
            for field in ('group', 'tag'):
                item = record[field]
                if (not (isinstance(item, str))) or pattern.fullmatch(item) is None:
                    raise ValueError('invalid string')
            value = record['value']
            weight = record['weight']
            if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
                raise ValueError('invalid value')
            if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
                raise ValueError('invalid weight')

        extrema = {}
        for record in records:
            group = record['group']
            value = record['value']
            if group not in extrema:
                extrema[group] = [value, value]
            else:
                bounds = extrema[group]
                bounds[0] = min(bounds[0], value)
                bounds[1] = max(bounds[1], value)

        groups = []
        for group in sorted(extrema):
            minimum, maximum = extrema[group]
            groups.append({
                'group': group,
                'minimum': minimum,
                'maximum': maximum,
                'spread': maximum - minimum,
            })
        output = json.dumps({'groups': groups}, separators=(',', ':')) + '\n'
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    sys.stdout.write(output)
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
