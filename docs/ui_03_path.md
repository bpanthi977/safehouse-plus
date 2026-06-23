# UI design 03: Paths tab

## Note: home ancestors are metadata-only

Home ancestor paths are not the same as normal read-only paths.

For example, `/Users` and `/Users/bpanthi977` may need to be visible enough for path traversal and metadata checks, but they should not imply normal read access to directory contents. In the UI, these should be shown as `[meta]`, not `[ro]`.

## Paths tab, default settings

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

User path rules
> [add] Add path rule
  [info] No custom path rules

Default writable paths
  [rw] Workdir
       /Users/bpanthi977/Dev/safehouse-plus
  [rw] Temp directories
  [rw] Developer caches

Default read-only paths
  [ro] System runtime
  [ro] Git config

Default metadata-only paths
  [meta] Home ancestors

Default denied paths
  [deny] Project sandbox config
         /Users/bpanthi977/Dev/safehouse-plus/.safehouse-plus.json
  [deny] Sensitive sockets and private system paths
         Managed by Network and sandbox defaults

────────────────────────────────────────────
Space cycle · Enter expand/edit · D delete/reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Paths tab with custom path rules

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

User path rules
> [add] Add path rule
  [rw] ~/project-data
  [ro] ~/.config/tool
  [deny] ~/.ssh
  [off] ~/old-test-path

Default writable paths
  [rw] Workdir
       /Users/bpanthi977/Dev/safehouse-plus
  [rw] Temp directories
  [rw] Developer caches

Default read-only paths
  [ro] System runtime
  [ro] Git config

Default metadata-only paths
  [meta] Home ancestors

Changes from default
  [change] + RW ~/project-data
  [change] + RO ~/.config/tool
  [change] + DENY ~/.ssh

────────────────────────────────────────────
Space cycle · Enter expand/edit · D delete/reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Paths tab with writable categories expanded

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

User path rules
  [add] Add path rule
  [info] No custom path rules

Default writable paths
  [rw] Workdir
       /Users/bpanthi977/Dev/safehouse-plus
> [rw] Temp directories
    [rw] /tmp
    [rw] /var/folders/...
  [rw] Developer caches
    [rw] ~/.cache
    [rw] ~/.npm
    [rw] ~/.cargo
    [rw] ~/.rustup
    [rw] ~/.local/share/pnpm
    [rw] ~/.pi

Default read-only paths
  [ro] System runtime
  [ro] Git config

Default metadata-only paths
  [meta] Home ancestors

────────────────────────────────────────────
Space cycle · Enter expand/collapse · D reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Paths tab with read-only and metadata categories expanded

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

User path rules
  [add] Add path rule
  [info] No custom path rules

Default writable paths
  [rw] Workdir
       /Users/bpanthi977/Dev/safehouse-plus
  [rw] Temp directories
  [rw] Developer caches

Default read-only paths
> [ro] System runtime
    [ro] /bin
    [ro] /sbin
    [ro] /usr
    [ro] /System
    [ro] /Library
    [ro] /opt
  [ro] Git config
    [ro] ~/.gitconfig
    [ro] ~/.config/git

Default metadata-only paths
  [meta] Home ancestors
    [meta] /Users
    [meta] /Users/bpanthi977

────────────────────────────────────────────
Space cycle · Enter expand/collapse · D reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Paths tab with default path overrides

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

User path rules
  [add] Add path rule
  [info] No custom path rules

Default writable paths
  [rw] Workdir
       /Users/bpanthi977/Dev/safehouse-plus
  [rw] Temp directories
    [rw] /tmp
>   [deny] /var/folders/...
  [rw] Developer caches

Default read-only paths
  [ro] System runtime
    [ro] /bin
    [ro] /sbin
    [ro] /usr
    [ro] /System
    [ro] /Library
    [deny] /opt
  [ro] Git config

Default metadata-only paths
  [meta] Home ancestors

Changes from default
  [change] /var/folders/...: RW → DENY
  [change] /opt: RO → DENY

────────────────────────────────────────────
Space cycle · Enter expand/collapse · D reset · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Editing behavior

There is no separate action prompt for changing access. Path rows are changed directly from the list.

For user path rules:

```text
Space/Enter: ro → rw → deny → off → ro
D: delete rule
```

For default individual path rows:

```text
Space: default → ro → rw → deny → off → default
Enter: same as Space for non-category rows
D: reset to default
```

For default category rows such as `Temp directories`, `Developer caches`, `System runtime`, `Git config`, and `Home ancestors`:

```text
Space: cycle access for the whole category
Enter: expand/collapse category
D: reset all paths in the category to default
```

Default rows should keep showing their current effective state in the tag:

```text
[rw]   default or override read/write
[ro]   default or override read-only
[deny] override deny
[off]  override off/not applied
[meta] default metadata-only
```

When a default row is overridden, it appears in `Changes from default`. Pressing `D` on that row removes the override and restores the default state.

When a user rule reaches `[off]`, it stays visible in `User path rules`. It is removed only by pressing `D`.

## Category behavior

- Categories are expandable/collapsible.
- Expanded category contents are indented under the category row.
- Categories are used when a group contains multiple related paths.
- Enter on a category expands/collapses it; Enter does not change its access mode.
- Space on a category cycles access for the whole category.
- Writable categories include:
  - `Temp directories`
  - `Developer caches`
- Read-only categories include:
  - `System runtime`
  - `Git config`
- Metadata-only categories include:
  - `Home ancestors`
- Individual paths inside expanded categories are editable.
- Pressing `D` on an individual default path resets that path to default.
- Pressing `D` on a category resets all overrides inside that category to default.

## Design notes

- The old `Path controls` section is removed.
- `Workdir` is shown inside `Default writable paths`.
- The project sandbox config file, `<workdir>/.safehouse-plus.json`, is denied by default even though the workdir is writable. This prevents the sandboxed command from modifying future sandbox settings.
- `[add] Add path rule` belongs inside `User path rules`.
- `[add] Add path rule` opens a path input with Tab completion.
- No repeated `Press Enter to expand` helper text is shown on category rows; the footer explains the controls.
- Default writable, read-only, and metadata-only paths are grouped into expandable categories when useful.
- Individual default paths can be changed directly when their category is expanded.
- Do not show a `Changes from default` section when there are no changes.
- Show `Changes from default` only when custom rules or overrides exist.
- Color may highlight rw/ro/deny/meta states, but the textual tags must carry the meaning.
