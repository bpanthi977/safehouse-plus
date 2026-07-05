# safehouse+

`safehouse+` is a CLI program to run agents and other programs inside
a sandbox for macOS. It is small (few kBs in size), fast (half a
second) and configurable using TUI. You can configure access to
network, filesystem (rw, ro, none) and environment variables.

`safehouse+` builds upon [`safehouse`](https://agent-safehouse.dev)
and runs the command you give inside macOS's inbuilt sandboxing tool
(called `sandbox-exec`).


## Installation

```bash
curl -fsSL https://raw.githubusercontent.com/bpanthi977/safehouse-plus/main/install.sh | bash
```

This installs `safehouse+` to `~/.local/bin` (or updates it in place if already on your `PATH`).

## Usage

Run a command in the sandbox:

```bash
safehouse+ pi
safehouse+ claude
safehouse+ codex
```

Quitting the program opens the settings UI, then resumes the session
with your updated settings.

Open the UI before running:

```bash
safehouse+ --menu pi
```

Open the UI with the last saved command and settings:

```bash
safehouse+
```

Settings are saved per folder in `.safehouse-plus.json`.

## What you can configure

The UI is organized into tabs:

- **Run** — run/restart, edit the command, resume a detected session, save/discard, or export the generated policy.
- **Network** — allow/deny network traffic and sensitive sockets such as Docker, Podman, and SSH agent sockets.
- **Paths** — add custom `ro`, `rw`, or `deny` path rules and override default path groups.
- **Environment** — use the default sanitized environment, pass selected variables, pass the full environment, or load a trusted env file sourced by bash.
- **Features** — enable optional safehouse integrations such as Docker, SSH, VS Code, cloud credentials, browsers, GUI access, and broad presets.

Because sandbox profiles are applied when a process starts, changing settings requires restarting the command. `safehouse+` is designed to make that loop fast.
