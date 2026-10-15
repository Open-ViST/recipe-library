#!/usr/bin/env python3
import argparse
import json
import math
import sys


class InputError(Exception):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise InputError("provide exactly one nonempty field name")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("duplicate object key")
        result[key] = value
    return result


def reject_constant(token):
    raise InputError("non-finite numeric constant")


def finite_float(token):
    value = float(token)
    if not math.isfinite(value):
        raise InputError("numeric token exceeds the finite float range")
    return value


def prepare_output():
    parser = Parser(add_help=False, allow_abbrev=False)
    parser.add_argument("field")
    args = parser.parse_args()
    if args.field == "":
        raise InputError("field name must not be empty")

    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise InputError("input exceeds 65536 bytes")
    text = raw.decode("utf-8", errors="strict")
    data = json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )
    if not isinstance(data, list):
        raise InputError("top-level JSON value must be an array")

    counts = {}
    for record in data:
        if not isinstance(record, dict):
            raise InputError("every array element must be an object")
        if args.field not in record:
            raise InputError("a record is missing the selected field")
        value = record[args.field]
        if not isinstance(value, str) or value == "":
            raise InputError("every selected field must be a nonempty string")
        counts[value] = counts.get(value, 0) + 1

    result = {
        "records": len(data),
        "groups": [
            {"value": value, "count": counts[value]}
            for value in sorted(counts)
        ],
    }
    return json.dumps(result, ensure_ascii=True, allow_nan=False) + "\n"


def main():
    try:
        output = prepare_output()
    except InputError as exc:
        sys.stderr.write("error: " + str(exc) + "\n")
        return 2
    except (ValueError, OverflowError, RecursionError):
        sys.stderr.write("error: invalid JSON, UTF-8, or parser limit exceeded\n")
        return 2
    except OSError:
        sys.stderr.write("error: unable to read stdin\n")
        return 2
    except MemoryError:
        sys.stderr.write("error: insufficient memory to process input\n")
        return 2

    sys.stdout.write(output)
    sys.stdout.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
