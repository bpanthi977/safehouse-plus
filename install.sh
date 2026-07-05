#!/usr/bin/env bash
# Installs safehouse+ into a local bin directory.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/bpanthi977/safehouse-plus/main/install.sh | bash
#
# Env overrides:
#   SAFEHOUSE_PLUS_REPO     org/repo to install from (default: bpanthi977/safehouse-plus)
#   SAFEHOUSE_PLUS_REF      branch/tag to install from (default: main)
#   SAFEHOUSE_PLUS_BIN_DIR  install directory (default: ~/.local/bin)

set -euo pipefail

REPO="${SAFEHOUSE_PLUS_REPO:-bpanthi977/safehouse-plus}"
REF="${SAFEHOUSE_PLUS_REF:-main}"
BIN_DIR="${SAFEHOUSE_PLUS_BIN_DIR:-$HOME/.local/bin}"
URL="https://raw.githubusercontent.com/${REPO}/${REF}/safehouse+"

# Update in place if safehouse+ is already on PATH somewhere, rather than
# assuming BIN_DIR and potentially creating a second, shadowed copy.
EXISTING="$(command -v safehouse+ 2>/dev/null || true)"
if [ -n "$EXISTING" ]; then
  echo "safehouse+ is already installed at $EXISTING"
  TARGET="$EXISTING"
else
  TARGET="$BIN_DIR/safehouse+"
  mkdir -p "$BIN_DIR"
fi

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

echo "Checking ${URL}..."
curl -fsSL "$URL" -o "$TMP"

if [ -f "$TARGET" ] && cmp -s "$TMP" "$TARGET"; then
  echo "safehouse+ is already up to date."
else
  if [ -f "$TARGET" ]; then
    echo "Updating safehouse+ at $TARGET..."
  else
    echo "Installing safehouse+ to $TARGET..."
  fi
  if ! cp "$TMP" "$TARGET" 2>/dev/null; then
    echo "Error: cannot write to $TARGET (try with sudo, or set SAFEHOUSE_PLUS_BIN_DIR)." >&2
    exit 1
  fi
  chmod +x "$TARGET"
  echo "Done."
fi

TARGET_DIR="$(dirname "$TARGET")"
case ":$PATH:" in
  *":$TARGET_DIR:"*) ;;
  *)
    echo
    echo "Note: $TARGET_DIR is not on your PATH."
    echo "Add it to your shell profile, e.g.:"
    echo "  export PATH=\"$TARGET_DIR:\$PATH\""
    ;;
esac

# This script is commonly run as `curl ... | bash`, which occupies stdin
# with the script body itself. Reattach to the terminal (if any) so the
# y/N prompt in --ensure-safehouse can actually be answered interactively.
echo
if { : < /dev/tty; } 2>/dev/null; then
  "$TARGET" --ensure-safehouse < /dev/tty || true
else
  echo "Skipping safehouse dependency check (no terminal attached)."
  echo "Run '$TARGET --ensure-safehouse' manually to install it."
fi

echo
echo "Done. Run 'safehouse+' to get started (after ensuring $TARGET_DIR is on your PATH)."
