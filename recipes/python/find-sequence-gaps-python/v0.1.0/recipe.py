import json
import sys
import math


def reject_constant(_value):
    raise ValueError()


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError()
    return value


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError()

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536 or raw.startswith(b'\xef\xbb\xbf'):
            raise ValueError()

        text = raw.decode('utf-8', errors='strict')
        values = json.loads(
            text,
            parse_constant=reject_constant,
            parse_float=finite_float,
        )

        if not isinstance(values, list) or len(values) > 1000:
            raise ValueError()

        previous = None
        for value in values:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError()
            if value < 0 or value > 1000000000:
                raise ValueError()
            if previous is not None and value <= previous:
                raise ValueError()
            previous = value

        gaps = []
        missing_count = 0
        previous = None
        for value in values:
            if previous is not None and value > previous + 1:
                start = previous + 1
                end = value - 1
                gaps.append({'start': start, 'end': end})
                missing_count += end - start + 1
            previous = value

        output = json.dumps(
            {'gaps': gaps, 'missing_count': missing_count},
            separators=(',', ':'),
            allow_nan=False,
        ) + '\n'
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    sys.stdout.write(output)
    sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
