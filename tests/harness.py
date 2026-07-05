"""Black-box test harness for safehouse+.

The harness drives the real `safehouse+` program. It does NOT import any of its
internals, so refactors of the implementation don't require test changes. A test
declares a sandbox spec as the contents of a `.safehouse-plus.json` file, runs a
probe command through `safehouse+`, and asserts on what the *sandboxed* probe
observed. In other words: we verify that the specification written in
`.safehouse-plus.json` is actually enforced by the sandbox.

How it works:
  * Create a fresh temp workdir and write `.safehouse-plus.json` into it.
  * Run `safehouse+ --script <probe...>` inside that workdir. `--script` runs the
    command once and exits immediately with no curses menu, so the probe's stdout
    can be captured directly.

Probe rules:
  * stdout is the verdict; stderr is discarded.
"""
from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAFEHOUSE_PLUS = os.path.join(ROOT, "safehouse+")
SAFEHOUSE_BIN = os.environ.get("SAFEHOUSE_BIN") or shutil.which("safehouse") or "safehouse"

# Test workdirs must live OUTSIDE any path a spec-under-test might restrict
# (notably /tmp and /var/folders, which the temp-dir tests deny). A dedicated
# directory in HOME that belongs to no default path category is always safe:
# safehouse makes the chosen --workdir writable regardless, so the probe can
# record its verdict there. This dir is NOT under any default category path.
WORKDIR_BASE = os.path.expanduser("~/.safehouse-plus-tests")


# A probe that classifies a single filesystem access by the errno the sandbox
# returns, so a test gives the same answer whether or not the target exists:
#   OK       access succeeded
#   BLOCKED  denied by the sandbox (EPERM/EACCES -> PermissionError)
#   ABSENT   target does not exist (ENOENT) -- inconclusive, not a leak
#   OTHER:n  some other errno
# For writes it opens in append mode and writes nothing, so a successful write
# never modifies an existing file.
_CLASSIFY_PY = r'''import sys, os
mode, path, label = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    if mode == "read":
        if os.path.isdir(path):
            os.listdir(path)
        else:
            open(path, "rb").read(1)
    else:
        f = open(path, "a"); f.close()
    print(label + "=OK")
except PermissionError:
    print(label + "=BLOCKED")
except FileNotFoundError:
    print(label + "=ABSENT")
except IsADirectoryError:
    os.listdir(path); print(label + "=OK")
except OSError as e:
    print(label + "=OTHER:%d" % e.errno)'''


def classify_probe(mode: str, path: str, label: str = "A") -> str:
    """Build a probe body that reports `<label>=OK|BLOCKED|ABSENT|OTHER:n`.

    mode is "read" or "write". `path` may contain ~ (expanded by the shell).
    """
    return "python3 -c %s %s %s %s" % (
        shlex.quote(_CLASSIFY_PY), shlex.quote(mode), path, shlex.quote(label))


def run_probe(config: dict, body: str, parent_env: dict | None = None, timeout: int = 45) -> dict:
    """Run a probe under `safehouse+ --script` with `config` as the project
    .safehouse-plus.json.

    `body` is a `/bin/sh` snippet whose stdout is captured as the verdict. Return
    a dict with:
      tokens:  list[str] of non-empty stdout lines the probe produced
      raw:     the probe's raw stdout
      term:    raw stdout+stderr combined (for debugging)
      timed_out: whether the harness had to kill safehouse+
    """
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="shp-test-", dir=WORKDIR_BASE)
    try:
        with open(os.path.join(workdir, ".safehouse-plus.json"), "w") as f:
            json.dump(config, f)
        env = dict(os.environ)
        env["SAFEHOUSE"] = SAFEHOUSE_BIN
        argv = [SAFEHOUSE_PLUS, "--script", "/bin/sh", "-c", body]
        if parent_env:
            env.update({k: str(v) for k, v in parent_env.items()})
        timed_out = False
        try:
            proc = subprocess.run(
                argv, cwd=workdir, env=env, timeout=timeout,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            raw = proc.stdout.decode(errors="replace")
            term = raw + proc.stderr.decode(errors="replace")
        except subprocess.TimeoutExpired as e:
            timed_out = True
            raw = (e.stdout or b"").decode(errors="replace")
            term = raw + "\n__HARNESS_TIMEOUT__\n"
        tokens = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        return {
            "tokens": tokens,
            "raw": raw,
            "term": term,
            "timed_out": timed_out,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
