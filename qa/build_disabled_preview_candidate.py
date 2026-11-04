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
MANUAL="""# 8510 Stage01 V02 / Disabled GUI Preview / QA Candidate
This is an independent DISABLED demo. It is not formal 8510 v1.0, not a
scientifically validated disease-mouse explanation service, and not a
Provider-enabled or G4-accepted app. Do not overwrite any installed app.

## Requirements
Python 3.12 with venv and pip on macOS or Linux. Create a NEW isolated folder.

## Install, start and stop
1. Unzip into a new empty folder without overwriting any existing source.
2. Open Terminal in that folder.
3. python3 -m venv .preview_venv
4. .preview_venv/bin/python -m pip install -r requirements-preview.txt
5. bash RUN_DISABLED_PREVIEW.command
6. Open http://127.0.0.1:18610 in a browser (local-only preview).
7. Verify that V02 runtime is disabled; no Provider SEND or G4 approval.
8. To stop, return to the SAME foreground Terminal and press Control-C.
Closing the browser does not stop Streamlit. Do not stop other containers.

If the default port is used, do not terminate the competing service;
run: bash RUN_DISABLED_PREVIEW.command 18611

## Known limitations
Dependency install needs network and is not a tested offline wheelhouse.
The package does not enable API credentials, Provider sending,
8504 request/approval transfer, the frozen formal 8510 app or KGE ranking.
No clinical or scientific conclusions. No PRIMARY_TEST, test, validation
or withheld data. MAC runtime NOT_TESTED. Only cloud Linux preview QA applies.
Historical spool module is included from a verified 2026-11-04 handoff.
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
REQUIREMENTS="""streamlit>=1.45,<1.60
pandas>=2.2,<3
plotly>=5,<7
requests>=2.31,<3
openai>=1.0,<4
cryptography>=42,<50
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
            if n.startswith("source/") and n.endswith(".py"):
                b=z.read(n);ast.parse(b.decode("utf-8-sig"));items[n]=b
    if len(items)!=9:raise RuntimeError("EXPECTED_NINE_SOURCE_MODULES")
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
