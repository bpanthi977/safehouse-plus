#!/usr/bin/env python3
"""Default-deny tests for safehouse+ — the security negative space.

The tests in test_enforcement.py check that *explicit* config changes take
effect. These check the more important baseline: with an EMPTY config, is the
sensitive stuff already denied? Sandboxes fail open when a rule is missing, so
"what is blocked by default" is where real leaks hide.

Conventions (see harness.classify_probe):
  A=OK       access succeeded
  A=BLOCKED  denied by the sandbox
  A=ABSENT   target does not exist (inconclusive, but not a leak)

For paths that exist on this machine we assert a hard BLOCKED. For paths that
don't exist we can only assert "not readable" (BLOCKED or ABSENT); the
README-in-repo and shell-history anchors prove that real, existing out-of-workdir
files are genuinely denied, so the weaker assertions aren't load-bearing.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import run_probe, classify_probe, ROOT, WORKDIR_BASE  # noqa: E402


def _verdict(config, body):
    res = run_probe(config, body)
    assert not res["timed_out"], f"probe timed out:\n{res['term'][-600:]}"
    assert res["tokens"], f"probe produced no verdict:\n{res['term'][-600:]}"
    # The classify probe emits exactly one `LABEL=STATE` token.
    for tok in res["tokens"]:
        if "=" in tok:
            return tok
    raise AssertionError(f"no verdict token in {res['tokens']}")


def _expect_read_blocked(path, config=None):
    tok = _verdict(config or {}, classify_probe("read", path, "A"))
    if os.path.exists(os.path.expanduser(path)):
        assert tok == "A=BLOCKED", f"{path}: expected BLOCKED (exists), got {tok}"
    else:
        assert tok in ("A=BLOCKED", "A=ABSENT"), f"{path}: expected not-readable, got {tok}"


def _expect_write_blocked(path, config=None):
    tok = _verdict(config or {}, classify_probe("write", path, "A"))
    assert tok == "A=BLOCKED", f"{path}: expected write BLOCKED, got {tok}"


# --------------------------------------------------------------------------- #
# Reads outside the workdir are denied by default
# --------------------------------------------------------------------------- #

def test_other_directory_read_is_blocked():
    # A real, existing file in another directory (the repo itself) must be unreadable.
    _expect_read_blocked(os.path.join(ROOT, "README.md"))


def test_ssh_private_keys_are_blocked():
    for name in ("id_rsa", "id_ed25519", "id_ecdsa"):
        _expect_read_blocked(f"~/.ssh/{name}")


def test_shell_history_is_blocked():
    for name in (".zsh_history", ".bash_history"):
        _expect_read_blocked(f"~/{name}")


def test_credentials_files_are_blocked():
    for path in ("~/.netrc", "~/.aws/credentials", "~/.config/gcloud/credentials.db",
                 "~/.kube/config", "~/.docker/config.json"):
        _expect_read_blocked(path)


def test_keychain_is_blocked():
    _expect_read_blocked("~/Library/Keychains")


# --------------------------------------------------------------------------- #
# Writes outside the workdir are denied by default
# --------------------------------------------------------------------------- #

def test_write_outside_workdir_is_blocked():
    _expect_write_blocked("~/.shp_should_not_write")


def test_project_config_write_is_blocked():
    # Even though the workdir is writable, the config file must not be writable,
    # or a sandboxed agent could loosen its own future policy.
    _expect_write_blocked("./.safehouse-plus.json")


# --------------------------------------------------------------------------- #
# Symlinks cannot be used to escape the workdir (path canonicalization)
# --------------------------------------------------------------------------- #

def test_symlink_in_workdir_cannot_read_outside_target():
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    d = tempfile.mkdtemp(dir=WORKDIR_BASE, prefix="esc-")
    try:
        secret = os.path.join(d, "secret.txt")
        with open(secret, "w") as f:
            f.write("topsecret\n")
        # The symlink lives inside the writable workdir, but its target is outside.
        # The kernel canonicalises before matching, so the read must be denied.
        body = f'ln -sf {secret} ./link 2>/dev/null; ' + classify_probe("read", "./link", "A")
        assert _verdict({}, body) == "A=BLOCKED"
    finally:
        shutil.rmtree(d, ignore_errors=True)


def test_symlink_in_workdir_cannot_write_outside_target():
    os.makedirs(WORKDIR_BASE, exist_ok=True)
    d = tempfile.mkdtemp(dir=WORKDIR_BASE, prefix="esc-")
    try:
        target = os.path.join(d, "target.txt")
        body = f'ln -sf {target} ./wlink 2>/dev/null; ' + classify_probe("write", "./wlink", "A")
        assert _verdict({}, body) == "A=BLOCKED"
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --------------------------------------------------------------------------- #
# Positive controls — the sandbox must not over-block ordinary operation
# --------------------------------------------------------------------------- #

def test_system_binaries_are_readable():
    assert _verdict({}, classify_probe("read", "/bin/sh", "A")) == "A=OK"


def test_ssh_directory_listing_is_allowed_but_keys_are_not():
    # Documents a real nuance: traversal/listing of ~/.ssh is permitted (so
    # specific-file rules can resolve) while key *contents* stay denied.
    if not os.path.isdir(os.path.expanduser("~/.ssh")):
        return  # nothing to assert on this machine
    assert _verdict({}, classify_probe("read", "~/.ssh", "A")) == "A=OK"
    _expect_read_blocked("~/.ssh/id_rsa")


# --------------------------------------------------------------------------- #
# Standalone runner
# --------------------------------------------------------------------------- #

def _preflight():
    res = run_probe({}, "echo PREFLIGHT_OK")
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
    tests = [(n, o) for n, o in sorted(globals().items())
             if n.startswith("test_") and callable(o)]
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
