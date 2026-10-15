import json
import math
import sys


MAX_BYTES = 65536


def reject_constant(_token):
    raise ValueError('Nonstandard numeric constant')


def parse_integer(_token):
    # Only the numeric type matters; avoid Python's integer digit limit.
    return 0


def parse_float(token):
    value = float(token)
    if not math.isfinite(value):
        raise ValueError('Nonfinite number')
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate object key')
        result[key] = value
    return result


def value_type(value):
    if value is None:
        return 'null'
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, (int, float)):
        return 'number'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, list):
        return 'array'
    return 'object'


def main():
    if len(sys.argv) != 1:
        sys.stderr.write('error: no command-line arguments are accepted\n')
        return 2

    try:
        raw = sys.stdin.buffer.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Input too large')
        text = raw.decode('utf-8', errors='strict')
        records = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_int=parse_integer,
            parse_float=parse_float,
            parse_constant=reject_constant,
        )
        if not isinstance(records, list):
            raise ValueError('Expected an array')
        if any(not isinstance(record, dict) for record in records):
            raise ValueError('Expected objects in the array')

        counts = {}
        for record in records:
            for name, value in record.items():
                types = counts.setdefault(name, {})
                label = value_type(value)
                types[label] = types.get(label, 0) + 1

        total = len(records)
        labels = ('null', 'boolean', 'number', 'string', 'array', 'object')
        fields = []
        for name in sorted(counts):
            types = counts[name]
            present = sum(types.values())
            fields.append({
                'name': name,
                'present': present,
                'missing': total - present,
                'types': {label: types[label] for label in labels if label in types},
            })
        output = json.dumps(
            {'records': total, 'fields': fields},
            ensure_ascii=True,
            allow_nan=False,
            separators=(',', ':'),
        )
    except (ValueError, RecursionError, OverflowError, MemoryError, OSError):
        sys.stderr.write(
            'error: invalid, oversized, excessively nested, or unreadable input\n'
        )
        return 2

    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
