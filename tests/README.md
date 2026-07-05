# safehouse+ behavioral tests

These tests verify that the policy written in `.safehouse-plus.json` is **actually
enforced by the sandbox** — not merely that safehouse+ generates the right text.
Each test writes a config, runs a probe command through the real `safehouse+`
binary, and asserts what the *sandboxed* probe could observe.

They are **black box**: nothing imports safehouse+ internals, so changing the
implementation does not require changing the tests. The contract under test is
the `.safehouse-plus.json` schema and "does the resulting sandbox enforce it".

There are two suites:

- `test_enforcement.py` — does an **explicit** config change take effect?
- `test_default_deny.py` — with an **empty** config, is the sensitive stuff
  already blocked? (the security negative space — where leaks actually hide)

## Running

```bash
python3 tests/test_enforcement.py     # standalone runner, prints PASS/FAIL
python3 tests/test_default_deny.py
pytest tests/                          # both suites, if pytest is installed
```

Requirements:

- **macOS** with a working `sandbox-exec` (safehouse uses it).
- Must run **outside** any sandbox — you cannot nest `sandbox-exec`. (A preflight
  check aborts with a clear message if a sandboxed probe can't run.)
- `SAFEHOUSE_BIN` env var overrides which `safehouse` binary is used (defaults to
  `./safehouse` in the repo root).

Test workdirs are created under `~/.safehouse-plus-tests/` and removed after each
run. That location is deliberately outside `/tmp` and `/var/folders`, so a test
that restricts those paths can't clobber the harness's own result file.

## How a probe reports its verdict

`safehouse+`'s UI is curses, so the harness drives it through a PTY: it launches
`safehouse+ /bin/sh -c '<probe>'`, which runs the probe in the sandbox on first
launch, then waits at the menu. The probe's stdout is redirected to a file in the
(writable) workdir; once the menu header appears the harness sends `q` to quit and
reads that file. See `harness.py` for details.

## Behavioral checklist

### Implemented

| # | Spec under test | Expectation |
|---|---|---|
| 1 | default | outbound network allowed |
| 2 | `network: false` | network syscalls blocked (EPERM) |
| 3 | default | workdir is writable |
| 4 | default | `<workdir>/.safehouse-plus.json` is denied (config self-protection) |
| 5 | `deny_paths: ["/etc/hosts"]` | a normally-readable file becomes unreadable (also exercises symlink canonicalization) |
| 6 | `Temp directories → ro` | writes to `/tmp` are blocked, reads still work — **regression test for the `/tmp` canonicalization bug** |
| 7 | default (sanitized) | an unlisted secret env var is stripped |
| 8 | default (sanitized) | default vars (`HOME`, `PATH`) are passed |
| 9 | `env_pass: ["SECRET_TOKEN"]` | the named var is forwarded |
| 10 | `env_mode: "full"` | the secret var is forwarded |
| 11 | `env_file` + `env_file_enabled` | variables from the trusted env file are present |
| 12 | `enabled: ["wide-read"]` | a default-denied HOME file becomes readable |

Most tests assert a **baseline and the restricted case** (e.g. /etc/hosts is
readable by default, then blocked once denied) so a pass means the control caused
the change, not that the probe was broken.

### Default-deny (`test_default_deny.py`) — empty config

| Spec under test | Expectation |
|---|---|
| read a file in another directory (the repo README) | blocked |
| read `~/.ssh/id_rsa` (and other private keys) | blocked |
| read `~/.zsh_history`, `~/.bash_history` | blocked |
| read `~/.netrc`, `~/.aws/credentials`, `~/.kube/config`, … | blocked |
| read `~/Library/Keychains` | blocked |
| write anywhere outside the workdir (`~/...`) | blocked |
| write `<workdir>/.safehouse-plus.json` | blocked |
| read via a workdir symlink whose target is outside | blocked (no symlink escape) |
| write via a workdir symlink whose target is outside | blocked (no symlink escape) |
| read `/bin/sh` (control) | allowed — must not over-block |
| list `~/.ssh` while key contents stay denied | listing allowed, keys blocked |

Tests are **existence-aware**: a file that exists on the machine must be hard
`BLOCKED`; a path that doesn't exist may be `BLOCKED` or `ABSENT` (absence isn't a
leak). The repo README and shell-history anchors always exist, so they prove real
out-of-workdir denial; the symlink-escape tests prove the kernel canonicalizes
paths so the writable workdir can't be used as a springboard.

### Not yet implemented (need a runtime prerequisite or external state)

These are valid behavioral checks but depend on something not guaranteed on a
given machine; they are documented here rather than silently skipped:

- **Docker / Podman socket access** (Network tab) — needs a live socket at
  `/var/run/docker.sock` etc. to connect to. The *allow* rule is exercised
  indirectly: the canonicalization the socket grant relies on is the same code
  path proven by tests 5 and 6.
- **SSH agent socket access** (Network tab) — needs `SSH_AUTH_SOCK` set and an
  agent running, plus the var passed into the sandbox.
- **ro user-rule on a writable path / rw user-rule** — the ro→deny-write
  mechanism is covered by test 6; an explicit user-rule variant could be added.
- **Per-feature integrations** (`docker`, `ssh`, `vscode`, `keychain`, browsers,
  …) — each grants integration-specific access that's hard to observe without the
  corresponding tool installed/running. `wide-read` (test 12) is the
  representative feature with a cleanly observable effect.

### Out of scope

- **UI / curses interaction** (key handling, tab navigation, redraw, resume
  detection) — not behavioral sandbox enforcement; would need a separate
  PTY-scripting / unit-test layer.
