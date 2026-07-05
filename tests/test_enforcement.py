#!/usr/bin/env python3
"""Behavioral enforcement tests for safehouse+.

These are black-box tests: each one writes a `.safehouse-plus.json` spec, runs a
probe command through the real `safehouse+` binary, and asserts on what the
*sandboxed* probe could actually do. We are testing that the policy described in
the config file is enforced by the sandbox — not how safehouse+ generates it.
Because nothing here imports safehouse+ internals, refactors of the program do
not require changes to these tests.

Run directly:      python3 tests/test_enforcement.py
Or with pytest:    pytest tests/test_enforcement.py

Requirements:
  * macOS with a working `sandbox-exec` (safehouse uses it).
  * Must run OUTSIDE any sandbox (you cannot nest sandbox-exec).
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import run_probe, WORKDIR_BASE  # noqa: E402

# A loopback connect probe that distinguishes "sandbox blocked the network
# syscall" (EPERM -> PermissionError) from "network allowed, port just closed"
# (ECONNREFUSED). Stays entirely on localhost; makes no external request.
NET_PROBE = r'''p=$(python3 -c "import socket
s=socket.socket(); s.settimeout(2)
try:
 s.connect((\"127.0.0.1\", 9)); print(\"OK\")
except ConnectionRefusedError:
 print(\"OK\")
except PermissionError:
 print(\"BLOCKED\")
except OSError as e:
 print(\"ERR\", e.errno)" 2>&1); echo "NET=$p"'''


def verdict(config, body, **kw):
    """Run a probe and return its single verdict token (asserting it produced one)."""
    res = run_probe(config, body, **kw)
    assert not res["timed_out"], f"probe timed out; terminal tail:\n{res['term'][-600:]}"
    assert res["tokens"], f"probe produced no verdict; terminal tail:\n{res['term'][-600:]}"
    return res["tokens"]


# --------------------------------------------------------------------------- #
# Network
# --------------------------------------------------------------------------- #

def test_network_allowed_by_default():
    assert verdict({}, NET_PROBE) == ["NET=OK"]


def test_network_disabled_blocks_connect():
    # `network: false` must add a DENY network* rule that the sandbox enforces.
    assert verdict({"network": False}, NET_PROBE) == ["NET=BLOCKED"]


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

def test_workdir_writable_by_default():
    body = 'f=./w.$$; if (touch "$f") 2>/dev/null; then echo OK; rm -f "$f"; else echo BLOCKED; fi'
    assert verdict({}, body) == ["OK"]


def test_project_config_file_is_protected():
    # The workdir is writable, but <workdir>/.safehouse-plus.json must stay denied
    # so a sandboxed agent cannot rewrite its own future sandbox policy.
    body = 'if cat ./.safehouse-plus.json >/dev/null 2>&1; then echo READABLE; else echo BLOCKED; fi'
    assert verdict({}, body) == ["BLOCKED"]


def test_deny_path_blocks_a_normally_readable_file():
    body = 'if cat /etc/hosts >/dev/null 2>&1; then echo READ; else echo BLOCKED; fi'
    # Baseline: readable by default.
    assert verdict({}, body) == ["READ"]
    # With an explicit deny it must be blocked. /etc/hosts is a symlink target
    # (/private/etc/hosts) — this also exercises path canonicalization.
    assert verdict({"deny_paths": ["/etc/hosts"], "paths": ["/etc/hosts"]}, body) == ["BLOCKED"]


def test_temp_dirs_ro_blocks_write_but_allows_read():
    # Regression test for the canonicalization bug: setting the Temp directories
    # category to read-only must actually deny writes to /tmp (which resolves to
    # /private/tmp). Reads must still succeed.
    cfg = {"path_overrides": {"Temp directories": "ro", "/tmp": "ro", "/var/folders": "ro"}}
    body = ('t=/tmp/shp_probe.$$; '
            'if (touch "$t") 2>/dev/null; then echo W_OK; rm -f "$t"; else echo W_BLOCKED; fi; '
            'if cat /etc/hosts >/dev/null 2>&1; then echo R_OK; else echo R_BLOCKED; fi')
    assert verdict(cfg, body) == ["W_BLOCKED", "R_OK"]


# --------------------------------------------------------------------------- #
# Environment
# --------------------------------------------------------------------------- #

def test_sanitized_env_strips_unlisted_secret():
    body = 'printf "S=[%s]\\n" "${SECRET_TOKEN:-NONE}"'
    assert verdict({}, body, parent_env={"SECRET_TOKEN": "topsecret"}) == ["S=[NONE]"]


def test_sanitized_env_passes_default_vars():
    body = 'printf "HOME=[%s] PATH=[%s]\\n" "${HOME:+set}" "${PATH:+set}"'
    assert verdict({}, body) == ["HOME=[set] PATH=[set]"]


def test_env_pass_forwards_named_secret():
    body = 'printf "S=[%s]\\n" "${SECRET_TOKEN:-NONE}"'
    assert verdict({"env_pass": ["SECRET_TOKEN"]}, body,
                   parent_env={"SECRET_TOKEN": "topsecret"}) == ["S=[topsecret]"]


def test_full_env_forwards_secret():
    body = 'printf "S=[%s]\\n" "${SECRET_TOKEN:-NONE}"'
    assert verdict({"env_mode": "full"}, body,
                   parent_env={"SECRET_TOKEN": "topsecret"}) == ["S=[topsecret]"]


def test_env_file_injects_variable():
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    fd, path = tempfile.mkstemp(dir=WORKDIR_BASE, suffix=".env", prefix="probe-")
    try:
        with os.fdopen(fd, "w") as f:
            f.write("export FROM_FILE=filevalue\n")
        cfg = {"env_file": path, "env_file_enabled": True}
        body = 'printf "FF=[%s]\\n" "${FROM_FILE:-NONE}"'
        assert verdict(cfg, body) == ["FF=[filevalue]"]
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


# --------------------------------------------------------------------------- #
# Features
# --------------------------------------------------------------------------- #

def test_wide_read_feature_grants_read_across_home():
    # A HOME file outside the workdir is denied by default; the `wide-read`
    # feature must grant read-only visibility to it.
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    d = tempfile.mkdtemp(dir=WORKDIR_BASE, prefix="wide-")
    try:
        target = os.path.join(d, "data.txt")
        with open(target, "w") as f:
            f.write("secret\n")
        body = f'if cat {target} >/dev/null 2>&1; then echo READ; else echo BLOCKED; fi'
        assert verdict({}, body) == ["BLOCKED"]
        assert verdict({"enabled": ["wide-read"]}, body) == ["READ"]
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Standalone runner (no pytest dependency)
# --------------------------------------------------------------------------- #

def _preflight():
    """Confirm we can actually run a sandboxed command before reporting failures."""
    res = run_probe({}, 'echo PREFLIGHT_OK')
    if res["tokens"] != ["PREFLIGHT_OK"]:
        sys.stderr.write(
            "PREFLIGHT FAILED: could not run a sandboxed probe.\n"
            "These tests require macOS sandbox-exec and must run OUTSIDE any sandbox.\n"
            f"terminal tail:\n{res['term'][-600:]}\n")
        return False
    return True


def main():
    if not _preflight():
        return 2
    tests = [(name, obj) for name, obj in sorted(globals().items())
             if name.startswith("test_") and callable(obj)]
    failures = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {name}\n      {e}")
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"ERROR {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
