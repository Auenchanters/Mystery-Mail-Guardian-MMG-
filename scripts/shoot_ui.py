"""Screenshot the running mock app via headless Edge + CDP (real-time waits).

Usage: .venv\\Scripts\\python.exe scripts\\shoot_ui.py <url> <out.png> [wait_s] [width] [height]
Dev-tooling only; not part of the deployed app.
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

import websockets

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
PORT = 9777


async def shoot(url: str, out: str, wait_s: float, width: int, height: int) -> None:
    edge = next(p for p in EDGE_PATHS if os.path.exists(p))
    profile = os.path.join(tempfile.gettempdir(), "edge-cdp-shot")
    proc = subprocess.Popen([
        edge, "--headless=new", "--disable-gpu", "--no-first-run",
        f"--user-data-dir={profile}", f"--remote-debugging-port={PORT}",
        f"--window-size={width},{height}", "about:blank",
    ])
    try:
        ws_url = None
        for _ in range(50):  # wait for the devtools endpoint
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json") as r:
                    tabs = json.load(r)
                page = next(t for t in tabs if t["type"] == "page")
                ws_url = page["webSocketDebuggerUrl"]
                break
            except Exception:
                time.sleep(0.2)
        if not ws_url:
            raise RuntimeError("devtools endpoint never came up")

        async with websockets.connect(ws_url, max_size=64 * 1024 * 1024) as ws:
            mid = 0

            async def cmd(method: str, **params):
                nonlocal mid
                mid += 1
                await ws.send(json.dumps({"id": mid, "method": method, "params": params}))
                while True:
                    msg = json.loads(await ws.recv())
                    if msg.get("id") == mid:
                        return msg.get("result", {})

            await cmd("Emulation.setDeviceMetricsOverride", width=width,
                      height=height, deviceScaleFactor=1, mobile=width < 500)
            await cmd("Page.enable")
            await cmd("Page.navigate", url=url)
            await asyncio.sleep(wait_s)  # real time: queue + SSE + animations
            shot = await cmd("Page.captureScreenshot", format="png")
            with open(out, "wb") as f:
                f.write(base64.b64decode(shot["data"]))
            print(f"wrote {out}")
    finally:
        proc.terminate()


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    wait_s = float(sys.argv[3]) if len(sys.argv) > 3 else 8.0
    width = int(sys.argv[4]) if len(sys.argv) > 4 else 1280
    height = int(sys.argv[5]) if len(sys.argv) > 5 else 1500
    asyncio.run(shoot(url, out, wait_s, width, height))
