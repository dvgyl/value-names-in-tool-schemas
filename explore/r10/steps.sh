#!/usr/bin/env bash
# Run one step (pilot or submit) of round-10 runs in order, each at its printed bound (standing approval of
# 2026-11-12, memory standing-approval-round10). r10/runs.py adds the lock, the protected-dialogue, the manifest and the
# budget-gate checks before the client runs. It never raises a cap or a limit.
# Usage (from explore/): bash r10/steps.sh <pilot|submit> <max bound per step in USD> <run name>...
# Stops at the first step whose printed bound is above the maximum or whose client exits with an error.
set -uo pipefail
cd "$(dirname "$0")/.."
step="$1"; max="$2"; shift 2
for name in "$@"; do
  out="$(.venv/bin/python -I "r10/$name.py" "$step" 2>&1)"
  bound="$(printf '%s\n' "$out" | sed -n 's/.*Rerun with --approve \([0-9.]*\) .*/\1/p' | tail -1)"
  if [ -z "$bound" ]; then printf '== %s %s: no bound printed\n%s\n' "$name" "$step" "$(printf '%s\n' "$out" | tail -4)"; exit 1; fi
  if awk -v b="$bound" -v m="$max" 'BEGIN{exit !(b>m)}'; then echo "== $name $step: bound $bound is above $max. Stopped."; exit 1; fi
  echo "== $name $step: bound $bound USD  $(date -u +%H:%M)"
  .venv/bin/python -I "r10/$name.py" "$step" --approve "$bound" 2>&1 | grep -v '^ \|^{\|^}' | tail -3
  [ "${PIPESTATUS[0]}" -eq 0 ] || { echo "failed: $name"; exit 1; }
done
echo "done $(date -u +%H:%M)"
