# FreeCAD Cross-Platform Macro Development Guidelines

(Target: macOS Development → Windows Deployment)

## 1. コーディング規約（OS差異の完全吸収）

AIにコード生成を依頼する際、および自身で実装する際は以下のルールを厳守する。

### 1.1 パス操作（最重要）

* **文字列によるパス結合の禁止:** `\` や `/` をハードコードしない。
* **`pathlib.Path` の徹底:** ファイル入出力、マクロディレクトリ参照、アイコン読み込み等はすべて `pathlib.Path` を使用する。

```python
from pathlib import Path
import FreeCAD

# GOOD:
macro_dir = Path(FreeCAD.getUserMacroDir())
target_file = macro_dir / "data" / "output.dxf"

# BAD:
# target_file = FreeCAD.getUserMacroDir() + "/data/output.dxf"

```

### 1.2 依存関係と環境の閉鎖性

* **外部 `pip` パッケージへの依存禁止:** 会社のWindows環境で `pip install` が通らない・権限がない前提で設計する。
* **標準同梱モジュールのみで完結:**
* Python標準ライブラリ（`os`, `sys`, `json`, `math`, `pathlib`, `re` 等）
* FreeCAD内蔵モジュール（`FreeCAD`, `FreeCADGui`, `Part`, `Draft`, `Sketcher` 等）
* Qt関連: `PySide` または `FreeCADGui.PySideUic`



### 1.3 文字コードと改行コード

* **エンコーディング:** すべてのソースファイルは `UTF-8`（BOMなし）とする。
* **改行コード:** 原則 `LF` で統一（Git側で `core.autocrlf = true` 等に設定）。
* **ファイル読み書き:** `open()` を呼ぶ際は必ず `encoding="utf-8"` を明示する。

```python
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

```

### 1.4 GUI & スタイリング（PySide / QSS）

* **固定ピクセル指定の禁止:** OSごとの解像度やスケーリング（HiDPI）の差異を考慮し、フォントやウィジェット幅を `px` で固定しない。
* **相対単位の利用:** サイズ指定は `pt` やレイアウトマネージャー（`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`）の伸縮比率（Stretch）に任せる。
* **フォント指定:** 特定のシステムフォント（`Hiragino`, `MS Gothic` など）を直接指定せず、システムデフォルトまたは総称ファミリを指定する。

### 1.5 ショートカットキーと修飾キー

* 修飾キーの判定が必要な場合は、プラットフォームを判定して動的に切り替える。

```python
import sys
from PySide import QtCore

MODIFIER_KEY = (
    QtCore.Qt.MetaModifier
    if sys.platform == "darwin"
    else QtCore.Qt.ControlModifier
)

```

---

## 2. 開発・バージョン管理規約

* **開発の主権はMac側:**
* 開発、リファクタリング、機能追加はすべてMac（プライベート環境）で行う。
* Windows側は「検証・実行」のみとし、原則としてWindows側でコードを直接編集しない。


* **リポジトリ管理:**
* ソースコードはGitHub（プライベートまたはオープンソースリポジトリ）で一元管理する。
* ライセンスを明確化するため、リポジトリ直下に `LICENSE`（例: MIT License）を配置する。


* **`.gitignore` の必須設定:**
* `__pycache__/`, `*.pyc`, `.DS_Store`, `Thumbs.db` 等のOS依存ゴミファイルをコミット対象から除外する。



---

## 3. 会社環境（Windows）持ち込み・運用ルール

* **持ち込み経路の透明化:**
* 私用USBメモリや未承認クラウドストレージは使用しない。
* リポジトリをGitHub等のパブリック／正規アクセス可能な場所からクローン、またはZIPダウンロードして配置する。


* **プレーンテキストの維持:**
* セキュリティ審査やコードレビューで不審がられないよう、`.exe` 化などは行わず、常に中身が読めるプレーンな `.py` / `.FCMacro` のまま配備する。


* **職務著作の分離:**
* 会社の業務時間中・会社PC上で機能追加や大規模改修を行わない（改変箇所の権利が会社側に帰属するリスクを防ぐため）。
* 会社PCで発見したバグや改善点はIssueやメモに残し、自宅のMacで修正・コミットしたものを再度プルする。



---

## 4. AI（Claude等）への指示用プロンプト・スニペット

FreeCAD用スクリプトをAIに生成させる際は、以下の指示をプロンプトの冒頭またはSystem Promptに付与する。

> **AIへの指示テンプレート:**
> FreeCAD 1.0以降で動作するPythonスクリプト（またはマクロ）を作成してください。
> 以下のクロスプラットフォーム要件を厳守してください：
> 1. **OS非依存:** macOSとWindowsの両方で修正なしで動作すること。パス処理には必ず `pathlib.Path` を使用し、ハードコードされたスラッシュを使わないこと。
> 2. **依存性:** 外部 `pip` パッケージを使わず、FreeCAD標準内包のモジュール（`FreeCAD`, `FreeCADGui`, `Part`, `Draft` 等）と標準ライブラリ、`PySide` のみで実装すること。
> 3. **UI設計:** PySideでUIを作成する場合、フォントやレイアウトはOS標準スケーリングに対応できるよう相対配置・レイアウトマネージャーベースとすること。