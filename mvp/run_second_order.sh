#!/bin/bash
# Detached second-order probe (prereg-second-order.md). setsid so it survives Claude Code exit.
cd "$(dirname "$0")"
exec .venv/bin/python second_order_probe.py >> results/workspace/logs/second_order_v2.log 2>&1
