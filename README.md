# safehouse+

`safehouse+` is a small terminal UI wrapper around [`safehouse`](https://agent-safehouse.dev) for iterating on sandbox settings without remembering command-line flags.

It does **not** modify `safehouse`; it builds and runs `safehouse` commands for you.

## Usage

Run a command immediately:

```bash
safehouse+ pi
```

Open the menu first:

```bash
safehouse+ --menu pi
```

Open the menu with the last saved command/settings:

```bash
safehouse+
```

Settings are saved per-folder in:

```text
.safehouse-plus.json
```

## What you can change

From the menu you can:

- run/restart the current command
- edit the command before restarting
- toggle Safehouse optional features
- toggle network access
- edit path rules in one list (`ro`, `rw`, `deny`, or off)
- set the Safehouse workdir
- toggle full environment passthrough
- pass selected environment variables
- view the generated `safehouse` command
- view `safehouse --explain`

## Resume commands

If a tool prints a resume hint like:

```text
To resume this session: pi --session ...
```

`safehouse+` detects it for the current run and adds a temporary menu item:

```text
Resume detected session: ...
```

Press `r` to resume quickly. Resume commands are **not** saved to disk.

## Keys

Main/menu navigation:

- `Ctrl-n` / Down / `j` — move down
- `Ctrl-p` / Up / `k` — move up
- `Enter` — select
- `q` or `Ctrl-c` — save and quit from main menu
- `Ctrl-c` — return from submenus

Text input:

- `Ctrl-a` — start of line
- `Ctrl-e` — end of line
- `Ctrl-b` / `Ctrl-f` — back/forward one character
- `Alt-b` / `Alt-f` or `Esc b` / `Esc f` — back/forward one word
- `Ctrl-w` — delete previous word
- `Ctrl-k` — delete to end
- `Ctrl-u` — delete before cursor
- `Esc` — cancel input

## Notes

Because macOS sandbox profiles are applied when a process starts, changing settings requires restarting the sandboxed program. `safehouse+` is designed to make that restart loop fast.
