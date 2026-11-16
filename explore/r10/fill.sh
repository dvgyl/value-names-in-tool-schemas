#!/usr/bin/env bash
# The fill rule (PROTOCOL.md amendment R10-4): submit the named fill runs in order, each at its printed bound. A run whose
# bound does not fit the account's free money minus the reserve (r10/runs.py budget check) is skipped, and the next one is
# tried. Each decision gets one row in r10/fill_log.tsv (time, run, decision).
# Usage (from explore/): bash r10/fill.sh <max bound per step in USD> <run name>...
set -uo pipefail
cd "$(dirname "$0")/.."
max="$1"; shift
log="r10/fill_log.tsv"
[ -e "$log" ] || printf 'utc\trun\tdecision\n' > "$log"
for name in "$@"; do
  if [ -e "$name/batch.json" ]; then printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$name" "already submitted" >> "$log"; continue; fi
  if out="$(bash r10/steps.sh submit "$max" "$name" 2>&1)"; then
    printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$name" "submitted: $(printf '%s\n' "$out" | grep -o 'bound [0-9.]* USD' | head -1)" >> "$log"
  else
    printf '%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$name" "skipped: $(printf '%s\n' "$out" | grep -v '^ *$' | tail -1 | cut -c1-200)" >> "$log"
  fi
  printf '%s\n' "$out" | grep "bound\|submitted\|Not run" | cut -c1-160
done
