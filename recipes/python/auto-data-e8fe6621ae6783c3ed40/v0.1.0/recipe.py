import sys
import json
import re


def reject_number(text):
    raise ValueError('Unsupported numeric value')


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate object key')
        result[key] = value
    return result


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError('CLI arguments are not supported')

        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError('Input exceeds byte limit')
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff'):
            raise ValueError('Leading BOM is not allowed')

        records = json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
        if (not (isinstance(records, list))) or len(records) > 40:
            raise ValueError('Expected an array of at most 40 records')

        required_keys = {'group', 'value', 'weight', 'tag'}
        identifier = re.compile(r'[a-z][a-z0-9_-]{0,19}')
        for record in records:
            if (not (isinstance(record, dict))) or set(record) != required_keys:
                raise ValueError('Invalid record fields')
            for field in ('group', 'tag'):
                value = record[field]
                if (not (isinstance(value, str))) or identifier.fullmatch(value) is None:
                    raise ValueError('Invalid group or tag')
            value = record['value']
            weight = record['weight']
            if (not ((isinstance(value, int) and not isinstance(value, bool)))) or not -1000000 <= value <= 1000000:
                raise ValueError('Invalid value')
            if (not ((isinstance(weight, int) and not isinstance(weight, bool)))) or not -1000 <= weight <= 1000:
                raise ValueError('Invalid weight')

        balances = {}
        output_records = []
        for record in records:
            if record['value'] <= 0:
                continue
            group = record['group']
            balance = balances.get(group, 0) + record['value']
            balances[group] = balance
            output_record = record.copy()
            output_record['running_total'] = balance
            output_records.append(output_record)

        output = json.dumps(
            {'records': output_records},
            ensure_ascii=True,
            allow_nan=False,
            separators=(',', ':'),
        ) + '\n'
    except Exception:
        sys.stderr.write('error: invalid input or input read failure\n')
        return 2

    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
