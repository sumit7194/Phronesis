#!/bin/bash
cd "$(dirname "$0")"
exec .venv/bin/python workspace_curvature_scan.py >> results/workspace/logs/curvature_scan.log 2>&1
