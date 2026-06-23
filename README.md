# safehouse+

`safehouse+` is a terminal UI for running commands through [`safehouse`](https://agent-safehouse.dev). It helps you tune sandbox permissions, restart quickly, and see/export the generated `safehouse` policy without memorizing flags.

It does not modify `safehouse`; it builds and runs `safehouse` commands for you.

## Usage

Run a command in the sandbox:

```bash
safehouse+ pi
```

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
