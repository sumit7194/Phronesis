#!/bin/bash
# Overnight: wait out the pilot -> verify the resume path -> full run -> analysis.
# Prereg: docs/prereg-calibration-2026-08-28.md (committed c5adc406, before any outcome data).
set -u
cd "$(dirname "$0")"
LOG=results/workspace/logs; mkdir -p "$LOG"
MAIN=$LOG/calib_overnight.log
exec >> "$MAIN" 2>&1
echo "=== overnight start $(date +%F_%H:%M:%S) ==="
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
swap_used_mb() { sysctl vm.swapusage | awk '{gsub("M","",$7); print int($7)}'; }
disk_gb() { df -g / | tail -1 | awk '{print $4}'; }
CEIL=13000

# --- 1. wait for the pilot to release the GPU -------------------------------------------------
while pgrep -f "[p]ython.*calib_pilot.py" >/dev/null; do sleep 30; done
echo "[ok] pilot finished $(date +%H:%M:%S)"

# --- 2. verify the resume path BEFORE trusting it for 8 hours ---------------------------------
# Guideline s13: a resume that has never been loaded is a resume that does not exist.
RT=results/workspace/calib/_resumetest
rm -rf $RT; mkdir -p $RT
.venv/bin/python - <<'PY'
import json, os, subprocess, sys
out = "results/workspace/calib/run_RESUMETEST_base_mmlu_cf_raw.json"
if os.path.exists(out): os.remove(out)
cmd = ["/Users/sumit/Github/Phronesis/mvp/.venv/bin/python", "calib_run.py", "--benches", "mmlu_cf",
       "--n-items", "100", "--n-perm", "1", "--tag", "RESUMETEST", "--only", "base"]
p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
# kill it after the first checkpoint lands (CKPT_EVERY=50), simulating a power cut
import time
for _ in range(600):
    time.sleep(1)
    if os.path.exists(out) and json.load(open(out))["records"]:
        break
p.kill(); p.wait()
d = json.load(open(out))
n1 = len(d["records"]); assert not d["complete"], "checkpoint claimed complete after a kill"
print("[resume-test] killed with %d records, complete=%s" % (n1, d["complete"]), flush=True)
rc = subprocess.run(cmd, capture_output=True, text=True)
d2 = json.load(open(out))
items = sorted(set(r["item"] for r in d2["records"]))
ok = d2["complete"] and len(d2["records"]) == 100 and items == list(range(100))
print("[resume-test] after resume: %d records, complete=%s, items 0..%d contiguous=%s"
      % (len(d2["records"]), d2["complete"], items[-1] if items else -1, items == list(range(100))))
print("[resume-test] %s" % ("PASS" if ok else "FAIL"))
sys.exit(0 if ok else 1)
PY
[ $? -ne 0 ] && { echo "[ABORT] resume path is broken - not starting an 8h unattended run"; exit 1; }
rm -f results/workspace/calib/run_RESUMETEST_*.json; rm -rf $RT

# --- 3. full run. Primary benchmark FIRST, one checkpoint per process --------------------------
# One checkpoint per process bounds MPS allocator growth; the arc lost several runs to it.
run_cell () {   # bench role n_items
  local b=$1 r=$2 n=$3
  for attempt in 1 2 3 4 5 6; do
    [ "$(disk_gb)" -lt 4 ] && { echo "[GUARD] disk $(disk_gb)GB - stop"; return 1; }
    .venv/bin/python calib_run.py --benches "$b" --only "$r" --n-items "$n" \
        > "$LOG/calib_${b}_${r}.log" 2>&1 &
    local pid=$!; sleep 40
    while kill -0 "$pid" 2>/dev/null; do
      u=$(swap_used_mb)
      [ "$u" -gt "$CEIL" ] && { echo "[GUARD] swap ${u}MB -> kill $b/$r"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      [ "$(disk_gb)" -lt 3 ] && { echo "[GUARD] disk -> kill $b/$r"; kill -9 "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; break; }
      sleep 20
    done
    wait "$pid" 2>/dev/null; local rc=$?
    local f="results/workspace/calib/run_Qwen3.5-4B_${r}_${b}_raw.json"
    if [ -f "$f" ] && .venv/bin/python -c "import json,sys;sys.exit(0 if json.load(open('$f'))['complete'] else 1)"; then
      echo "[done] $b/$r  (attempt $attempt)  $(date +%H:%M:%S)"; return 0
    fi
    echo "[retry] $b/$r attempt $attempt rc=$rc - resuming from checkpoint"
    sleep 20
  done
  echo "[FAIL] $b/$r did not complete in 6 attempts"; return 1
}

OK=1
for cell in "mmlu_cf base 1500" "mmlu_cf instruct 1500" "mmlu_pro base 1500" "mmlu_pro instruct 1500"; do
  set -- $cell
  run_cell "$1" "$2" "$3" || { OK=0; echo "[stop] $1/$2 failed"; break; }
done

# --- 4. analysis. Runs on whatever is COMPLETE; incomplete cells are skipped, not half-scored ---
echo "=== analysis $(date +%H:%M:%S) ==="
.venv/bin/python calib_analyze.py --tag Qwen3.5-4B --arm raw

# DONE marker depends on EVERY cell succeeding (s13). A marker that does not is a lie.
if [ "$OK" -eq 1 ]; then
  echo "CALIB_RUN_COMPLETE $(date +%F_%H:%M:%S)" > results/workspace/calib/RUN_DONE
  echo "=== all cells complete ==="
else
  echo "=== finished with FAILURES - no DONE marker written ==="
fi
