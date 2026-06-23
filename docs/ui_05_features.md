# UI design 05: Features tab

## Features tab, default settings

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Developer tools
> [ ] Shell startup files
  [ ] Process control
  [ ] LLDB
  [ ] Xcode
  [ ] VS Code

Cloud / credentials
  [ ] Cloud credentials
  [ ] Cloud storage
  [ ] 1Password
  [ ] Keychain

Desktop / browser
  [ ] macOS GUI
  [ ] Clipboard
  [ ] Microphone
  [ ] Chromium headless
  [ ] Chromium full
  [ ] Electron
  [ ] Playwright Chrome
  [ ] Agent browser
  [ ] Browser native messaging
  [ ] CleanShot

Containers / remote
  [ ] Docker
  [ ] Kubernetes
  [ ] SSH

Broad presets
  [ ] All agent profiles
  [ ] All app profiles
  [ ] Wide read access

────────────────────────────────────────────
Space/Enter toggle · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Features tab with selected features

```text
safehouse+

 Run  |  Network  |  Paths  |  Environment  |  Features
────────────────────────────────────────────

Developer tools
  [x] Shell startup files
  [ ] Process control
  [ ] LLDB
  [ ] Xcode
  [x] VS Code

Cloud / credentials
  [x] Cloud credentials
  [ ] Cloud storage
  [ ] 1Password
  [ ] Keychain

Desktop / browser
  [ ] macOS GUI
  [ ] Clipboard
  [ ] Microphone
  [ ] Chromium headless
  [ ] Chromium full
  [ ] Electron
  [ ] Playwright Chrome
  [ ] Agent browser
  [ ] Browser native messaging
  [ ] CleanShot

Containers / remote
> [x] Docker
  [ ] Kubernetes
  [x] SSH

Broad presets
  [ ] All agent profiles
  [ ] All app profiles
  [ ] Wide read access

Changes from default
  [change] + ENABLE shell-init
  [change] + ENABLE vscode
  [change] + ENABLE cloud-credentials
  [change] + ENABLE docker
  [change] + ENABLE ssh

────────────────────────────────────────────
Space/Enter toggle · ←/→ tabs · Ctrl-p/Ctrl-n move · q/Ctrl-C save
```

## Feature mapping

The Features tab maps to safehouse's `--enable=FEATURES` option.

```text
Shell startup files        shell-init
Process control            process-control
LLDB                       lldb
Xcode                      xcode
VS Code                    vscode

Cloud credentials          cloud-credentials
Cloud storage              cloud-storage
1Password                  1password
Keychain                   keychain

macOS GUI                  macos-gui
Clipboard                  clipboard
Microphone                 microphone
Chromium headless          chromium-headless
Chromium full              chromium-full
Electron                   electron
Playwright Chrome          playwright-chrome
Agent browser              agent-browser
Browser native messaging   browser-native-messaging
CleanShot                  cleanshot

Docker                     docker
Kubernetes                 kubectl
SSH                        ssh

All agent profiles         all-agents
All app profiles           all-apps
Wide read access           wide-read
```

## Relationship to Network tab

Some feature toggles overlap with Network tab concepts.

In particular:

- `Docker` appears in Features and Docker socket access appears in Network.
- `SSH` appears in Features and SSH agent socket access appears in Network.

This duplication is intentional:

- The Network tab exposes direct socket/network permissions.
- The Features tab exposes higher-level safehouse optional integrations.

The UI should not try to hide one just because the other exists. If needed, rows can include short explanatory text later.

## Dependency notes

Some safehouse features imply or require other features internally. The UI can keep simple checkboxes and let safehouse resolve dependencies.

Important examples from safehouse help:

```text
electron implies macos-gui
chromium-full implies chromium-headless
playwright-chrome implies chromium-full and chromium-headless
agent-browser implies chromium-full and chromium-headless
lldb implies process-control
xcode enables Xcode developer roots plus scoped build/simulator state
wide-read grants read-only visibility across / and should be used cautiously
```

Future UI improvement: show implied features as read-only hints under the selected feature, but do not add that complexity initially.

## Design notes

- Features are grouped so the list is scannable.
- Rows are simple checkboxes.
- Do not expose update commands in this tab.
- Do not expose raw append-profile settings in this tab.
- Do not show a `Changes from default` section when no features are enabled.
- Show `Changes from default` only when one or more features are enabled.
- Color may highlight enabled or risky features, but checkbox text must carry the meaning.
