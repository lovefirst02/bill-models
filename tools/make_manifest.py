"""models.json for a release: what is in it and each file's SHA-256, which the apps check on download.

    python tools/make_manifest.py v1.0.0 path/to/models > models.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ORDER = ("bill_detector.onnx", "bill_reader.onnx", "bill_reader.chars.json",
         "PP-OCRv6_small_det.onnx", "PP-OCRv6_small_rec.onnx", "PP-OCRv6_small_rec.chars.json")


def main() -> None:
    version, folder = sys.argv[1], Path(sys.argv[2])
    files = {name: {"sha256": hashlib.sha256((folder / name).read_bytes()).hexdigest(), "bytes": (folder / name).stat().st_size}
             for name in ORDER}
    json.dump({"version": version, "files": files}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
