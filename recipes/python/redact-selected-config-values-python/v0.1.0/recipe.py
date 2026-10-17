import sys
import json


def valid_key(key):
    if not 1 <= len(key) <= 64:
        return False
    first = key[0]
    if not ('A' <= first <= 'Z' or 'a' <= first <= 'z' or first == '_'):
        return False
    return all(
        'A' <= ch <= 'Z' or 'a' <= ch <= 'z' or
        '0' <= ch <= '9' or ch == '_'
        for ch in key[1:]
    )


def parse(data):
    if len(data) > 65536:
        raise ValueError
    text = data.decode('utf-8', errors='strict')
    if text.startswith('\ufeff'):
        raise ValueError
    for ch in text:
        number = ord(ch)
        if (number < 32 and ch != '\n') or number == 127:
            raise ValueError

    selectors = set()
    assignments = []
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
            if not valid_key(line) or line in selectors:
                raise ValueError
            selectors.add(line)
            if len(selectors) > 100:
                raise ValueError
            continue

        assignment_count += 1
        if assignment_count > 100 or '=' not in line:
            raise ValueError
        key, value = line.split('=', 1)
        if not valid_key(key):
            raise ValueError
        value_bytes += len(value.encode('utf-8'))
        if value_bytes > 1024:
            raise ValueError
        assignments.append({
            'key': key,
            'value': '[REDACTED]' if key in selectors else value
        })

    if not separator_seen:
        raise ValueError
    return {'assignments': assignments}


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError
        data = sys.stdin.buffer.read(65537)
        result = parse(data)
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    output = json.dumps(result, ensure_ascii=True) + '\n'
    sys.stdout.write(output)
    return 0


if __name__ == '__main__':
    sys.exit(main())
