#!/bin/bash
cd "$(dirname "$0")"
exec .venv/bin/python curvature_twin.py >> results/workspace/logs/curvature_twin.log 2>&1
