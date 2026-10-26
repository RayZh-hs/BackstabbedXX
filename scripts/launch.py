#!/usr/bin/env python3
"""Launch the working copy with the NeoForge version from mmc-pack.json."""

from base64 import b64encode
from http.client import HTTPSConnection
import json
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
from urllib.request import getproxies, proxy_bypass

import portablemc.download
from portablemc.cli import main as portablemc_main


ROOT = Path(__file__).resolve().parent.parent


def enable_resourcepack():
    """Enable the built pack while preserving the player's other options and packs."""
    path = ROOT / ".minecraft/options.txt"
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    pack = "file/backstabbed-resource.zip"
    for index, line in enumerate(lines):
        if line.startswith("resourcePacks:"):
            packs = json.loads(line.partition(":")[2])
            if pack in packs:
                return
            packs.append(pack)
            lines[index] = "resourcePacks:" + json.dumps(packs, ensure_ascii=False)
            break
    else:
        lines.append("resourcePacks:" + json.dumps(["vanilla", pack]))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def configure_download_proxy():
    """Make PortableMC's HTTPS downloads use the same proxy as its metadata requests."""
    proxy_url = getproxies().get("https")
    if not proxy_url:
        return
    proxy = urlsplit(proxy_url)
    if proxy.scheme != "http" or not proxy.hostname:
        raise SystemExit("HTTPS_PROXY must be an HTTP proxy URL, for example http://127.0.0.1:7890")
    headers = {}
    if proxy.username is not None:
        credentials = f"{unquote(proxy.username)}:{unquote(proxy.password or '')}"
        headers["Proxy-Authorization"] = "Basic " + b64encode(credentials.encode()).decode()

    class ProxiedHTTPSConnection(HTTPSConnection):
        def __init__(self, host, port=None, **kwargs):
            if proxy_bypass(host):
                super().__init__(host, port, **kwargs)
            else:
                super().__init__(proxy.hostname, proxy.port or 80, **kwargs)
                self.set_tunnel(host, port or 443, headers=headers)

    # PortableMC 4.4.1 uses http.client directly for downloads, bypassing urllib's proxy support.
    portablemc.download.HTTPSConnection = ProxiedHTTPSConnection


def main():
    metadata = json.loads((ROOT / "mmc-pack.json").read_text(encoding="utf-8"))
    versions = {item["uid"]: item["version"] for item in metadata["components"]}
    minecraft = versions["net.minecraft"]
    neoforge = versions["net.neoforged"]
    runtime = Path(os.environ.get("MINECRAFT_RUNTIME_DIR") or ROOT / "dev/launcher").expanduser().resolve()
    runtime.mkdir(parents=True, exist_ok=True)

    enable_resourcepack()
    configure_download_proxy()
    print(f"Launching Minecraft {minecraft} / NeoForge {neoforge}", flush=True)
    print(f"Game directory: {ROOT / '.minecraft'}", flush=True)
    portablemc_main([
        "--main-dir", str(runtime),
        "--work-dir", str(ROOT / ".minecraft"),
        "start", f"neoforge:{neoforge}",
        "--username", "BackstabbedDev",
        "--jvm-args=-Xmx4G",
        *sys.argv[1:],
    ])


if __name__ == "__main__":
    main()
