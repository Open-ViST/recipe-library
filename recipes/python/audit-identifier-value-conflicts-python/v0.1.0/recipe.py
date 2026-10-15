import json
import sys
import math


def reject_constant(token):
    raise ValueError()


def parse_float(token):
    number = float(token)
    if not math.isfinite(number):
        raise ValueError()
    return number


def parse_integer(token):
    # No integer fields are supported. A sentinel avoids integer digit limits
    # for ignored fields while ensuring numeric IDs and values are rejected.
    return None


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError()

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536 or raw.startswith(b'\xef\xbb\xbf'):
            raise ValueError()
        text = raw.decode('utf-8', errors='strict')
        records = json.loads(
            text,
            parse_constant=reject_constant,
            parse_float=parse_float,
            parse_int=parse_integer,
        )

        if not isinstance(records, list) or len(records) > 100:
            raise ValueError()

        grouped = {}
        for record in records:
            if not isinstance(record, dict):
                raise ValueError()
            record_id = record.get('id')
            value = record.get('value')
            if not isinstance(record_id, str) or not 1 <= len(record_id) <= 80:
                raise ValueError()
            if not isinstance(value, str) or not 1 <= len(value) <= 80:
                raise ValueError()
            grouped.setdefault(record_id, set()).add(value)

        result = {
            'conflicts': [
                {'id': record_id, 'values': sorted(grouped[record_id])}
                for record_id in sorted(grouped)
                if len(grouped[record_id]) >= 2
            ]
        }
        output = json.dumps(result, ensure_ascii=True, separators=(',', ':'))
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    # Output-write failures are deliberately outside the input-error guarantee.
    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
