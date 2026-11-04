#!/usr/bin/env python3
"""Conservative static screening of the disabled-preview candidate ZIP.
This does not establish network isolation, code safety, or absence of all secrets.
"""
import ast
import csv
import hashlib
import io
from pathlib import PurePosixPath,Path
import re
import stat
import zlib
from zipfile import ZipFile
import sys

ZIP=Path("candidate/8510_STAGE01_V02_DISABLED_PREVIEW_QA_CANDIDATE.zip")
EXPECTED={
"source/gui_v02_fix1/stage01_citation_contract_v02.py",
"source/gui_v02_fix1/stage01_contract_8504_compat_v02.py",
"source/gui_v02_fix1/stage01_contract_bridge_v02.py",
"source/gui_v02_fix1/stage01_contract_ui_v02.py",
"source/gui_v02_fix1/streamlit_8510_stage01_v02_contract_review_20261104.py",
"source/gui_v02_fix1/kge_v11_spool_bridge_v0_1.py",
"README_FIRST_JA.md",
"RUN_DISABLED_PREVIEW.command",
"requirements-preview.txt",
"MANIFEST_SHA256_SIZE_CRC.tsv",
}
SECRET=[
re.compile(rb'sk-(?:proj-)?[A-Za-z0-9_-]{20,}'),
re.compile(rb'(?:ghp_|gho_|ghs_|ghu_|github_pat_)[A-Za-z0-9_]{16,}'),
re.compile(rb'AKIA[0-9A-Z]{16}'),
re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
re.compile(rb'AIza[0-9A-Za-z_-]{30,}'),
]
def main():
    if not ZIP.is_file():raise RuntimeError("CANDIDATE_MISSING")
    with ZipFile(ZIP) as z:
        if z.testzip() is not None:raise RuntimeError("CRC_FAILURE")
        infos=z.infolist()
        names=[x.filename for x in infos]
        if len(names)!=len(set(names)) or set(names)!=EXPECTED:
            raise RuntimeError("BUNDLE_FILE_ALLOWLIST_FAILURE")
        for info in infos:
            p=PurePosixPath(info.filename)
            mode=(info.external_attr>>16)&0xffff
            if p.is_absolute() or ".." in p.parts or "\\" in info.filename:
                raise RuntimeError("UNSAFE_ARCHIVE_PATH")
            if stat.S_ISLNK(mode):raise RuntimeError("ZIP_SYMLINK_FORBIDDEN")
            if info.file_size>150000 or info.compress_size>150000:
                raise RuntimeError("MEMBER_SIZE_LIMIT")
            b=z.read(info)
            if info.filename.endswith(".py"):ast.parse(b.decode("utf-8-sig"))
            for pattern in SECRET:
                if pattern.search(b):raise RuntimeError("SECRET_SHAPE_BLOCKED")
            print("STATIC_MEMBER_CHECK=PASS",info.filename)
        rows=list(csv.DictReader(io.StringIO(z.read("MANIFEST_SHA256_SIZE_CRC.tsv").decode()),delimiter="\t"))
        if len(rows)!=len(EXPECTED)-1:raise RuntimeError("MANIFEST_ENTRY_COUNT")
        if {r["path"] for r in rows}!=EXPECTED-{"MANIFEST_SHA256_SIZE_CRC.tsv"}:
            raise RuntimeError("MANIFEST_ALLOWLIST_FAILURE")
        for r in rows:
            b=z.read(r["path"])
            if len(b)!=int(r["size_bytes"]) or hashlib.sha256(b).hexdigest()!=r["sha256"]:
                raise RuntimeError("MANIFEST_HASH_SIZE")
            if f"{zlib.crc32(b)&0xffffffff:08x}"!=r["crc32_hex"]:
                raise RuntimeError("MANIFEST_CRC")
        manual=z.read("README_FIRST_JA.md").decode()
        script=z.read("RUN_DISABLED_PREVIEW.command").decode()
        if not all(x in manual for x in ("起動","終了","未検証","8504")):
            raise RuntimeError("USER_MANUAL_MISSING")
        if not all(x in script for x in ("KGE_STAGE01_V02_ENABLED=NO","127.0.0.1",
                                         "unset OPENAI_API_KEY","unset KEY_ENCRYPTION_SECRET",
                                         ".preview_venv/bin/python")):
            raise RuntimeError("LAUNCH_FAIL_CLOSED_MISSING")
        print("STATIC_SOURCE_CONTENT_SCREEN=PASS")
        print("SOURCE_SECRET_SHAPE_SCREEN_ONLY_NOT_PROOF=YES")
        print("CANDIDATE_ALLOWLIST_MANIFEST_AND_MANUAL=PASS")
if __name__=="__main__":
    try:main()
    except Exception as e:
        print("STATIC_CANDIDATE_SCREEN=FAIL:",type(e).__name__,str(e),file=sys.stderr)
        raise SystemExit(2)
