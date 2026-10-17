import sys
import json


def valid_key(key):
    if not 1 <= len(key) <= 64:
        return False
    first = key[0]
    if not ('A' <= first <= 'Z' or 'a' <= first <= 'z' or first == '_'):
        return False
    for char in key[1:]:
        if not ('A' <= char <= 'Z' or 'a' <= char <= 'z' or '0' <= char <= '9' or char == '_'):
            return False
    return True


def audit(text):
    if text.startswith('\ufeff'):
        raise ValueError
    for char in text:
        number = ord(char)
        if (number < 32 and number != 10) or number == 127:
            raise ValueError

    required = set()
    positions = {}
    empty_values = set()
    separator_seen = False
    assignment_count = 0
    value_bytes = 0

    for line in text.split('\n'):
        if line == '' or line.startswith('#'):
            continue
        if line == '---':
            if separator_seen:
                raise ValueError
            separator_seen = True
            continue

        if not separator_seen:
            if not valid_key(line) or line in required or len(required) >= 100:
                raise ValueError
            required.add(line)
            continue

        assignment_count += 1
        if assignment_count > 100:
            raise ValueError
        key, delimiter, value = line.partition('=')
        if delimiter != '=' or not valid_key(key):
            raise ValueError
        value_bytes += len(value.encode('utf-8'))
        if value_bytes > 1024:
            raise ValueError
        if key not in positions:
            positions[key] = []
        positions[key].append(assignment_count)
        if value == '':
            empty_values.add(key)

    if not separator_seen:
        raise ValueError

    return {
        'missing': sorted(key for key in required if key not in positions),
        'empty': sorted(required & empty_values),
        'duplicates': [
            {'key': key, 'positions': positions[key]}
            for key in sorted(positions)
            if len(positions[key]) >= 2
        ],
        'unknown': sorted(key for key in positions if key not in required),
    }


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError
        data = sys.stdin.buffer.read(65537)
        if len(data) > 65536:
            raise ValueError
        text = data.decode('utf-8', errors='strict')
        output = json.dumps(audit(text), ensure_ascii=True) + '\n'
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
