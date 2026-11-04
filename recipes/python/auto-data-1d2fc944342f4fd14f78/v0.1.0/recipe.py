import sys
import json
import re


NAME = re.compile(r"[a-z][a-z0-9_-]{0,19}", re.ASCII)
FIELDS = {"group", "value", "weight", "tag"}


def reject_number(text):
    raise ValueError("Unsupported number")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate key")
        result[key] = value
    return result


def prepare_output():
    if len(sys.argv) != 1:
        raise ValueError("Arguments are not accepted")

    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise ValueError("Input exceeds byte limit")
    text = raw.decode("utf-8", errors="strict")
    if text.startswith("\ufeff"):
        raise ValueError("Leading BOM")

    records = json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_float=reject_number,
        parse_constant=reject_number,
    )

    if (not (isinstance(records, list))) or len(records) > 40:
        raise ValueError("Expected at most 40 records")

    for record in records:
        if (not (isinstance(record, dict))) or set(record) != FIELDS:
            raise ValueError("Invalid record fields")
        for field in ("group", "tag"):
            value = record[field]
            if (not (isinstance(value, str))) or NAME.fullmatch(value) is None:
                raise ValueError("Invalid name")
        value = record["value"]
        weight = record["weight"]
        if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
            raise ValueError("Invalid value")
        if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
            raise ValueError("Invalid weight")

    inventories = {}
    for record in records:
        group = record["group"]
        if group not in inventories:
            inventories[group] = set()
        inventories[group].add(record["tag"])

    result = {
        "groups": [
            {"group": group, "tags": sorted(inventories[group])}
            for group in sorted(inventories)
        ]
    }
    return json.dumps(result, ensure_ascii=True, separators=(",", ":")) + "\n"


def main():
    try:
        output = prepare_output()
    except Exception:
        sys.stderr.write("error: invalid input or input read failure\n")
        return 2

    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
