from __future__ import annotations

import argparse
from pathlib import Path

from mpack_codec import unpack_tree


def main() -> int:
    parser = argparse.ArgumentParser(description="Unpack Unity .mpack save files into JSON.")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Folder with .mpack files (default: current directory).", 
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("unpacked_json"),
        help="Output folder relative to --root (default: unpacked_json).",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    out_root = (root / args.out).resolve() if not args.out.is_absolute() else args.out.resolve()

    files = sorted(root.rglob("*.mpack"))
    if not files:
        print("No .mpack files found.")
        return 0

    print(f"Found {len(files)} mpack files under: {root}")
    print(f"Output directory: {out_root}")

    results = unpack_tree(root, out_root)
    ok_count = 0
    fail_count = 0
    for source, output, err in results:
        rel = source.relative_to(root)
        if err:
            print(f"ERR {rel}: {err}")
            fail_count += 1
        else:
            print(f"OK  {rel} -> {output.relative_to(root)}")
            ok_count += 1

    print(f"Done. success={ok_count}, failed={fail_count}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
