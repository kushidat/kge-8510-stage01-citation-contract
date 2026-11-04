#!/usr/bin/env python3
"""Build an UNPUBLISHED disabled-GUI candidate from the immutable public release.
The source-only v0.2.0 release stays intact. This is not a Provider-enabled build.
"""
import ast, csv, hashlib, io, zlib
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

URL=("https://github.com/kushidat/kge-8510-stage01-citation-contract/"
     "releases/download/8510-stage01-v0.2.0/"
     "KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip")
RELEASE_SHA="bf68b4176dfb8c05295dab1c7636307ac775a872d7b660cfd4b22517ffad9f26"
SPOOL_SHA="e7d89291ab6286b008d91ef0b50b2def4587e879a091de69e7b4222685be00d3"
SPOOL="source/gui_v02_fix1/kge_v11_spool_bridge_v0_1.py"
OUTPUT=Path("candidate/8510_STAGE01_V02_DISABLED_PREVIEW_QA_CANDIDATE.zip")
def sha(b):return hashlib.sha256(b).hexdigest()
MANUAL="""# 8510 Stage01 V02 — 隔離・無効化GUIプレビュー候補

**対象**：疾患–マウス候補の引用契約を確認する開発用画面の表示。
本ZIPは、正式8510 v1.0を置換するアプリではなく、実Provider連携、8504 G4承認、研究データ参照が一切できない**無効化プレビュー**です。研究的・臨床的有効性は未評価です。

## 1. 動作環境
macOSまたはLinux、Python 3.12、pip、venv、依存パッケージを取得するネットワーク接続が必要です。検証済み実機環境はGitHub ActionsのLinux/Python 3.12であり、**ユーザーMacでは未検証**です。既存の研究用venv、Docker、Streamlitポートを変更しないでください。

## 2. 新しい隔離フォルダへの展開とインストール
1. ZIPのSHA256とREADMEの版番号を照合してください。
2. 空の新規フォルダへ展開します（既存ファイルは上書きしない）。
3. Terminalで展開先へ移動し、次を実行します。

    python3 -m venv .preview_venv
    .preview_venv/bin/python -m pip install -r requirements-preview.txt

4. プレビューを起動します。

    bash RUN_DISABLED_PREVIEW.command

5. ブラウザで `http://127.0.0.1:18610` を開き、画面タイトル、`STAGE01_V02_RUNTIME_DISABLED`、ユーザーID未設定、有効なSEND・APPROVEボタンがないことを確認してください。

既に18610番が使用されている場合、稼働中のサービスを停止せず、`bash RUN_DISABLED_PREVIEW.command 18611` で別ポートを使用してください。起動コマンドは前景実行です。

## 3. 終了・再起動
起動コマンドを実行した**同じTerminalでControl-C**を押してください。ブラウザを閉じるだけではStreamlitサーバーは終了しません。再表示は再度起動コマンドを実行します。8501/8504/正式8510のコンテナ停止・再起動は不要・禁止です。

## 4. 利用者向け基本操作と制限
- この版で可能：無効化状態のGUI表示、説明文、引用契約画面の確認。
- この版で不可能：APIキー登録、実Provider送信、8504からの承認済み実データ入力、G4受入、疾患モデルの科学的評価。
- 秘密情報、OpenAI APIキー、研究原本、PRIMARY_TEST、validation/test/withheldを配置・入力しないでください。
- 旧Stage01 V01の要求を再送しないでください。正式8510へ統合しないでください。

## 5. 検証範囲と障害時の対応
GitHub ActionsではZIP CRC/SHA256/サイズ、6 Pythonソースの構文、無効化GUIのAppTest、SEND/APPROVE無効、HTTP起動、サーバー停止、候補ZIPのハッシュmanifestを確認しました。ただしMac上でのインストール、実API、研究室内ネットワーク・OS隔離、科学的妥当性は未検証です。

起動失敗・例外が出た場合は再送・上書き・本番切替をせず、Terminalのエラーを保全してください。APIキーや機密情報をログ共有しないでください。

この候補はGitHub Actionsから取得できる検査用成果物であり、正式なGitHub Releaseへの昇格を意味しません。
"""
RUN="""#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PORT="18610"
if test "$#" -ge 1; then PORT="$1"; fi
case "$PORT" in ''|*[!0-9]*) echo INVALID_PORT >&2; exit 2;; esac
if test "$PORT" -lt 1024 || test "$PORT" -gt 65535; then echo INVALID_PORT >&2; exit 2; fi
PY="$ROOT/.preview_venv/bin/python"
if test ! -x "$PY"; then echo "MISSING_PREVIEW_VENV" >&2; exit 2; fi
export KGE_STAGE01_V02_ENABLED=NO
export APP_USER_ID=''
export ALLOW_SERVER_OPENAI_KEY=false
unset OPENAI_API_KEY
unset KEY_ENCRYPTION_SECRET
export PYTHONPATH="$ROOT/source/gui_v02_fix1"
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
"$PY" -c 'import streamlit, openai, cryptography'
echo "DISABLED_PREVIEW_ONLY=YES; URL=http://127.0.0.1:$PORT; STOP=Ctrl-C"
exec "$PY" -m streamlit run "$ROOT/source/gui_v02_fix1/streamlit_8510_stage01_v02_contract_review_20261104.py" --server.headless=true --server.address=127.0.0.1 --server.port="$PORT" --server.fileWatcherType=none --browser.gatherUsageStats=false
"""
REQUIREMENTS="""streamlit==1.59.2
pandas==2.3.3
plotly==6.9.0
requests==2.34.2
openai==3.45.0
cryptography==49.0.0
"""
def main():
    with urlopen(URL,timeout=30) as r:old=r.read(1024*1024)
    if len(old)!=41353 or sha(old)!=RELEASE_SHA:raise RuntimeError("PINNED_RELEASE_MISMATCH")
    sp=Path("qa/recovered_sources/kge_v11_spool_bridge_v0_1.py").read_bytes()
    if sha(sp)!=SPOOL_SHA:raise RuntimeError("PINNED_HISTORICAL_SPOOL_MISMATCH")
    items={}
    with ZipFile(io.BytesIO(old)) as z:
        if z.testzip() is not None:raise RuntimeError("SOURCE_CRC_FAILED")
        for n in z.namelist():
            if n.startswith("source/gui_v02_fix1/") and n.endswith(".py"):
                b=z.read(n);ast.parse(b.decode("utf-8-sig"));items[n]=b
    if len(items)!=5:raise RuntimeError("EXPECTED_FIVE_GUI_MODULES")
    items[SPOOL]=sp
    items["README_FIRST_JA.md"]=MANUAL.encode()
    items["RUN_DISABLED_PREVIEW.command"]=RUN.encode()
    items["requirements-preview.txt"]=REQUIREMENTS.encode()
    s=io.StringIO();writer=csv.writer(s,delimiter="\t",lineterminator="\n")
    writer.writerow(["path","size_bytes","sha256","crc32_hex"])
    for n,b in sorted(items.items()):writer.writerow([n,str(len(b)),sha(b),f"{zlib.crc32(b)&0xffffffff:08x}"])
    items["MANIFEST_SHA256_SIZE_CRC.tsv"]=s.getvalue().encode()
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    if OUTPUT.exists():raise RuntimeError("OUTPUT_EXISTS_NO_OVERWRITE")
    with ZipFile(OUTPUT,"w",compression=ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(items.items()):
            info=ZipInfo(n,date_time=(2026,11,5,0,0,0))
            info.compress_type=ZIP_DEFLATED
            info.external_attr=((0o100755 if n.endswith(".command") else 0o100644)<<16)
            z.writestr(info,b)
    with ZipFile(OUTPUT) as z:
        if z.testzip() is not None:raise RuntimeError("CANDIDATE_CRC")
    print("CANDIDATE_BUILT_NOT_PUBLISHED=YES")
    print("CANDIDATE_BYTES="+str(OUTPUT.stat().st_size))
    print("CANDIDATE_SHA256="+sha(OUTPUT.read_bytes()))
    print("CANDIDATE_QA_SCOPE=DISABLED_PREVIEW_ONLY")
if __name__=="__main__":main()
