# UI design 02: Network tab

## Network tab, default settings

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Network controls
> [x] Allow network traffic
  [ ] Allow Docker socket access
      /var/run/docker.sock
      ~/.docker/run/docker.sock
  [ ] Allow Podman socket access
      /run/podman/podman.sock
      ~/.local/share/containers/podman/machine/podman.sock
  [ ] Allow SSH agent socket access
      SSH_AUTH_SOCK

────────────────────────────────────────────
Enter/Space toggle · ←/→ switch tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save · D discard
```

## Network tab, network disabled

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Network controls
> [ ] Allow network traffic
  [ ] Allow Docker socket access
      /var/run/docker.sock
      ~/.docker/run/docker.sock
  [ ] Allow Podman socket access
      /run/podman/podman.sock
      ~/.local/share/containers/podman/machine/podman.sock
  [ ] Allow SSH agent socket access
      SSH_AUTH_SOCK

Changes from default
  [change] + DENY network*

────────────────────────────────────────────
Enter/Space toggle · ←/→ switch tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save · D discard
```

## Network tab, socket overrides enabled

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Network controls
  [x] Allow network traffic
> [x] Allow Docker socket access
      /var/run/docker.sock
      ~/.docker/run/docker.sock
  [ ] Allow Podman socket access
      /run/podman/podman.sock
      ~/.local/share/containers/podman/machine/podman.sock
  [x] Allow SSH agent socket access
      SSH_AUTH_SOCK

Changes from default
  [change] + ALLOW Docker socket access
  [change] + ALLOW SSH agent socket access

────────────────────────────────────────────
Enter/Space toggle · ←/→ switch tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save · D discard
```

## Design notes

- The editable rows on this tab are:
  - `[x] / [ ] Allow network traffic`
  - `[x] / [ ] Allow Docker socket access`
  - `[x] / [ ] Allow Podman socket access`
  - `[x] / [ ] Allow SSH agent socket access`
- Since all visible permission rows are editable, there is no separate `Effective network permissions` section.
- The selected row defaults to `Allow network traffic` unless a recently changed row should retain focus.
- Docker, Podman, and SSH agent socket permissions are directly changeable from this tab.
- Socket rows default to unchecked because the sandbox default is to deny these sensitive sockets.
- Do not show a `Changes from default` section when there are no changes.
- Show `Changes from default` only when the user has changed something from the default policy, such as disabling all network or allowing a sensitive socket.
- The labels avoid backend-specific wording such as “safehouse profile”.
- Color may highlight allow/deny state, but the checkbox text must carry the meaning.
