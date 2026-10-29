import sys
import json


def invalid():
    sys.stderr.write('error: invalid input\n')
    sys.exit(2)


def decimal(token, max_digits, maximum):
    if not token or len(token) > max_digits:
        raise ValueError
    if len(token) > 1 and token[0] == '0':
        raise ValueError
    if any(c < '0' or c > '9' for c in token):
        raise ValueError
    value = int(token)
    if value > maximum:
        raise ValueError
    return value


def dotted(value):
    return '.'.join(str((value >> shift) & 255)
                    for shift in (24, 16, 8, 0))


def parse_record(record):
    parts = record.split('/')
    if len(parts) != 2:
        raise ValueError
    octets = parts[0].split('.')
    if len(octets) != 4:
        raise ValueError
    a, b, c, d = (decimal(token, 3, 255) for token in octets)
    prefix = decimal(parts[1], 2, 32)
    address = a * 16777216 + b * 65536 + c * 256 + d
    size = 1 << (32 - prefix)
    network = (address // size) * size
    last = network + size - 1
    return {
        'input': record,
        'network': dotted(network),
        'last': dotted(last),
        'prefix': prefix,
        'address_count': size,
        'host_bits_set': address != network,
    }


def main():
    if len(sys.argv) != 1:
        invalid()

    try:
        raw = sys.stdin.buffer.read(65537)
    except Exception:
        invalid()

    try:
        if len(raw) > 65536:
            raise ValueError
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff') or not text.isascii():
            raise ValueError

        networks = []
        for record in text.split('\n'):
            if record == '':
                continue
            if len(networks) >= 100:
                raise ValueError
            networks.append(parse_record(record))
    except ValueError:
        invalid()

    output = json.dumps({'networks': networks}, separators=(',', ':'))
    sys.stdout.write(output + '\n')
    sys.exit(0)


if __name__ == '__main__':
    main()
