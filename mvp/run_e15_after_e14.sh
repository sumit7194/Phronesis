#!/bin/bash
cd /Users/sumit/Github/Phronesis
WS=mvp/results/workspace
# wait up to 3h for E14 to finish (poll); proceed anyway if it dies
for i in $(seq 1 180); do
  [ -f "$WS/E15_DONE" ] && exit 0
  if [ -f "$WS/E14_DONE" ] || ! pgrep -qf e14_alpha_atlas; then break; fi
  sleep 60
done
mvp/.venv/bin/python mvp/e15_caa_sycophancy.py >> /tmp/e15.log 2>&1
