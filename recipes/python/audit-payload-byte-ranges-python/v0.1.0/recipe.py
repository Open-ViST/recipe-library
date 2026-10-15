import json
import sys
import math


def reject_constant(_value):
    raise ValueError("invalid JSON number")


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("invalid JSON number")
    return value


def valid_integer(value, minimum, maximum):
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and minimum <= value <= maximum
    )


def process():
    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise ValueError("input too large")

    text = raw.decode("utf-8", errors="strict")
    if text.startswith("\ufeff"):
        raise ValueError("leading BOM")

    data = json.loads(
        text,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )
    if not isinstance(data, dict):
        raise ValueError("invalid structure")

    size = data.get("size")
    ranges = data.get("ranges")
    if not valid_integer(size, 0, 1000000000):
        raise ValueError("invalid size")
    if not isinstance(ranges, list) or len(ranges) > 100:
        raise ValueError("invalid ranges")

    out_of_bounds = []
    for position, item in enumerate(ranges, start=1):
        if not isinstance(item, dict):
            raise ValueError("invalid range")
        start = item.get("start")
        length = item.get("length")
        if not valid_integer(start, 0, 1000000000):
            raise ValueError("invalid start")
        if not valid_integer(length, 1, 1000000000):
            raise ValueError("invalid length")
        if start + length > size:
            out_of_bounds.append(position)

    return {
        "range_count": len(ranges),
        "out_of_bounds": out_of_bounds,
        "within_bounds": not out_of_bounds,
    }


def fail():
    sys.stderr.write("error: invalid input\n")
    sys.exit(2)


def main():
    if len(sys.argv) != 1:
        fail()
    try:
        result = process()
    except Exception:
        fail()

    sys.stdout.write(json.dumps(result, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
