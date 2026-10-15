# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OpenViST contributors
"""Record relative paths, sizes and SHA-256 hashes for a trusted local folder."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

MAX_FILES = 10000
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024


def manifest(folder):
    root = Path(folder)
    if root.is_symlink() or not root.is_dir():
        raise ValueError("input must be a real folder, not a symlink")
    root = root.resolve()
    paths, skipped = [], []

    def cannot_walk(error):
        raise error

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=cannot_walk):
        base = Path(directory)
        dirs.sort()
        for name in list(dirs):
            path = base / name
            if path.is_symlink():
                skipped.append(path.relative_to(root).as_posix())
                dirs.remove(name)
        for name in sorted(files):
            path = base / name
            if path.is_symlink():
                skipped.append(path.relative_to(root).as_posix())
            elif path.is_file():
                paths.append(path)
            else:
                raise ValueError("non-regular file: " + path.relative_to(root).as_posix())
            if len(paths) > MAX_FILES or len(skipped) > MAX_FILES:
                raise ValueError("folder exceeds the file or skipped-link limit")
    records, total = [], 0
    for path in sorted(paths, key=lambda p: p.relative_to(root).as_posix()):
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        with os.fdopen(os.open(path, flags), "rb") as stream:
            before = os.fstat(stream.fileno())
            if before.st_size > MAX_FILE_BYTES or total + before.st_size > MAX_TOTAL_BYTES:
                raise ValueError("folder exceeds the byte limits")
            digest, size = hashlib.sha256(), 0
            while True:
                block = stream.read(65536)
                if not block:
                    break
                size += len(block)
                if size > MAX_FILE_BYTES or total + size > MAX_TOTAL_BYTES:
                    raise ValueError("file grew beyond the byte limits")
                digest.update(block)
            after = os.fstat(stream.fileno())
            if size != before.st_size or after.st_size != before.st_size or after.st_mtime_ns != before.st_mtime_ns:
                raise ValueError("a file changed while being read")
        total += size
        records.append({"path": path.relative_to(root).as_posix(), "bytes": size, "sha256": digest.hexdigest()})
    return {"files": records, "total_bytes": total, "skipped_symlinks": sorted(skipped)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder")
    args = parser.parse_args()
    try:
        print(json.dumps(manifest(args.folder), ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
