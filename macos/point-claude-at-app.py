"""Point Claude's Flighty server at the CraneOS Flighty app instead of uv.

    python3 macos/point-claude-at-app.py

Why (2026-10-12): Claude started this server as `uv ... run main.py`, so Full
Disk Access had to go to uv itself, and every program run through uv on this
Mac inherited it. Run as its own app, only this server gets the permission and
it shows by name in System Settings. Backs the config up first; prints what it
changed; changes nothing if no Flighty entry is found.
"""
import json, os, shutil, sys, time

CFG = os.path.expanduser("~/Library/Application Support/Claude/claude_desktop_config.json")
HERE = os.path.expanduser("~/Documents/Code/flighty-mcp")
APP_EXE = os.path.expanduser("~/Applications/CraneOS/CraneOS Flighty.app/Contents/MacOS/CraneOS Flighty")
SITE = os.path.join(HERE, ".venv/lib/python3.14/site-packages")

if not os.path.exists(APP_EXE):
    sys.exit(f"build the app first: macos-apps/make-job-app.sh \"CraneOS Flighty\" me.craneos.flighty-mcp\n(missing {APP_EXE})")
cfg = json.load(open(CFG))
servers = cfg.get("mcpServers", {})
hits = [k for k, v in servers.items()
        if "flighty-mcp" in " ".join([str(v.get("command", ""))] + [str(a) for a in v.get("args", [])])]
if len(hits) != 1:
    sys.exit(f"expected one Flighty server in {CFG}, found {hits or 'none'}; nothing changed")
key = hits[0]
backup = f"{CFG}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(CFG, backup)
old = servers[key]
env = dict(old.get("env", {}))
env["PYTHONPATH"] = SITE
servers[key] = {"command": APP_EXE, "args": [os.path.join(HERE, "main.py")], "env": env}
json.dump(cfg, open(CFG, "w"), indent=2)
print(f"backed up to {backup}")
print(f"'{key}' was: {json.dumps({k: old[k] for k in ('command', 'args') if k in old})}")
print(f"'{key}' now: {APP_EXE} main.py (PYTHONPATH = the project venv)")
print("Quit and reopen Claude for it to take effect.")
