import csv
import io


def inspect_csv(text, required_columns):
    """Validate CSV structure and report repeated rows (1-based record numbers)."""
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    header = next(reader, None)
    if not header:
        raise ValueError("CSV is empty")

    header[0] = header[0].removeprefix("\ufeff")
    if any(not name.strip() for name in header):
        raise ValueError("Empty column name")
    if len(set(header)) != len(header):
        raise ValueError("Repeated column name")

    missing = sorted(set(required_columns) - set(header))
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    seen = {}
    duplicates = []
    count = 0
    for record_number, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise ValueError(f"Wrong column count in record {record_number}")
        count += 1
        key = tuple(row)
        if key in seen:
            duplicates.append({
                "record": record_number,
                "first_record": seen[key],
            })
        else:
            seen[key] = record_number

    return {"rows": count, "duplicates": duplicates}
