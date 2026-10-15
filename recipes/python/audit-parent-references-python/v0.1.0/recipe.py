import json
import sys
import math


MAX_BYTES = 65536


def reject_constant(_token):
    raise ValueError('invalid constant')


def parse_finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        raise ValueError('nonfinite number')
    return value


def parse_integer(token):
    # Preserve large JSON integers without changing interpreter settings.
    negative = token.startswith('-')
    digits = token[1:] if negative else token
    value = 0
    for offset in range(0, len(digits), 1000):
        chunk = digits[offset:offset + 1000]
        value = value * (10 ** len(chunk)) + int(chunk)
    return -value if negative else value


def valid_identifier(value):
    return isinstance(value, str) and 1 <= len(value) <= 80


def process_input():
    if len(sys.argv) != 1:
        raise ValueError('arguments are not supported')

    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('input too large')
    if raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('leading BOM')
    text = raw.decode('utf-8', errors='strict')

    records = json.loads(
        text,
        parse_constant=reject_constant,
        parse_float=parse_finite_float,
        parse_int=parse_integer,
    )
    if not isinstance(records, list) or len(records) > 100:
        raise ValueError('invalid collection')

    identifiers = set()
    pairs = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('invalid record')
        if 'id' not in record or 'parent' not in record:
            raise ValueError('missing field')
        identifier = record['id']
        parent = record['parent']
        if not valid_identifier(identifier):
            raise ValueError('invalid identifier')
        if parent is not None and not valid_identifier(parent):
            raise ValueError('invalid parent')
        if identifier in identifiers:
            raise ValueError('duplicate identifier')
        identifiers.add(identifier)
        pairs.append((identifier, parent))

    roots = sorted(identifier for identifier, parent in pairs if parent is None)
    dangling = [
        {'id': identifier, 'parent': parent}
        for identifier, parent in sorted(pairs, key=lambda pair: pair[0])
        if parent is not None and parent not in identifiers
    ]
    return json.dumps(
        {'roots': roots, 'dangling': dangling},
        ensure_ascii=True,
        allow_nan=False,
        separators=(',', ':'),
    )


def main():
    try:
        output = process_input()
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    # Output-write failures are deliberately outside the input-error handler.
    sys.stdout.write(output + '\n')
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
