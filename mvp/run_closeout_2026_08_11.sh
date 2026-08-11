#!/bin/bash
# Closeout batch: the three things left open after the cross-family programme (F-AJ).
#   A/B  chat-format robustness on the two Qwen instruct models
#   C..G steering traction search + the confirmatory protect-blame test, cross-family
#
# Guard discipline (guidelines s13, all of it learned the hard way):
#   - swap baseline is read AFTER the model has loaded and settled, never before: reading it at
#     launch made the guard fire on the 10GB load itself
#   - the guard kills the PYTHON CHILD, not this wrapper; killing the wrapper twice left two
#     models resident and swap at 10.8GB
#   - every stage's exit status is recorded; COMPLETE is printed only if ALL of them passed, and
#     the script exits non-zero otherwise. A driver once printed "COMPLETE" after a stale swap
#     reading killed five stages in one second.
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs
mkdir -p "$LOG"
FAILED=()
PASSED=()

swap_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }   # free MB
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }

run_stage () {
  local name="$1"; shift
  echo "=== [$name] $(date +%H:%M:%S) ==="
  if [ "$(disk_gb)" -lt 5 ]; then
    echo "[$name] SKIP: only $(disk_gb)GB disk free"; FAILED+=("$name:disk"); return 1
  fi
  .venv/bin/python "$@" > "$LOG/${name}.log" 2>&1 &
  local pid=$!
  # settle: let the weights load and the allocator reach steady state before the guard reads swap
  sleep 60
  local base; base=$(swap_mb)
  echo "[$name] pid $pid, swap free after load: ${base}MB"
  while kill -0 "$pid" 2>/dev/null; do
    local free; free=$(swap_mb)
    if [ "$free" -lt 300 ]; then
      echo "[$name] GUARD: swap free ${free}MB -> killing python child $pid"
      kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
      FAILED+=("$name:swap"); return 1
    fi
    if [ "$(disk_gb)" -lt 3 ]; then
      echo "[$name] GUARD: disk $(disk_gb)GB -> killing python child $pid"
      kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null
      FAILED+=("$name:disk"); return 1
    fi
    sleep 20
  done
  wait "$pid"; local rc=$?
  if [ $rc -ne 0 ]; then
    echo "[$name] FAILED rc=$rc"; tail -5 "$LOG/${name}.log"; FAILED+=("$name:rc$rc"); return 1
  fi
  echo "[$name] ok"; PASSED+=("$name"); return 0
}

# The MPS caching allocator does not return freed blocks, so a process doing thousands of forwards
# creeps into swap until the guard kills it. The search resumes from its own JSON, so run it in
# chunks of a few configs in a FRESH process each time and stop when it prints [done].
run_search () {
  local name="$1" model="$2" tag="$3"
  for round in 1 2 3 4 5 6; do
    run_stage "${name}_r${round}" mindedness_steer_search.py \
        --model "$model" --tag "$tag" --max-cells 5 || return 1
    if grep -q "^\[done\]" "$LOG/${name}_r${round}.log"; then
      echo "[$name] search finished in $round round(s)"; return 0
    fi
  done
  echo "[$name] did not finish within 6 rounds"; FAILED+=("$name:rounds"); return 1
}

# ---- A/B: is chat format usable on the Qwen instruct models at all? -------------------------
# Both defaulted to RAW because no gate file existed for them, so raw was never actually chosen.
# Writes to a *-chatcheck tag on purpose: a real gate file at the plain tag would silently change
# the format for every future run of every other script and break comparability with the sweeps
# already on disk.
run_stage gate_qwen3_chatcheck   mindedness_base_gate.py --model Qwen/Qwen3-4B   --tag Qwen3-4B-chatcheck
run_stage gate_qwen35_chatcheck  mindedness_base_gate.py --model Qwen/Qwen3.5-4B --tag Qwen3_5-4B-chatcheck

# ---- C/D: OLMo (already downloading in another shell) ---------------------------------------
# Gate on the fetcher's own COMPLETE line, NOT on the weight file existing: curl writes
# model.safetensors progressively, so -f is true from the first byte and would hand a truncated
# 240MB-of-2832MB checkpoint to the loader.
echo "=== [wait_olmo] $(date +%H:%M:%S) waiting for the fetch to report COMPLETE ==="
for _ in $(seq 1 240); do
  grep -q "COMPLETE ->" "$LOG/fetch_olmo.log" 2>/dev/null && break
  grep -q "FAILED " "$LOG/fetch_olmo.log" 2>/dev/null && break
  sleep 15
done
if grep -q "COMPLETE ->" "$LOG/fetch_olmo.log" 2>/dev/null; then
  run_search steersearch_olmo models/OLMo-2-0425-1B-Instruct OLMo2-1B-Instruct
  run_stage moral_olmo mindedness_moral_run.py \
      --model models/OLMo-2-0425-1B-Instruct --tag OLMo2-1B-Instruct
else
  echo "[olmo] fetch never reported COMPLETE, skipping C/D"; FAILED+=("olmo:nofetch")
fi

# ---- E/F/G: Gemma ---------------------------------------------------------------------------
echo "=== [fetch_gemma] $(date +%H:%M:%S) ==="
./fetch_model.sh google/gemma-4-E2B-it models/gemma-4-E2B-it > "$LOG/fetch_gemma.log" 2>&1 \
  || { echo "[fetch_gemma] FAILED"; FAILED+=("fetch_gemma"); }
if grep -q "COMPLETE ->" "$LOG/fetch_gemma.log" 2>/dev/null; then
  run_search steersearch_gemma models/gemma-4-E2B-it Gemma4-E2B-Instruct
  run_stage moral_gemma mindedness_moral_run.py \
      --model models/gemma-4-E2B-it --tag Gemma4-E2B-Instruct
else
  echo "[gemma] fetch never reported COMPLETE, skipping F/G"; FAILED+=("gemma:noweights")
fi

echo
echo "================ CLOSEOUT SUMMARY $(date +%H:%M:%S) ================"
echo "passed (${#PASSED[@]}): ${PASSED[*]:-none}"
echo "failed (${#FAILED[@]}): ${FAILED[*]:-none}"
if [ ${#FAILED[@]} -eq 0 ]; then
  echo "COMPLETE — all ${#PASSED[@]} stages succeeded"
  exit 0
fi
echo "INCOMPLETE — ${#FAILED[@]} stage(s) failed; nothing here should be read as a null result"
exit 1
