#!/bin/bash
cd /Users/sumit/Github/Phronesis; WS=mvp/results/workspace
for i in $(seq 1 480); do
  [ -f "$WS/E21_DONE" ] && exit 0
  if [ -f "$WS/E20_DONE" ] || ! pgrep -qf e20_correctness; then break; fi
  sleep 30
done
mvp/.venv/bin/python mvp/e21_truthfulqa_probe.py >> /tmp/e21.log 2>&1
