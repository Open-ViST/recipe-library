import sys
import json


def decimal(token, max_digits, maximum):
    if not token or len(token) > max_digits:
        raise ValueError
    if len(token) > 1 and token[0] == '0':
        raise ValueError
    value = 0
    for char in token:
        if not ('0' <= char <= '9'):
            raise ValueError
        value = value * 10 + (ord(char) - ord('0'))
    if value > maximum:
        raise ValueError
    return value


def ipv4(token):
    parts = token.split('.')
    if len(parts) != 4:
        raise ValueError
    a, b, c, d = [decimal(part, 3, 255) for part in parts]
    return a * 16777216 + b * 65536 + c * 256 + d


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError
        raw = sys.stdin.buffer.read(65537)
        if len(raw) > 65536:
            raise ValueError
        text = raw.decode('utf-8', errors='strict')
        if text.startswith('\ufeff') or not text.isascii():
            raise ValueError

        checks = []
        for line in text.split('\n'):
            if line == '':
                continue
            if len(checks) >= 100:
                raise ValueError
            fields = line.split(' ')
            if len(fields) != 2:
                raise ValueError
            address_text, cidr_text = fields
            address = ipv4(address_text)
            cidr_parts = cidr_text.split('/')
            if len(cidr_parts) != 2:
                raise ValueError
            network_text, prefix_text = cidr_parts
            supplied_network = ipv4(network_text)
            prefix = decimal(prefix_text, 2, 32)
            size = 1 << (32 - prefix)
            network = (supplied_network // size) * size
            if supplied_network != network:
                raise ValueError
            last = network + size - 1
            checks.append({
                'address': address_text,
                'cidr': cidr_text,
                'contains': network <= address <= last
            })
    except Exception:
        sys.stderr.write('error: invalid input\n')
        return 2

    output = json.dumps({'checks': checks}, separators=(',', ':'))
    sys.stdout.write(output + '\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
