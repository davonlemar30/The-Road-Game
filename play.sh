#!/bin/bash
# The Road — quick dev launcher
# Usage: ./play.sh
#        bash play.sh
# Run from anywhere in the repo tree.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/the-road"
python3 main.py
