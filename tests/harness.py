"""Black-box test harness for safehouse+.

The harness drives the real `safehouse+` program. It does NOT import any of its
internals, so refactors of the implementation don't require test changes. A test
declares a sandbox spec as the contents of a `.safehouse-plus.json` file, runs a
probe command through `safehouse+`, and asserts on what the *sandboxed* probe
observed. In other words: we verify that the specification written in
`.safehouse-plus.json` is actually enforced by the sandbox.

How it works:
  * Create a fresh temp workdir and write `.safehouse-plus.json` into it.
  * Launch `safehouse+ <probe...>` inside that workdir under a PTY (the UI is
    curses, so a TTY is required). `safehouse+` runs the probe in the sandbox on
    first launch, then drops to its menu.
  * The probe's stdout is redirected to a result file in the workdir. The probe's
    cwd IS the (writable) workdir, so it can always record its verdict there.
  * Once the menu header is drawn (which only happens after the probe finishes),
    the harness sends `q` to quit, then reads the verdict file.

Probe rules:
  * Must exit 0 (a non-zero exit makes safehouse+ show a pager that would
    deadlock the single `q` we send); `run_probe` appends `exit 0` for you.
  * Must only write to unique, freshly-created temp paths and clean up.
"""
from __future__ import annotations

import json
import os
import pty
import select
import shlex
import shutil
import signal
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAFEHOUSE_PLUS = os.path.join(ROOT, "safehouse+")
SAFEHOUSE_BIN = os.environ.get("SAFEHOUSE_BIN", os.path.join(ROOT, "safehouse"))

MENU_MARKER = b"safehouse+"   # drawn only after the probe completes
RESULT_FILE = "probe_result.txt"

# Test workdirs must live OUTSIDE any path a spec-under-test might restrict
# (notably /tmp and /var/folders, which the temp-dir tests deny). A dedicated
# directory in HOME that belongs to no default path category is always safe:
# safehouse makes the chosen --workdir writable regardless, so the probe can
# record its verdict there. This dir is NOT under any default category path.
WORKDIR_BASE = os.path.expanduser("~/.safehouse-plus-tests")


def _pty_run(argv, cwd, env, timeout):
    """Run argv under a PTY; send `q` once the menu appears; return raw output."""
    pid, fd = pty.fork()
    if pid == 0:  # child
        try:
            os.chdir(cwd)
            os.execvpe(argv[0], argv, env)
        except Exception:
            os._exit(127)

    out = bytearray()
    sent_quit = False
    deadline = time.time() + timeout
    while True:
        if time.time() > deadline:
            try:
                os.kill(pid, signal.SIGTERM)
            except OSError:
                pass
            out.extend(b"\n__HARNESS_TIMEOUT__\n")
            break
        try:
            ready, _, _ = select.select([fd], [], [], 0.5)
        except OSError:
            break
        if fd in ready:
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            out.extend(data)
            if not sent_quit and MENU_MARKER in bytes(out):
                try:
                    os.write(fd, b"q")  # quit the menu (saves and exits)
                except OSError:
                    pass
                sent_quit = True
        try:
            done, _ = os.waitpid(pid, os.WNOHANG)
            if done == pid:
                break
        except ChildProcessError:
            break
    try:
        os.close(fd)
    except OSError:
        pass
    try:
        os.waitpid(pid, 0)
    except (ChildProcessError, OSError):
        pass
    return out.decode(errors="replace")


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
    """Run a probe under `safehouse+` with `config` as the project .safehouse-plus.json.

    `body` is a `/bin/sh` snippet whose stdout is captured as the verdict. Return
    a dict with:
      tokens:  list[str] of non-empty stdout lines the probe produced
      raw:     the full verdict-file contents
      term:    the full captured terminal output (for debugging)
      timed_out: whether the harness had to kill safehouse+
    """
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix="shp-test-", dir=WORKDIR_BASE)
    try:
        with open(os.path.join(workdir, ".safehouse-plus.json"), "w") as f:
            json.dump(config, f)
        env = dict(os.environ)
        env["SAFEHOUSE"] = SAFEHOUSE_BIN
        env.setdefault("TERM", "xterm")
        if parent_env:
            env.update({k: str(v) for k, v in parent_env.items()})
        # Redirect the probe's stdout into the verdict file in the workdir; force
        # a clean exit so safehouse+ returns straight to its menu.
        script = "{ %s ; } > %s 2>/dev/null; exit 0" % (body, RESULT_FILE)
        argv = [SAFEHOUSE_PLUS, "/bin/sh", "-c", script]
        term = _pty_run(argv, workdir, env, timeout)
        try:
            with open(os.path.join(workdir, RESULT_FILE)) as f:
                raw = f.read()
        except OSError:
            raw = ""
        tokens = [ln.strip() for ln in raw.splitlines() if ln.strip()]
        return {
            "tokens": tokens,
            "raw": raw,
            "term": term,
            "timed_out": "__HARNESS_TIMEOUT__" in term,
        }
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
