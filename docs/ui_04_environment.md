# UI design 04: Environment tab

## Environment tab, default sanitized mode

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
> [ ] Pass full environment
  [ ] Load trusted environment file (sourced by bash)

Extra env-pass variables
  [add] Add variable

Passed variables
  [pass] HOME      /Users/bpanthi977
  [pass] PATH      /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [pass] SHELL     /bin/zsh
  [pass] USER      bpanthi977
  [pass] LOGNAME   bpanthi977
  [pass] TMPDIR    /var/folders/...
  [pass] PWD       /Users/bpanthi977/Dev/safehouse-plus

────────────────────────────────────────────
Space toggle · Enter edit/add · D delete/reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Environment tab with env file enabled

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
  [ ] Pass full environment
> [x] Load trusted environment file (sourced by bash)
      .env

Extra env-pass variables
  [add] Add variable
  [pass] OPENAI_API_KEY     sk-proj-example-value

Passed variables
  [pass] HOME      /Users/bpanthi977
  [pass] PATH      /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [pass] SHELL     /bin/zsh
  [pass] USER      bpanthi977
  [pass] LOGNAME   bpanthi977
  [pass] TMPDIR    /var/folders/...
  [pass] PWD       /Users/bpanthi977/Dev/safehouse-plus
  [file] MY_ENV_VAR        value from .env
  [file] API_BASE_URL      https://example.test

────────────────────────────────────────────
Space toggle · Enter select file · D clear file · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Environment tab with extra env-pass variables

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
  [ ] Pass full environment
  [ ] Load trusted environment file (sourced by bash)

Extra env-pass variables
> [add] Add variable
  [pass] OPENAI_API_KEY     sk-proj-example-value
  [pass] ANTHROPIC_API_KEY  sk-ant-example-value
  [missing] GITHUB_TOKEN    not set in parent environment

Passed variables
  [pass] HOME      /Users/bpanthi977
  [pass] PATH      /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [pass] SHELL     /bin/zsh
  [pass] USER      bpanthi977
  [pass] LOGNAME   bpanthi977
  [pass] TMPDIR    /var/folders/...
  [pass] PWD       /Users/bpanthi977/Dev/safehouse-plus

────────────────────────────────────────────
Space toggle · Enter edit/add · D delete/reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Environment tab, full environment enabled

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
> [x] Pass full environment
  [ ] Load trusted environment file (sourced by bash)

Extra env-pass variables
  [info] Ignored while full environment is enabled

Passed variables
  [all] Full parent environment will be passed to the command

Preview
  [env] HOME              /Users/bpanthi977
  [env] PATH              /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [env] SHELL             /bin/zsh
  [env] USER              bpanthi977
  [env] OPENAI_API_KEY    sk-proj-example-value
  [env] GITHUB_TOKEN      ghp_example_value
  [env] ...               more variables not shown

────────────────────────────────────────────
Space toggle · Enter edit/add · D delete/reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Environment tab with extra variable selected

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
  [ ] Pass full environment
  [ ] Load trusted environment file (sourced by bash)

Extra env-pass variables
  [add] Add variable
> [pass] OPENAI_API_KEY     sk-proj-example-value
  [pass] ANTHROPIC_API_KEY  sk-ant-example-value

Passed variables
  [pass] HOME      /Users/bpanthi977
  [pass] PATH      /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [pass] SHELL     /bin/zsh
  [pass] USER      bpanthi977
  [pass] LOGNAME   bpanthi977
  [pass] TMPDIR    /var/folders/...
  [pass] PWD       /Users/bpanthi977/Dev/safehouse-plus

────────────────────────────────────────────
Enter edit · D delete · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Environment tab with passed variable selected

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Environment mode
  [ ] Pass full environment
  [ ] Load trusted environment file (sourced by bash)

Extra env-pass variables
  [add] Add variable
  [pass] OPENAI_API_KEY     sk-proj-example-value
  [pass] ANTHROPIC_API_KEY  sk-ant-example-value

Passed variables
> [pass] HOME      /Users/bpanthi977
  [pass] PATH      /opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:...
  [pass] SHELL     /bin/zsh
  [pass] USER      bpanthi977
  [pass] LOGNAME   bpanthi977
  [pass] TMPDIR    /var/folders/...
  [pass] PWD       /Users/bpanthi977/Dev/safehouse-plus

────────────────────────────────────────────
Read-only · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Editing behavior

For environment mode:

```text
Pass full environment:
  Space/Enter: toggle Pass full environment
  D: reset to default sanitized mode

Load trusted environment file (sourced by bash):
  Space: toggle env file loading on/off
  Enter: select/change env file path with path completion
  D: clear selected env file
```

For `[add] Add variable`:

```text
Enter: prompt for an environment variable name
Space: same as Enter
```

For extra env-pass variables:

```text
Enter: edit variable name
D: delete from env-pass list
```

Default sanitized variables are read-only on this screen. They are shown so the user knows what the command will receive.

When the cursor is on a read-only passed variable, the footer should not show editing/deletion actions. It should show read-only navigation help instead.

## Env file behavior

The env file option maps to safehouse's `--env=FILE`.

The UI label must say:

```text
Load trusted environment file (sourced by bash)
```

This makes it clear that the file is not merely dotenv syntax. It is trusted shell input sourced by bash, so normal shell assignments and shell code can run while preparing the environment.

Values loaded from the env file are shown in `Passed variables` with a `[file]` tag.

## Value display policy

Show all environment variable values directly for transparency.

There is no redaction logic. Simple behavior is preferred: the value displayed in the Environment tab is the value that will be available to the command, or `not set in parent environment` if the variable is missing.

## Design notes

- The tab clearly separates environment mode, user-added env-pass variables, and default passed variables.
- `Extra env-pass variables` is the second section so users can edit added variables without moving past the default passed variable list.
- Environment variable values are shown, not just names.
- `[ ] Pass full environment` defaults to off, meaning sanitized mode.
- `[ ] Load trusted environment file (sourced by bash)` lets the user select an env file to source with bash.
- `Extra env-pass variables` is where users add specific variables while staying in sanitized mode.
- Default passed variables are always passed in sanitized mode, so they do not need a `Changes from default` section.
- No `Changes from default` section is shown on this tab.
- If full environment is enabled, extra env-pass variables and env file settings remain saved but are ignored until full environment is disabled again.
- Do not show a `No extra variables` placeholder line; an empty `Extra env-pass variables` section should contain only `[add] Add variable`.
- Color may highlight missing variables, but textual tags must carry the meaning.
