import argparse
import json
import os
import stat

MAX_BYTES = 1024 * 1024


class ValidationError(ValueError):
    pass


def reject_constant(token):
    raise ValidationError('Non-finite JSON constant is not allowed: ' + token)


def parse_finite_float(token):
    value = float(token)
    if value == float('inf') or value == float('-inf'):
        raise ValidationError('JSON number overflows to an infinite float')
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError('Duplicate object key: ' + json.dumps(key))
        result[key] = value
    return result


def load_object(path):
    # Linux: do not follow the final symlink or block opening a FIFO.
    descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValidationError('Input must be a regular local file')
        with os.fdopen(descriptor, 'rb', closefd=False) as stream:
            data = stream.read(MAX_BYTES + 1)
    finally:
        os.close(descriptor)
    if len(data) > MAX_BYTES:
        raise ValidationError('Input exceeds the 1 MiB limit')
    text = data.decode('utf-8')
    value = json.loads(
        text,
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
        parse_float=parse_finite_float,
    )
    if not isinstance(value, dict):
        raise ValidationError('Top-level JSON value must be an object')
    return value


def equal_values(left, right):
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, dict) or isinstance(right, dict):
        if not isinstance(left, dict) or not isinstance(right, dict):
            return False
        if left.keys() != right.keys():
            return False
        return all(equal_values(left[key], right[key]) for key in left)
    if isinstance(left, list) or isinstance(right, list):
        if not isinstance(left, list) or not isinstance(right, list):
            return False
        return len(left) == len(right) and all(
            equal_values(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, (int, float)) or isinstance(right, (int, float)):
        return (
            isinstance(left, (int, float))
            and isinstance(right, (int, float))
            and left == right
        )
    if left is None or right is None:
        return left is None and right is None
    return isinstance(left, str) and isinstance(right, str) and left == right


def child_pointer(parent, key):
    return parent + '/' + key.replace('~', '~0').replace('/', '~1')


def compare_objects(left, right, parent, result):
    for key in left:
        path = child_pointer(parent, key)
        if key not in right:
            result['removed'].append(path)
        elif isinstance(left[key], dict) and isinstance(right[key], dict):
            compare_objects(left[key], right[key], path, result)
        elif not equal_values(left[key], right[key]):
            result['changed'].append(path)
    for key in right:
        if key not in left:
            result['added'].append(child_pointer(parent, key))


def main():
    parser = argparse.ArgumentParser(
        description='Compare two UTF-8 JSON objects without modifying either input.'
    )
    parser.add_argument('before', help='Original JSON file')
    parser.add_argument('after', help='New JSON file')
    args = parser.parse_args()
    try:
        before = load_object(args.before)
        after = load_object(args.after)
        result = {'added': [], 'removed': [], 'changed': []}
        compare_objects(before, after, '', result)
        for paths in result.values():
            paths.sort()
        output = json.dumps(result, ensure_ascii=True, allow_nan=False)
    except (OSError, ValueError, RecursionError, OverflowError) as error:
        parser.exit(2, 'error: ' + str(error) + '\n')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
