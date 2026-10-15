import json
import sys
import math


def reject_constant(text):
    raise ValueError('invalid input')


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError('invalid input')
    return value


def process_input():
    if len(sys.argv) != 1:
        raise ValueError('invalid input')

    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536 or raw.startswith(b'\xef\xbb\xbf'):
        raise ValueError('invalid input')
    text = raw.decode('utf-8', errors='strict')
    records = json.loads(
        text,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )

    if not isinstance(records, list) or len(records) > 20:
        raise ValueError('invalid input')

    intervals = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError('invalid input')
        if 'start' not in record or 'end' not in record:
            raise ValueError('invalid input')
        start = record['start']
        end = record['end']
        for value in (start, end):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('invalid input')
            if not 0 <= value <= 1000000000:
                raise ValueError('invalid input')
        if start >= end:
            raise ValueError('invalid input')
        intervals.append((start, end))

    overlaps = []
    for i in range(len(intervals)):
        for j in range(i + 1, len(intervals)):
            start = max(intervals[i][0], intervals[j][0])
            end = min(intervals[i][1], intervals[j][1])
            if start < end:
                overlaps.append({
                    'first': i + 1,
                    'second': j + 1,
                    'start': start,
                    'end': end,
                })
    return {'overlaps': overlaps}


def main():
    try:
        result = process_input()
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    sys.stdout.write(json.dumps(result, separators=(',', ':')) + '\n')
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
