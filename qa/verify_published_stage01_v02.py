#!/usr/bin/env python3
"""Fail-closed, offline-by-design QA of the exact public 8510 Stage01 V02 ZIP.
No existing local research files, API keys, requests, or containers are used.
A PASS here does not certify a full scientific or Provider E2E workflow.
"""
import ast
import hashlib
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen
from urllib.error import URLError
from zipfile import ZipFile

URL = ("https://github.com/kushidat/kge-8510-stage01-citation-contract"
       "/releases/download/8510-stage01-v0.2.0/"
       "KGE_8510_STAGE01_V02_SOURCE_ONLY_20261105.zip")
EXPECTED_SHA256 = "bf68b4176dfb8c05295dab1c7636307ac775a872d7b660cfd4b22517ffad9f26"
EXPECTED_SIZE = 41353
EXPECTED_PY = 9
EXPECTED_ENTRY = "source/gui_v02_fix1/streamlit_8510_stage01_v02_contract_review_20261104.py"
out = {"test_suite": "8510-public-asset-disabled-preview",
       "asset": URL, "expected_sha256": EXPECTED_SHA256,
       "checks": {}, "limitations": [
        "No real Provider/API calls or user credentials",
        "No full 8504->8510->8504 G4 end-to-end validation",
        "No Mac or original production-container runtime certification",
        "No OS-level embargoed-data nonread proof on user's Mac",
        "No standalone complete-product or scientific-result certification",
       ]}

def check(name, passed, detail=None):
    out["checks"][name] = {"pass": bool(passed), "detail": detail}
    print(("PASS " if passed else "FAIL ") + name + (": "+str(detail) if detail else ""), flush=True)
    if not passed:
        raise AssertionError(name + ": " + str(detail))

def inspect_archive(zbytes, workspace):
    with ZipFile(io.BytesIO(zbytes)) as z:
        check("zip_crc", z.testzip() is None)
        names = z.namelist()
        check("zip_member_uniqueness", len(names) == len(set(names)))
        check("source_nine_modules", len([n for n in names if n.endswith(".py")]) == EXPECTED_PY)
        check("entry_present", EXPECTED_ENTRY in names)
        check("manifest_present", "MANIFEST_SOURCE_SHA256_SIZE_CRC.tsv" in names)
        check("release_readme_present", "README_RELEASE_JA.md" in names)
        for n in names:
            path = Path(n)
            check("safe_zip_path_" + n, not path.is_absolute()
                  and ".." not in path.parts and "\\" not in n)
            if n.endswith(".py"):
                b = z.read(n)
                ast.parse(b.decode("utf-8-sig"), filename=n)
                if n == EXPECTED_ENTRY:
                    t = ast.parse(b.decode("utf-8-sig"), filename=n)
                    print('ENTRY_IMPORTS=' + json.dumps([ast.unparse(x) for x in ast.walk(t) if isinstance(x, (ast.Import, ast.ImportFrom))], ensure_ascii=False), flush=True)
                p = workspace / n
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(b)
        check("all_python_syntax", True)
        readme = z.read("README_RELEASE_JA.md").decode("utf-8")
        check("source_only_disclosed", "source-only" in readme.lower()
              and "NOT verified" in readme)
    return workspace / EXPECTED_ENTRY

def http_check(port):
    import urllib.request
    for _ in range(75):
        try:
            with urllib.request.urlopen("http://127.0.0.1:%d/_stcore/health" % port, timeout=1) as r:
                return r.status == 200 and r.read(512).strip() == b"ok"
        except Exception:
            time.sleep(0.4)
    return False

def test_preview(entry, workspace):
    # UI execution is deliberately disabled and credentials are absent.
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(workspace),
        "PYTHONPATH": str(entry.parent),
        "KGE_STAGE01_V02_ENABLED": "NO",
        "APP_USER_ID": "",
        "ALLOW_SERVER_OPENAI_KEY": "false",
        "OPENAI_API_KEY": "",
        "KEY_ENCRYPTION_SECRET": "",
        "STREAMLIT_BROWSER_GATHER_USAGE_STATS": "false",
        "STREAMLIT_SERVER_HEADLESS": "true",
    }
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Use a random OS-selected ephemeral port and localhost binding only.
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    cmd = [sys.executable, "-m", "streamlit", "run", str(entry),
           "--server.headless=true", "--server.address=127.0.0.1",
           "--server.port="+str(port), "--server.fileWatcherType=none",
           "--browser.gatherUsageStats=false"]
    log = Path("streamlit_server.log")
    proc = None
    with log.open("w", encoding="utf-8") as handle:
        try:
            proc = subprocess.Popen(cmd, cwd=workspace, env=env, stdout=handle,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            healthy = http_check(port)
            if proc.poll() is not None: healthy = False
            check("http_server_health", healthy,
                  "local isolated HEADLESS server on 127.0.0.1")
        finally:
            if proc is not None and proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait(timeout=5)
            check("server_stopped", proc is not None and proc.poll() is not None)
    text = log.read_text(encoding="utf-8", errors="replace")
    check("no_server_traceback", "Traceback (most recent call last):" not in text,
          "Streamlit server stdout/stderr inspected")

def main():
    try:
        # Public release URL only; never authenticate or use local protected records.
        with urlopen(URL, timeout=30) as response:
            raw = response.read(1024*1024)
        check("asset_size", len(raw) == EXPECTED_SIZE, len(raw))
        digest = hashlib.sha256(raw).hexdigest()
        check("asset_sha256", digest == EXPECTED_SHA256, digest)
        with tempfile.TemporaryDirectory(prefix="8510_release_qa_") as td:
            root = Path(td)
            entry = inspect_archive(raw, root)
            # Candidate-specific dependency recovery from the SHA-pinned
            # historical 2026-11-04 handoff. Does NOT change the release ZIP.
            recovered = Path("qa/recovered_sources/kge_v11_spool_bridge_v0_1.py")
            check("historical_spool_dependency_exists", recovered.is_file())
            recovery_bytes = recovered.read_bytes()
            check("historical_spool_dependency_sha256",
                  hashlib.sha256(recovery_bytes).hexdigest() ==
                  "e7d89291ab6286b008d91ef0b50b2def4587e879a091de69e7b4222685be00d3")
            (entry.parent / "kge_v11_spool_bridge_v0_1.py").write_bytes(recovery_bytes)
            out["scope"] = "public_unchanged_asset_plus_historical_dependency_candidate"
            # Unlike an HTTP health endpoint, AppTest executes the Streamlit
            # script and checks for Python runtime exceptions in disabled mode.
            from streamlit.testing.v1 import AppTest
            old_env = {key: os.environ.get(key) for key in
                       ("KGE_STAGE01_V02_ENABLED", "APP_USER_ID",
                        "OPENAI_API_KEY", "ALLOW_SERVER_OPENAI_KEY",
                        "KEY_ENCRYPTION_SECRET", "PYTHONPATH")}
            try:
                os.environ.update({
                    "KGE_STAGE01_V02_ENABLED": "NO",
                    "APP_USER_ID": "",
                    "OPENAI_API_KEY": "",
                    "ALLOW_SERVER_OPENAI_KEY": "false",
                    "KEY_ENCRYPTION_SECRET": "",
                    "PYTHONPATH": str(entry.parent),
                })
                sys.path.insert(0, str(entry.parent))
                at = AppTest.from_file(str(entry), default_timeout=45).run()
                errors = [str(x.message) for x in at.exception]
                check("disabled_ui_python_execution", not errors,
                      ("; ".join(errors))[:750] if errors else "No AppTest exception")
                check("disabled_ui_screen_has_elements",
                      bool(at.title or at.markdown or at.warning or at.info or at.caption),
                      "At least one expected Streamlit UI element")
            finally:
                if str(entry.parent) in sys.path:
                    sys.path.remove(str(entry.parent))
                for key, value in old_env.items():
                    if value is None:
                        os.environ.pop(key, None)
                    else:
                        os.environ[key] = value
            test_preview(entry, root)
    except BaseException as ex:
        out["exception"] = type(ex).__name__ + ": " + str(ex)
    out["overall"] = ("PASS" if out["checks"] and
                      all(x["pass"] for x in out["checks"].values()) and
                      "exception" not in out else "FAIL")
    Path("qa_verification.json").write_text(json.dumps(out, ensure_ascii=False, indent=2)+"\n")
    print("RELEASE_QA_STATUS="+out["overall"], flush=True)
    print("TEST_SCOPE=PUBLIC_ASSET_AND_DISABLED_HTTP_SERVER_ONLY", flush=True)
    return 0 if out["overall"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
