#!/usr/bin/env python3
"""Browser-level smoke for the archived QA candidate only.
No real user data, API key, Provider send or G4 approval.
"""
import os
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from zipfile import ZipFile

from playwright.sync_api import sync_playwright

CANDIDATE=Path("candidate/8510_STAGE01_V02_DISABLED_PREVIEW_QA_CANDIDATE.zip")
LOG=Path("qa_browser_stdout.log")
SCREENSHOT=Path("qa_browser_preview.png")

def main():
    with tempfile.TemporaryDirectory(prefix="qa_preview_browser_") as d:
        root=Path(d)
        with ZipFile(CANDIDATE) as z:
            assert z.testzip() is None
            for n in z.namelist():
                p=Path(n)
                assert not p.is_absolute() and ".." not in p.parts
            z.extractall(root)
        subprocess.run([sys.executable,"-m","venv","--system-site-packages",str(root/".preview_venv")],check=True)
        so=socket.socket();so.bind(("127.0.0.1",0));port=so.getsockname()[1];so.close()
        proc=None
        with LOG.open("w",encoding="utf-8") as log:
            try:
                proc=subprocess.Popen(["bash",str(root/"RUN_DISABLED_PREVIEW.command"),str(port)],
                    stdout=log,stderr=subprocess.STDOUT,env=os.environ.copy(),cwd=root)
                url=f"http://127.0.0.1:{port}"
                with sync_playwright() as p:
                    browser=p.chromium.launch(headless=True)
                    try:
                        page=browser.new_page(viewport={"width":1440,"height":900})
                        ready=False
                        for i in range(60):
                            if proc.poll() is not None:
                                raise RuntimeError("PREVIEW_EXITED_BEFORE_BROWSER_LOADED")
                            try:
                                page.goto(url,timeout=2500,wait_until="domcontentloaded")
                                page.get_by_text("STAGE01_V02_RUNTIME_DISABLED",exact=False).wait_for(timeout=2500)
                                ready=True
                                break
                            except Exception:
                                time.sleep(0.3)
                        if not ready:
                            raise RuntimeError("DISABLED_BROWSER_UI_NOT_RENDERED")
                        assert page.get_by_text("KGE Stage01 V02 / 8510",exact=False).count()>0
                        active=page.locator("button:not([disabled]):visible")
                        bad=[b.inner_text().strip() for b in active.all()
                             if "send" in b.inner_text().lower() or "approve" in b.inner_text().lower()]
                        assert not bad, "UNEXPECTED_ENABLED_SEND_APPROVE: "+repr(bad)
                        assert "APP_USER_ID" in page.locator("body").inner_text()
                        page.screenshot(path=str(SCREENSHOT),full_page=True)
                        print("BROWSER_VISUAL_DISABLED_MARKER=PASS")
                        print("BROWSER_NO_ENABLED_SEND_APPROVE=PASS")
                        print("BROWSER_SCREENSHOT_SAVED="+str(SCREENSHOT))
                    finally:
                        browser.close()
            finally:
                if proc is not None:
                    if proc.poll() is None:
                        proc.terminate()
                        try:proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:
                            proc.kill();proc.wait(timeout=5)
                    assert proc.poll() is not None
        print("BROWSER_PREVIEW_SHUTDOWN=PASS")

if __name__=="__main__":
    main()
