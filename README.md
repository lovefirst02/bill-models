# bill-models

台電帳單專用的文字偵測與讀字模型：訓練程式與模型發佈。使用這些模型的程式在
[taipower-bill-ocr](https://github.com/lovefirst02/taipower-bill-ocr)。

訓練只用程式產生的合成資料，沒有真實帳單。

## 只想用模型

到 [Releases](https://github.com/lovefirst02/bill-models/releases) 下載。每版都有 `models.json`，記錄每個檔案的 SHA-256。

| 檔案 | 用途 |
|---|---|
| `bill_detector.onnx` | 找出帳單上每一行字（自訓練） |
| `bill_reader.onnx`、`bill_reader.chars.json` | 讀字，只認帳單會印的字（自訓練） |
| `PP-OCRv6_small_det.onnx`、`PP-OCRv6_small_rec.onnx`、`PP-OCRv6_small_rec.chars.json` | App 的 Fast 模式讀其他文件用。由 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 的模型轉換，不是這裡訓練的，授權依 PaddleOCR |

## 訓練

需要 Windows（字型取自 `C:\Windows\Fonts`，不隨附）和 NVIDIA GPU。

```powershell
uv venv --python 3.12
uv pip install torch --index-url https://download.pytorch.org/whl/cu126
uv pip install -r pyproject.toml

# 讀字模型：約 85 分鐘（30000 步）
uv run --no-sync python training/train.py --out out/reader1 --steps 30000
# 從上一版接著訓練（字集變大時，舊字保留原本的輸出權重，新字從頭學）
uv run --no-sync python training/train.py --out out/reader2 --steps 30000 --lr 3e-4 --init out/reader1/best.pt

# 偵測模型
uv run --no-sync python training/train_det.py --out out/det1 --steps 20000

# 在瀏覽器看訓練進度
uv run --no-sync python training/monitor.py out/reader1 --steps 30000 --port 8770
```

每個 `--out` 資料夾會有 `.pt` 檢查點、`.onnx` 模型和 `log.jsonl`。

| 檔案 | 內容 |
|---|---|
| `training/synth.py` | 讀字模型的合成資料 |
| `training/synth_det.py` | 偵測模型的合成資料 |
| `training/train.py` | 訓練讀字模型 |
| `training/train_det.py` | 訓練偵測模型 |
| `training/eval_reads.py` | 只評估讀字模型 |
| `training/monitor.py` | 訓練進度頁 |
| `tools/convert_ppocr.py` | 把 PP-OCR 模型轉成 ONNX |
| `tools/make_manifest.py` | 產生 `models.json` |

### 和主程式的關係

讀字模型要認得的字來自 [bill-reader](https://github.com/lovefirst02/bill-reader) 的 `vocabulary.py`，
偵測設定來自主程式的 `onnx_ocr.py`，所以這裡依賴固定版本的 `bill-reader` 和 `taipower-bill-ocr`（見 `pyproject.toml`）。

`training/synth.py` 的 `FOCUS` 是比較常抽到的標籤：新加的標籤，和長得像、容易讀混的標籤。

- **新增標籤，字都已學過：** 只改 bill-reader。
- **標籤有新字：** 更新這裡依賴的版本，重新訓練。

## 換模型的流程

1. 訓練。合成資料的準確率只代表合成資料，不能當成真實表現。
2. 用主程式 `evaluation/` 的腳本，在真實帳單、照片和多種尺寸上和目前的模型比較。
3. 確實比較好才發佈新版：

   ```powershell
   python tools/make_manifest.py v1.1.0 path\to\models > models.json
   gh release create v1.1.0 path\to\models\* models.json
   ```

4. 更新主程式記錄的模型版本和 SHA-256。

## 版本紀錄

### v1.1.0

讀字模型認得 229 個字，多了「上」「餘」「設」「施」，讀得出「上期預繳餘額」「本期預繳餘額」「本期預繳金額」「公共設施電費」。
偵測模型和 PP-OCR 模型與 v1.0.0 相同。

| 模型 | 來源 | 合成資料分數 |
|---|---|---|
| 讀字 | 第 5 輪，30000 步，學習率 3e-4，接續 v1.0.0（第 2 輪），新標籤和相近標籤多抽 | 準確率約 98.8% |

真實帳單和照片 370 頁，與 v1.0.0 比較：有正確答案的 186 頁、2469 個欄位，讀對從 2404 個變成 2408 個，沒有欄位變差。
不會再把「本期指數」讀成「本期預繳」。少數低解析度的掃描和照片變差，例如一頁把「流動電費」讀成「流共電費」。

第 4 輪（學習率 5e-4、沒有多抽）在有正確答案的頁面少了 4 個欄位，沒有採用。

### v1.0.0

主程式 `v0.25.0-docs` 使用的模型，內容和當時完全相同。

| 模型 | 來源 | 合成資料分數 |
|---|---|---|
| 讀字 | 第 2 輪，30000 步，接續第 1 輪 | 準確率約 98.5% |
| 偵測 | 第 2 輪，25000 步，接續第 1 輪 | F1 約 0.98 |

- 這版讀字模型認得 211 個字。目前的 `bill_vocabulary.py` 有 226 個字（多了表格版用詞），從現在的程式重新訓練會得到 226 個字。
- 曾用 226 個字訓練過第 3 輪：表格版變好，但照片退步、會把金額讀成負數，所以沒有採用。

## 已知限制

- 偵測和讀字都沒有用真實帳單訓練，表現要以主程式在真實帳單上的評估為準。
- 訓練依賴 Windows 字型，換電腦或換字型結果可能不同。
- 沒有固定所有亂數來源，重新訓練不保證得到完全相同的模型。
