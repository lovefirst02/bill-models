"""PaddleOCR's PP-OCRv6 small models as ONNX: the general reader of the app's Fast mode.

Not trained here. In an environment of its own, as they pin old versions:

    uv pip install paddlepaddle==3.2.0 paddle2onnx==2.1.0 onnx onnxruntime pyyaml
    python tools/convert_ppocr.py out/ppocr

The models come from %USERPROFILE%/.paddlex/official_models, where PaddleOCR
downloads them on its first run.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

MODELS = ("PP-OCRv6_small_det", "PP-OCRv6_small_rec")


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    source = Path.home() / ".paddlex" / "official_models"
    for name in MODELS:
        subprocess.run(["paddle2onnx", "--model_dir", str(source / name), "--model_filename", "inference.json",
                        "--params_filename", "inference.pdiparams", "--save_file", str(out / f"{name}.onnx"),
                        "--opset_version", "14"], check=True)
    settings = yaml.safe_load((source / MODELS[1] / "inference.yml").read_text(encoding="utf-8"))
    characters = settings["PostProcess"]["character_dict"]
    (out / f"{MODELS[1]}.chars.json").write_text(json.dumps(characters, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
