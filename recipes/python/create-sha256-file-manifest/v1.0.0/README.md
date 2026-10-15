# Create a SHA-256 manifest for a local folder

Record relative paths, file sizes and SHA-256 digests so a later copy can be compared with the original.

Published recipe: [create-sha256-file-manifest](https://openvist.com/recipes/create-sha256-file-manifest/)

**Language:** python · **Version:** 1.0.0 · **License:** MIT

## Usage

Code file: `recipe.py`

See requirements below.

## Requirements

- Python 3.10 or later; standard library only.
- A trusted, stable local folder that is not a symlink.
- Up to 10,000 files, 64 MiB per file and 256 MiB total; skipped links are bounded too.

## Steps

- Choose a folder and stop changes while taking the inventory.
- Run: python hash_manifest.py folder > manifest.json
- Write manifest.json outside the scanned folder so it is not included in a future inventory.
- Repeat for a later copy and compare relative paths, byte sizes and SHA-256 values.

## Checks

- Compare the digest of a known small file and an empty file.
- Confirm deterministic ordering, nested relative paths and skipped symlinks.
- Missing folders and count or byte-limit violations must return a nonzero exit status.

## Limits

- An integrity inventory is not a backup, signature or proof of authenticity. It does not restore files.
- Symlinks are skipped; permissions, empty directories and extended attributes are not recorded.
- The stable-folder assumption matters. This is not a locked filesystem snapshot or protection against an adversary changing paths while they are read.

## Recorded validation scope

Executed locally with deterministic fixtures and CLI checks on Python 3.12.14. The three scripts pass 22 tests covering valid output, invalid input and size limits. No network or provider call was made.

This scope is copied from the published recipe. Exporting does not rerun its tests or establish additional guarantees.

## Sources

- https://docs.python.org/3/library/hashlib.html
- https://docs.python.org/3/library/pathlib.html
