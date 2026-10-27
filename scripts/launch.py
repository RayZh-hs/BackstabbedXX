#!/usr/bin/env python3
"""Launch the working copy with the NeoForge version from mmc-pack.json."""

from base64 import b64encode
from contextlib import nullcontext
from http.client import HTTPSConnection
import json
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit
from urllib.request import getproxies, proxy_bypass

ROOT = Path(__file__).resolve().parent.parent


def enable_resourcepack(game_dir=None):
    """Enable the built pack while preserving the player's other options and packs."""
    path = (game_dir or ROOT / ".minecraft") / "options.txt"
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
    import portablemc.download

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
    import portablemc.cli

    args = sys.argv[1:]
    local = "--local" in args
    args = [arg for arg in args if arg != "--local"]
    if local and any(arg.split("=", 1)[0] in ("--server", "--server-port") for arg in args):
        raise SystemExit("--local opens the playtest world in singleplayer; omit --server and --server-port")
    metadata = json.loads((ROOT / "mmc-pack.json").read_text(encoding="utf-8"))
    versions = {item["uid"]: item["version"] for item in metadata["components"]}
    minecraft = versions["net.minecraft"]
    neoforge = versions["net.neoforged"]
    runtime = Path(os.environ.get("MINECRAFT_RUNTIME_DIR") or ROOT / "dev/launcher").expanduser().resolve()
    runtime.mkdir(parents=True, exist_ok=True)

    configure_download_proxy()
    if local:
        from local_playtest import WORLD_NAME, build_helper, local_game_directory

        original_runner = portablemc.cli.CliRunner

        class LocalRunner(original_runner):
            def run(self, env):
                # Installation has finished: compile against the exact game and
                # NeoForge jars, using the JDK PortableMC just installed.
                build_helper(ROOT, runtime, env.jvm_args[0], env.context.work_dir, minecraft, neoforge)
                env.game_args.extend(["--quickPlaySingleplayer", WORLD_NAME])
                return super().run(env)

        directory = local_game_directory(ROOT)
        portablemc.cli.CliRunner = LocalRunner
    else:
        directory = nullcontext(ROOT / ".minecraft")

    try:
        with directory as game_dir:
            enable_resourcepack(game_dir)
            print(f"Launching Minecraft {minecraft} / NeoForge {neoforge}", flush=True)
            print(f"Game directory: {game_dir}", flush=True)
            if local:
                print("Local playtest: fresh world copy, commands enabled, three idle players auto-queued.", flush=True)
            portablemc.cli.main([
                "--main-dir", str(runtime),
                "--work-dir", str(game_dir),
                "start", f"neoforge:{neoforge}",
                "--username", "BackstabbedDev",
                "--jvm-args=-Xmx4G",
                *args,
            ])
    finally:
        if local:
            portablemc.cli.CliRunner = original_runner


if __name__ == "__main__":
    main()
